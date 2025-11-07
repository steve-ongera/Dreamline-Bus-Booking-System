from django import forms
from .models import Bus, BusOperator, SeatLayout, Amenity


class BusForm(forms.ModelForm):
    """Form for creating/editing buses"""
    
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select all amenities available in this bus"
    )
    
    class Meta:
        model = Bus
        fields = [
            'operator', 'registration_number', 'bus_name', 'bus_type',
            'seat_layout', 'amenities', 'is_active'
        ]
        widgets = {
            'operator': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., KCA 123X',
                'required': True
            }),
            'bus_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Makarios Express X13',
                'required': True
            }),
            'bus_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'seat_layout': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active operators and layouts
        self.fields['operator'].queryset = BusOperator.objects.filter(is_active=True)
        self.fields['seat_layout'].queryset = SeatLayout.objects.all()


class BusOperatorForm(forms.ModelForm):
    """Form for creating/editing bus operators"""
    
    class Meta:
        model = BusOperator
        fields = [
            'name', 'logo', 'contact_phone', 'contact_email',
            'description', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Modern Coast Express',
                'required': True
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 700 000000',
                'required': True
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'info@operator.com',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief description about the operator...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SeatLayoutForm(forms.ModelForm):
    """Form for creating/editing seat layouts"""
    
    # Custom field for JSON configuration with better UX
    layout_config_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': '''Example JSON structure:
{
  "door_position": "front-left",
  "rows": [
    {
      "row": 1,
      "seats": [
        {"position": "A", "type": "window", "class": "vip"},
        {"position": "B", "type": "aisle", "class": "business"}
      ]
    }
  ]
}'''
        }),
        required=False,
        help_text="JSON configuration for seat positions (optional - can be edited later)"
    )
    
    class Meta:
        model = SeatLayout
        fields = [
            'name', 'total_rows', 'seats_per_row', 'total_seats',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2x2 Standard Layout',
                'required': True
            }),
            'total_rows': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'e.g., 12',
                'required': True
            }),
            'seats_per_row': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'e.g., 4',
                'required': True
            }),
            'total_seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'e.g., 48',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.layout_config:
            import json
            self.fields['layout_config_text'].initial = json.dumps(
                self.instance.layout_config, 
                indent=2
            )
    
    def clean_layout_config_text(self):
        """Validate JSON configuration"""
        import json
        text = self.cleaned_data.get('layout_config_text', '').strip()
        
        if not text:
            # Return default empty structure
            return {
                "door_position": "front-left",
                "rows": []
            }
        
        try:
            config = json.loads(text)
            return config
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {str(e)}")
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.layout_config = self.cleaned_data['layout_config_text']
        
        if commit:
            instance.save()
        
        return instance
    

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Trip, Bus, Route


class TripForm(forms.ModelForm):
    """Form for scheduling/editing trips"""
    
    class Meta:
        model = Trip
        fields = [
            'bus', 'route', 'departure_date', 'departure_time', 'arrival_time',
            'base_fare_vip', 'base_fare_business', 'base_fare_normal',
            'status', 'is_active'
        ]
        widgets = {
            'bus': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'route': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'departure_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'arrival_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'base_fare_vip': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'base_fare_business': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'base_fare_normal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active buses and routes
        self.fields['bus'].queryset = Bus.objects.filter(is_active=True).select_related('operator', 'seat_layout')
        self.fields['route'].queryset = Route.objects.filter(is_active=True).select_related('origin', 'destination')
        
        # Set default date to today
        if not self.instance.pk:
            self.initial['departure_date'] = timezone.now().date()
            self.initial['status'] = 'scheduled'
            self.initial['is_active'] = True
    
    def clean_departure_date(self):
        """Validate departure date is not in the past"""
        departure_date = self.cleaned_data.get('departure_date')
        
        # Allow past dates for editing existing trips
        if not self.instance.pk:
            if departure_date < timezone.now().date():
                raise ValidationError("Departure date cannot be in the past.")
        
        return departure_date
    
    def clean_arrival_time(self):
        """Validate arrival time is after departure time"""
        departure_time = self.cleaned_data.get('departure_time')
        arrival_time = self.cleaned_data.get('arrival_time')
        
        if departure_time and arrival_time:
            if arrival_time <= departure_time:
                raise ValidationError("Arrival time must be after departure time.")
        
        return arrival_time
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        bus = cleaned_data.get('bus')
        departure_date = cleaned_data.get('departure_date')
        departure_time = cleaned_data.get('departure_time')
        
        # Check for duplicate trips (same bus, date, and time)
        if bus and departure_date and departure_time:
            duplicate_check = Trip.objects.filter(
                bus=bus,
                departure_date=departure_date,
                departure_time=departure_time
            )
            
            # Exclude current instance when editing
            if self.instance.pk:
                duplicate_check = duplicate_check.exclude(pk=self.instance.pk)
            
            if duplicate_check.exists():
                raise ValidationError(
                    f"A trip for {bus.bus_name} is already scheduled on "
                    f"{departure_date} at {departure_time}."
                )
        
        # Validate fare amounts
        vip_fare = cleaned_data.get('base_fare_vip', 0)
        business_fare = cleaned_data.get('base_fare_business', 0)
        normal_fare = cleaned_data.get('base_fare_normal', 0)
        
        if vip_fare < business_fare:
            raise ValidationError("VIP fare should be equal to or greater than Business fare.")
        
        if business_fare < normal_fare:
            raise ValidationError("Business fare should be equal to or greater than Normal fare.")
        
        return cleaned_data