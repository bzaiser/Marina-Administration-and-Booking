from django import forms
from .models import Booking, Boat, Customer, Berth, Country, Invoice, InvoiceItem, ServiceProvider

class InvoiceForm(forms.ModelForm):
    discount = forms.DecimalField(required=False, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_method = forms.ChoiceField(choices=Invoice.PAYMENT_METHOD, required=False, initial='CASH', widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = ['customer', 'status', 'payment_method', 'discount']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select select2-search'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description...'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or Person Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['boat', 'berth', 'start_date', 'end_date', 'booking_type', 'status', 'reference', 'is_at_sea', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'boat': forms.Select(attrs={'class': 'select2-search'}),
            'berth': forms.Select(attrs={'class': 'select2-search'}),
            'booking_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'nationality', 'language']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DE, US, GR...'}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DE, EN, FR...'}),
        }

class BoatForm(forms.ModelForm):
    flag = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select select2-search'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "Select Flag...")]
        for country in Country.objects.all().order_by('name'):
            choices.append((country.iso_code.upper(), f"{country.iso_code.upper()} - {country.name}"))
        self.fields['flag'].choices = choices

    class Meta:
        model = Boat
        fields = ['name', 'boat_type', 'length', 'weight', 'flag', 'color', 'year_built', 'last_maintenance', 'diesel_tank', 'water_tank', 'notes', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Boat Name'}),
            'boat_type': forms.Select(attrs={'class': 'form-select'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'meters'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'tons'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2015'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'diesel_tank': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Liters'}),
            'water_tank': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Liters'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

from .models import BookingService

class BookingServiceForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ['service', 'quantity', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select select2-search'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'value': '1.0'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes...'}),
        }

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ['boat', 'service', 'berth', 'quantity', 'status', 'scheduled_start', 'scheduled_end', 'workload_hours', 'notes']
        widgets = {
            'boat': forms.Select(attrs={'class': 'form-select select2-search'}),
            'service': forms.Select(attrs={'class': 'form-select select2-search'}),
            'berth': forms.Select(attrs={'class': 'form-select select2-search'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'value': '1.0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'scheduled_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'workload_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'Estimated hours'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Job details...'}),
        }
