from django import forms
from .models import Booking, Boat, Customer, Berth

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['boat', 'berth', 'start_date', 'end_date', 'booking_type', 'reference', 'is_at_sea', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'boat': forms.Select(attrs={'class': 'form-select'}),
            'berth': forms.Select(attrs={'class': 'form-select'}),
            'booking_type': forms.Select(attrs={'class': 'form-select'}),
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
    flag = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select Flag..."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['flag'].label_from_instance = lambda obj: f"{obj.iso_code.upper()} - {obj.name}"

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
