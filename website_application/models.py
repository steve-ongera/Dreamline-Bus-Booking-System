from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class BusOperator(models.Model):
    """Bus company/operator information"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='operators/logos/', null=True, blank=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Amenity(models.Model):
    """Bus amenities like WiFi, AC, TV, etc."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Icon class or emoji")
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return self.name


class SeatLayout(models.Model):
    """Predefined seat layouts for different bus types"""
    name = models.CharField(max_length=100, help_text="e.g., '2x2 Standard', '2x1 VIP'")
    total_rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_per_row = models.IntegerField(validators=[MinValueValidator(1)])
    total_seats = models.IntegerField()
    layout_config = models.JSONField(
        help_text="JSON configuration for seat positions, door location, etc."
    )
    # Example layout_config structure:
    # {
    #   "door_position": "front-left",
    #   "rows": [
    #     {"row": 1, "seats": [{"position": "A", "type": "window"}, {"position": "B", "type": "aisle"}]},
    #     ...
    #   ]
    # }
    image = models.ImageField(upload_to='layouts/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.total_seats} seats)"


class Bus(models.Model):
    """Individual bus with its layout and amenities"""
    BUS_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('luxury', 'Luxury'),
        ('vip', 'VIP'),
        ('sleeper', 'Sleeper'),
    ]
    
    operator = models.ForeignKey(BusOperator, on_delete=models.CASCADE, related_name='buses')
    registration_number = models.CharField(max_length=50, unique=True)
    bus_name = models.CharField(max_length=200, help_text="e.g., 'Makarios X13'")
    bus_type = models.CharField(max_length=20, choices=BUS_TYPE_CHOICES)
    seat_layout = models.ForeignKey(SeatLayout, on_delete=models.PROTECT)
    amenities = models.ManyToManyField(Amenity, blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    total_ratings = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bus_name} ({self.registration_number})"


class Location(models.Model):
    """Cities and towns"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    county = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class BoardingPoint(models.Model):
    """Specific boarding/dropping points in a location"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='boarding_points')
    name = models.CharField(max_length=200, help_text="e.g., 'Nairobi CBD Office', 'South C'")
    address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['location', 'name']
    
    def __str__(self):
        return f"{self.location.name} - {self.name}"


class Route(models.Model):
    """Main routes between locations"""
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_from')
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_to')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_duration = models.DurationField(help_text="Estimated travel time")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['origin', 'destination']
    
    def __str__(self):
        return f"{self.origin.name} → {self.destination.name}"


class RouteStop(models.Model):
    """Intermediate stops along a route"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    boarding_point = models.ForeignKey(BoardingPoint, on_delete=models.CASCADE)
    stop_order = models.IntegerField(help_text="Order of stop along the route")
    time_from_origin = models.DurationField(help_text="Time from origin to this stop")
    is_pickup = models.BooleanField(default=True)
    is_dropoff = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['stop_order']
        unique_together = ['route', 'stop_order']
    
    def __str__(self):
        return f"{self.route} - Stop {self.stop_order}: {self.boarding_point}"


class Trip(models.Model):
    """Scheduled bus trips"""
    TRIP_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    base_fare_vip = models.DecimalField(max_digits=10, decimal_places=2)
    base_fare_business = models.DecimalField(max_digits=10, decimal_places=2)
    base_fare_normal = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRIP_STATUS_CHOICES, default='scheduled')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['departure_date', 'departure_time']
        unique_together = ['bus', 'departure_date', 'departure_time']
    
    def __str__(self):
        return f"{self.route} - {self.departure_date} {self.departure_time}"
    
    def available_seats_count(self):
        """Count available seats for this trip"""
        booked = self.seat_bookings.filter(
            booking__status__in=['pending', 'confirmed', 'paid']
        ).count()
        return self.bus.seat_layout.total_seats - booked


class Seat(models.Model):
    """Individual seats in a trip"""
    SEAT_CLASS_CHOICES = [
        ('vip', 'VIP'),
        ('business', 'Business'),
        ('normal', 'Normal/Economy'),
    ]
    
    SEAT_POSITION_CHOICES = [
        ('window', 'Window'),
        ('aisle', 'Aisle'),
        ('middle', 'Middle'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    row_number = models.IntegerField()
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES)
    position = models.CharField(max_length=20, choices=SEAT_POSITION_CHOICES)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['trip', 'seat_number']
        ordering = ['row_number', 'seat_number']
    
    def __str__(self):
        return f"Trip {self.trip.id} - Seat {self.seat_number}"
    
    def get_fare(self):
        """Get fare based on seat class"""
        if self.seat_class == 'vip':
            return self.trip.base_fare_vip
        elif self.seat_class == 'business':
            return self.trip.base_fare_business
        else:
            return self.trip.base_fare_normal


class Booking(models.Model):
    """Customer bookings"""
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_reference = models.CharField(max_length=20, unique=True, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings')
    
    # Customer details (no login required)
    customer_full_name = models.CharField(max_length=200)
    customer_id_number = models.CharField(max_length=50)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Journey details
    boarding_point = models.ForeignKey(
        BoardingPoint, 
        on_delete=models.PROTECT, 
        related_name='pickup_bookings'
    )
    dropping_point = models.ForeignKey(
        BoardingPoint, 
        on_delete=models.PROTECT, 
        related_name='dropoff_bookings'
    )
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate unique booking reference"""
        return f"BK{uuid.uuid4().hex[:8].upper()}"
    
    def __str__(self):
        return f"{self.booking_reference} - {self.customer_full_name}"


class SeatBooking(models.Model):
    """Link between bookings and seats"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='seat_bookings')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='bookings')
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['booking', 'seat']
    
    def __str__(self):
        return f"{self.booking.booking_reference} - Seat {self.seat.seat_number}"


class Payment(models.Model):
    """Payment transactions"""
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('cash', 'Cash'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_phone = models.CharField(max_length=20, blank=True)
    mpesa_receipt = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='initiated')
    
    # M-Pesa specific fields
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"


class Review(models.Model):
    """Customer reviews for trips/buses"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.rating}★"