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
    user_id = os.getenv("MYDATA_USER")
    sub_key = os.getenv("MYDATA_SUBSCRIPTION_KEY")
    env = os.getenv("MYDATA_ENVIRONMENT", "sandbox")
    my_vat = os.getenv("MYDATA_VAT_NUMBER", "888888888")

    if not user_id or not sub_key:
        return False, "myDATA credentials missing in .env"

    config = MyDataClientConfig(environment=env)
    client = MyDataClient(user_id=user_id, subscription_key=sub_key, config=config)

    # 1. Issuer (Your company)
    issuer = Issuer(vat_number=my_vat, country=Country.GR, branch=0)

    # 2. Counterpart (The customer)
    # Note: Customer model needs a vat_number field. For now using a placeholder.
    # TODO: Add vat_number and address fields to Customer model if needed.
    customer_vat = getattr(invoice.customer, 'vat_number', '999999999')
    a = Address(postal_code="00000", city=invoice.customer.city or "Unknown")
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
    header.invoice_type = InvoiceType.VALUE_2_1 # 2.1 is Retail Invoice (Appodeixi Lianikis)
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
        
        # Mapping VAT (Assuming 24% by default for GR)
        # TODO: Use item's actual tax rate if available
        row.vat_category = VatCategory.VAT_1 # 24%
        row.vat_amount = row.net_value * Decimal("0.24")
        
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
