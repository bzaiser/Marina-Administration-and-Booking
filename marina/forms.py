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
