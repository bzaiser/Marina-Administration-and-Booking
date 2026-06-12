import os
from decimal import Decimal
from django.conf import settings
from mydata import MyDataClient, MyDataClientConfig
from mydata.models import (
    Address, Counterpart, Country, Currency, 
    IncomeClassification, IncomeClassificationCategory, IncomeClassificationValue,
    Invoice as MyDataInvoice, InvoiceHeader, InvoiceRow, InvoiceType, 
    Issuer, PaymentMethodDetail, PaymentMethodType, ResponseDoc,
    VatCategory
)

def send_invoice_to_mydata(invoice):
    """
    Sends a Marina Invoice to the Greek myDATA platform.
    """
    from marina.router import get_active_tenant
    from marina.models import TenantConfig

    tenant_slug = get_active_tenant()
    if tenant_slug:
        prefix = f"TENANT_{tenant_slug.upper()}_"
        user_id = os.getenv(f"{prefix}MYDATA_USER") or os.getenv("MYDATA_USER")
        sub_key = os.getenv(f"{prefix}MYDATA_SUBSCRIPTION_KEY") or os.getenv("MYDATA_SUBSCRIPTION_KEY")
        env = os.getenv(f"{prefix}MYDATA_ENVIRONMENT") or os.getenv("MYDATA_ENVIRONMENT", "sandbox")
        my_vat = os.getenv(f"{prefix}MYDATA_VAT_NUMBER") or os.getenv("MYDATA_VAT_NUMBER")
        if not my_vat:
            db_config = TenantConfig.objects.first()
            my_vat = db_config.vat_number if db_config else "888888888"
    else:
        user_id = os.getenv("MYDATA_USER")
        sub_key = os.getenv("MYDATA_SUBSCRIPTION_KEY")
        env = os.getenv("MYDATA_ENVIRONMENT", "sandbox")
        my_vat = os.getenv("MYDATA_VAT_NUMBER")
        if not my_vat:
            db_config = TenantConfig.objects.first()
            my_vat = db_config.vat_number if db_config else "888888888"

    if not user_id or not sub_key:
        return False, "myDATA credentials missing in .env"

    config = MyDataClientConfig(environment=env)
    client = MyDataClient(user_id=user_id, subscription_key=sub_key, config=config)

    # 1. Issuer (Your company)
    issuer = Issuer(vat_number=my_vat, country=Country.GR, branch=0)

    # 2. Counterpart (The customer)
    # Under Greek tax laws, B2C retail receipts (11.2) do NOT require counterpart/client AFM details
    if invoice.document_type in ['RECEIPT', 'TAXFREE']:
        counterpart = None
    else:
        customer_vat = invoice.customer.vat_number or '999999999'
        customer_city = getattr(invoice.customer, 'city', None) or 'Samos'
        a = Address(postal_code="00000", city=customer_city)
        counterpart = Counterpart(
            vat_number=customer_vat, 
            country=Country.GR, 
            branch=0, 
            address=a
        )

    # 3. Header
    header = InvoiceHeader()
    header.series = "A" # Or from settings
    header.aa = str(invoice.id)
    header.issue_date = invoice.date.isoformat()
    if invoice.document_type in ['RECEIPT', 'TAXFREE']:
        header.invoice_type = InvoiceType.VALUE_11_2 # 11.2 is Retail Service Receipt (B2C)
    else:
        header.invoice_type = InvoiceType.VALUE_2_1 # 2.1 is Service Invoice (B2B)
    header.currency = Currency.EUR

    # 4. Payment Method
    payment = PaymentMethodDetail()
    if invoice.payment_method == 'CASH':
        payment.type_value = PaymentMethodType.CASH
    elif invoice.payment_method == 'CARD':
        payment.type_value = PaymentMethodType.POS
    else:
        payment.type_value = PaymentMethodType.BANK_ACC_LOCAL
    
    payment.amount = Decimal(str(invoice.total_amount))

    # 5. Rows (Items)
    rows = []
    for i, item in enumerate(invoice.items.all(), 1):
        row = InvoiceRow()
        row.line_number = i
        row.net_value = Decimal(str(item.unit_price * Decimal(item.quantity)))
        
        # Mapping VAT dynamically based on VatRateConfig
        from marina.models import VatRateConfig
        item_tax_rate = Decimal(str(item.tax_rate or 24.00))
        
        # Default fallback is VAT_1 (24%)
        row.vat_category = VatCategory.VAT_1
        
        # Try to find corresponding category in DB
        vat_cfg = VatRateConfig.objects.filter(rate=item_tax_rate).first()
        if vat_cfg:
            try:
                row.vat_category = VatCategory(vat_cfg.mydata_vat_category)
            except ValueError:
                pass
        else:
            # Fallback mappings for standard Greek rates if not found in DB
            fallback_map = {
                Decimal("24.00"): VatCategory.VAT_1,
                Decimal("13.00"): VatCategory.VAT_2,
                Decimal("6.00"): VatCategory.VAT_3,
                Decimal("17.00"): VatCategory.VAT_4,
                Decimal("9.00"): VatCategory.VAT_5,
                Decimal("4.00"): VatCategory.VAT_6,
                Decimal("0.00"): VatCategory.VAT_7,
            }
            if item_tax_rate in fallback_map:
                row.vat_category = fallback_map[item_tax_rate]

        # Calculate VAT amount
        row.vat_amount = row.net_value * (item_tax_rate / Decimal("100.0"))
        
        # Classification (Mandatory for myDATA)
        row.income_classification = [
            IncomeClassification(
                classification_type=IncomeClassificationValue.E3_561_001, # Sales of services
                classification_category=IncomeClassificationCategory.CATEGORY1_3, # Service income
                amount=row.net_value,
            )
        ]
        rows.append(row)

    # 6. Construct Final Invoice
    mydata_invoice = MyDataInvoice()
    mydata_invoice.issuer = issuer
    if counterpart:
        mydata_invoice.counterpart = counterpart
    mydata_invoice.invoice_header = header
    mydata_invoice.invoice_details = rows
    mydata_invoice.add_payment_method(payment)
    mydata_invoice.summarize()

    try:
        response_doc = client.send_invoice(invoice=mydata_invoice, response_model=ResponseDoc)
        for response in response_doc.response:
            if response.status_code == 'Success':
                invoice.mydata_mark = response.invoice_mark
                invoice.mydata_uid = response.invoice_uid
                invoice.save()
                return True, f"Success: Mark {response.invoice_mark}"
            else:
                errors = ", ".join([e.message for e in response.errors])
                return False, f"Failed: {errors}"
    except Exception as e:
        return False, str(e)

    return False, "Unknown error"
