from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    BusOperator, Amenity, SeatLayout, Bus, Location, 
    BoardingPoint, Route, RouteStop, Trip, Seat, 
    Booking, SeatBooking, Payment, Review
)


@admin.register(BusOperator)
class BusOperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_phone', 'contact_email', 'total_buses', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_phone', 'contact_email']
    readonly_fields = ['created_at']
    
    def total_buses(self, obj):
        return obj.buses.count()
    total_buses.short_description = 'Total Buses'


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'description']
    search_fields = ['name', 'description']


@admin.register(SeatLayout)
class SeatLayoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_rows', 'seats_per_row', 'total_seats', 'preview_image']
    list_filter = ['total_seats']
    search_fields = ['name']
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" />', obj.image.url)
        return '-'
    preview_image.short_description = 'Layout Preview'


class BusAmenityInline(admin.TabularInline):
    model = Bus.amenities.through
    extra = 1


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['bus_name', 'registration_number', 'operator', 'bus_type', 'rating_display', 'total_seats', 'is_active']
    list_filter = ['bus_type', 'is_active', 'operator', 'created_at']
    search_fields = ['bus_name', 'registration_number', 'operator__name']
    readonly_fields = ['created_at', 'rating', 'total_ratings']
    filter_horizontal = ['amenities']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('operator', 'bus_name', 'registration_number', 'bus_type')
        }),
        ('Seat Configuration', {
            'fields': ('seat_layout',)
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Rating & Status', {
            'fields': ('rating', 'total_ratings', 'is_active', 'created_at')
        }),
    )
    
    def total_seats(self, obj):
        return obj.seat_layout.total_seats
    total_seats.short_description = 'Seats'
    
    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating)
        formatted_rating = f"{obj.rating:.2f}"
        return format_html('{} ({})', stars, formatted_rating)
    rating_display.short_description = 'Rating'



@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'total_boarding_points', 'is_active']
    list_filter = ['county', 'is_active']
    search_fields = ['name', 'county']
    prepopulated_fields = {'slug': ('name',)}
    
    def total_boarding_points(self, obj):
        return obj.boarding_points.count()
    total_boarding_points.short_description = 'Boarding Points'


@admin.register(BoardingPoint)
class BoardingPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'contact_phone', 'has_coordinates', 'is_active']
    list_filter = ['location', 'is_active']
    search_fields = ['name', 'location__name', 'address']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('location', 'name', 'address', 'landmark', 'contact_phone')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def has_coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_coordinates.short_description = 'GPS'


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    fields = ['stop_order', 'boarding_point', 'time_from_origin', 'is_pickup', 'is_dropoff']
    ordering = ['stop_order']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_display', 'distance_km', 'estimated_duration', 'total_stops', 'is_active']
    list_filter = ['is_active', 'origin', 'destination']
    search_fields = ['origin__name', 'destination__name']
    inlines = [RouteStopInline]
    
    fieldsets = (
        ('Route Information', {
            'fields': ('origin', 'destination', 'distance_km', 'estimated_duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def route_display(self, obj):
        return format_html(
            '<strong>{}</strong> → <strong>{}</strong>',
            obj.origin.name,
            obj.destination.name
        )
    route_display.short_description = 'Route'
    
    def total_stops(self, obj):
        return obj.stops.count()
    total_stops.short_description = 'Stops'


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'stop_order', 'boarding_point', 'time_from_origin', 'pickup_dropoff']
    list_filter = ['route', 'is_pickup', 'is_dropoff']
    search_fields = ['route__origin__name', 'route__destination__name', 'boarding_point__name']
    ordering = ['route', 'stop_order']
    
    def pickup_dropoff(self, obj):
        pickup = '🚌' if obj.is_pickup else ''
        dropoff = '🏁' if obj.is_dropoff else ''
        return format_html('{} {}', pickup, dropoff)
    pickup_dropoff.short_description = 'P/D'


class SeatInline(admin.TabularInline):
    model = Seat
    fk_name = 'trip'  # 🔹 explicitly tell Django which FK connects Seat → Trip
    extra = 0
    fields = ['seat_number', 'row_number', 'seat_class', 'position', 'is_available']
    readonly_fields = ['seat_number', 'row_number', 'seat_class', 'position']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        'trip_id', 'route_display', 'bus_info', 'departure_datetime', 
        'status_badge', 'available_seats', 'total_bookings', 'revenue'
    ]
    list_filter = ['status', 'departure_date', 'route__origin', 'route__destination', 'bus__operator']
    search_fields = ['bus__bus_name', 'route__origin__name', 'route__destination__name']
    date_hierarchy = 'departure_date'
    readonly_fields = ['created_at']
    
    # Only include inlines if you have the proper relationship
    # inlines = [SeatInline]  # Comment this out if causing issues
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('bus', 'route', 'departure_date', 'departure_time', 'arrival_time')
        }),
        ('Pricing', {
            'fields': ('base_fare_vip', 'base_fare_business', 'base_fare_normal')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'created_at')
        }),
    )
    
    def trip_id(self, obj):
        return f"#{obj.id}"
    trip_id.short_description = 'ID'
    
    def route_display(self, obj):
        return format_html(
            '<strong>{}</strong> → <strong>{}</strong>',
            obj.route.origin.name,
            obj.route.destination.name
        )
    route_display.short_description = 'Route'
    
    def bus_info(self, obj):
        return format_html(
            '{}<br/><small>{}</small>',
            obj.bus.bus_name,
            obj.bus.operator.name
        )
    bus_info.short_description = 'Bus'
    
    def departure_datetime(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.departure_date.strftime('%d %b %Y'),
            obj.departure_time.strftime('%I:%M %p')
        )
    departure_datetime.short_description = 'Departure'
    
    def status_badge(self, obj):
        colors = {
            'scheduled': '#17a2b8',
            'boarding': '#ffc107',
            'departed': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def available_seats(self, obj):
        # Use the relationship that actually exists
        try:
            # Try different possible relationship names
            if hasattr(obj, 'available_seats_count'):
                return obj.available_seats_count()
            elif hasattr(obj, 'bookings'):
                total_seats = obj.bus.total_seats if obj.bus else 0
                booked_seats = obj.bookings.filter(status__in=['confirmed', 'paid']).count()
                return total_seats - booked_seats
            else:
                return "N/A"
        except AttributeError:
            return "N/A"
    available_seats.short_description = 'Available'
    
    def total_bookings(self, obj):
        try:
            if hasattr(obj, 'bookings'):
                count = obj.bookings.filter(status__in=['confirmed', 'paid']).count()
                return count
            return 0
        except AttributeError:
            return 0
    total_bookings.short_description = 'Bookings'
    
    def revenue(self, obj):
        try:
            if hasattr(obj, 'bookings'):
                total = obj.bookings.filter(
                    status__in=['confirmed', 'paid']
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                # Format the number first, then wrap in HTML
                formatted_total = "KES {:,.2f}".format(total)
                return format_html('<strong>{}</strong>', formatted_total)
            return format_html('<strong>KES 0.00</strong>')
        except (AttributeError, TypeError, ValueError):
            return format_html('<strong>KES 0.00</strong>')
    revenue.short_description = 'Revenue'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'trip_info', 'seat_class', 'position', 'fare_display', 'availability']
    list_filter = ['seat_class', 'position', 'is_available', 'trip__departure_date']
    search_fields = ['seat_number', 'trip__bus__bus_name']
    
    def trip_info(self, obj):
        return format_html(
            'Trip #{} - {}',
            obj.trip.id,
            obj.trip.bus.bus_name
        )
    trip_info.short_description = 'Trip'
    
    def fare_display(self, obj):
        return format_html('KES {:,.2f}', obj.get_fare())
    fare_display.short_description = 'Fare'
    
    def availability(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Booked</span>')
    availability.short_description = 'Status'


class SeatBookingInline(admin.TabularInline):
    model = SeatBooking
    extra = 0
    readonly_fields = ['seat', 'fare']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['transaction_id', 'payment_method', 'amount', 'status', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'customer_full_name', 'trip_info', 
        'seats_booked', 'total_amount_display', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'trip__departure_date']
    search_fields = [
        'booking_reference', 'customer_full_name', 'customer_email', 
        'customer_phone', 'customer_id_number'
    ]
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [SeatBookingInline, PaymentInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'trip', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_full_name', 'customer_id_number', 'customer_email', 'customer_phone')
        }),
        ('Journey Details', {
            'fields': ('boarding_point', 'dropping_point')
        }),
        ('Payment', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def trip_info(self, obj):
        return format_html(
            '{} → {}<br/><small>{} {}</small>',
            obj.trip.route.origin.name,
            obj.trip.route.destination.name,
            obj.trip.departure_date.strftime('%d %b %Y'),
            obj.trip.departure_time.strftime('%I:%M %p')
        )
    trip_info.short_description = 'Trip'
    
    def seats_booked(self, obj):
        seats = obj.seat_bookings.all()
        seat_numbers = ', '.join([sb.seat.seat_number for sb in seats])
        return format_html('<strong>{}</strong>', seat_numbers)
    seats_booked.short_description = 'Seats'
    
    def total_amount_display(self, obj):
        formatted_amount = f"{obj.total_amount:,.2f}"
        return format_html('<strong>KES {}</strong>', formatted_amount)

    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#17a2b8',
            'confirmed': '#28a745',
            'cancelled': '#dc3545',
            'completed': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ['booking', 'seat_info', 'fare_display']
    list_filter = ['booking__status', 'seat__seat_class']
    search_fields = ['booking__booking_reference', 'seat__seat_number']
    
    def seat_info(self, obj):
        return format_html(
            'Seat {} ({}) - {}',
            obj.seat.seat_number,
            obj.seat.get_seat_class_display(),
            obj.seat.get_position_display()
        )
    seat_info.short_description = 'Seat Details'
    
    def fare_display(self, obj):
        return format_html('KES {:,.2f}', obj.fare)
    fare_display.short_description = 'Fare'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'booking', 'payment_method', 
        'amount_display', 'status_badge', 'created_at'
    ]
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = [
        'transaction_id', 'booking__booking_reference', 
        'mpesa_receipt', 'mpesa_phone'
    ]
    readonly_fields = [
        'transaction_id', 'merchant_request_id', 
        'checkout_request_id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'transaction_id', 'payment_method', 'amount', 'status')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_phone', 'mpesa_receipt', 'merchant_request_id', 'checkout_request_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return format_html('<strong>KES {:,.2f}</strong>', obj.amount)
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'initiated': '#6c757d',
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545',
            'refunded': '#17a2b8',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'bus', 'rating_display', 'created_at']
    list_filter = ['rating', 'created_at', 'bus__operator']
    search_fields = ['booking__booking_reference', 'bus__bus_name', 'comment']
    readonly_fields = ['created_at']
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html('{} ({})', stars, obj.rating)
    rating_display.short_description = 'Rating'