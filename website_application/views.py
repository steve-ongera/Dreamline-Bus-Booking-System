from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Location, Trip, Seat, Booking, SeatBooking, 
    Payment, BoardingPoint, RouteStop
)


def home_view(request):
    """Home page with search form"""
    context = {
        'page_title': 'Book Your Bus Ticket'
    }
    return render(request, 'home.html', context)


def search_results_view(request):
    """Search results page showing available trips"""
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    travel_date = request.GET.get('date')
    
    if not all([origin_id, destination_id, travel_date]):
        return render(request, 'search_results.html', {
            'error': 'Please provide origin, destination, and travel date'
        })
    
    try:
        origin = Location.objects.get(id=origin_id)
        destination = Location.objects.get(id=destination_id)
        date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
    except (Location.DoesNotExist, ValueError):
        return render(request, 'search_results.html', {
            'error': 'Invalid search parameters'
        })
    
    context = {
        'origin': origin,
        'destination': destination,
        'travel_date': date_obj,
        'travel_date_str': travel_date,
        'page_title': f'{origin.name} to {destination.name}'
    }
    
    return render(request, 'search_results.html', context)


# ============== AJAX API VIEWS ==============

@require_http_methods(["GET"])
def api_autocomplete_locations(request):
    """Autocomplete API for location search"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    locations = Location.objects.filter(
        Q(name__icontains=query) | Q(county__icontains=query),
        is_active=True
    )[:10]
    
    results = [
        {
            'id': loc.id,
            'name': loc.name,
            'county': loc.county,
            'display': f"{loc.name}, {loc.county}"
        }
        for loc in locations
    ]
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_search_trips(request):
    """API to search for available trips"""
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    travel_date = request.GET.get('date')
    
    if not all([origin_id, destination_id, travel_date]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Find direct routes and routes that pass through
    trips = Trip.objects.filter(
        Q(route__origin_id=origin_id, route__destination_id=destination_id) |
        (
            Q(route__stops__boarding_point__location_id=origin_id) &
            Q(route__stops__boarding_point__location_id=destination_id)
        ),
        departure_date=date_obj,
        is_active=True,
        status='scheduled'
    ).select_related(
        'bus__operator',
        'bus__seat_layout',
        'route__origin',
        'route__destination'
    ).prefetch_related(
        'bus__amenities',
        'seats'
    ).distinct().order_by('departure_time')

    
    results = []
    for trip in trips:
        # Count available seats by class
        seats = trip.seats.filter(is_available=True)
        vip_count = seats.filter(seat_class='vip').count()
        business_count = seats.filter(seat_class='business').count()
        normal_count = seats.filter(seat_class='normal').count()
        
        # Get amenities
        amenities = [
            {'name': amenity.name, 'icon': amenity.icon}
            for amenity in trip.bus.amenities.all()
        ]
        
        results.append({
            'id': trip.id,
            'bus_name': trip.bus.bus_name,
            'operator': trip.bus.operator.name,
            'route': f"{trip.route.origin.name} → {trip.route.destination.name}",
            'departure_time': trip.departure_time.strftime('%H:%M'),
            'arrival_time': trip.arrival_time.strftime('%H:%M'),
            'rating': float(trip.bus.rating),
            'total_ratings': trip.bus.total_ratings,
            'amenities': amenities,
            'prices': {
                'vip': float(trip.base_fare_vip) if vip_count > 0 else None,
                'business': float(trip.base_fare_business) if business_count > 0 else None,
                'normal': float(trip.base_fare_normal) if normal_count > 0 else None,
            },
            'available_seats': {
                'vip': vip_count,
                'business': business_count,
                'normal': normal_count,
                'total': vip_count + business_count + normal_count
            }
        })
    
    return JsonResponse({'trips': results})


@require_http_methods(["GET"])
def api_get_seats(request, trip_id):
    """API to get seat layout and availability for a trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Get all seats with their status
    seats = trip.seats.all().order_by('row_number', 'seat_number')
    
    # Check for temporary locks
    now = timezone.now()
    
    seat_data = []
    for seat in seats:
        # Check if seat is temporarily locked
        lock_key = f"seat_lock_{seat.id}"
        locked_by = cache.get(lock_key)
        
        is_locked = locked_by is not None
        is_available = seat.is_available and not is_locked
        
        seat_data.append({
            'id': seat.id,
            'seat_number': seat.seat_number,
            'row_number': seat.row_number,
            'seat_class': seat.seat_class,
            'seat_class_display': seat.get_seat_class_display(),
            'position': seat.position,
            'position_display': seat.get_position_display(),
            'is_available': is_available,
            'is_locked': is_locked,
            'fare': float(seat.get_fare())
        })
    
    # Get layout configuration
    layout_config = trip.bus.seat_layout.layout_config
    
    return JsonResponse({
        'seats': seat_data,
        'layout': layout_config,
        'total_seats': trip.bus.seat_layout.total_seats,
        'total_rows': trip.bus.seat_layout.total_rows
    })


@require_http_methods(["POST"])
def api_lock_seat(request):
    """API to temporarily lock a seat (2 minutes)"""
    try:
        data = json.loads(request.body)
        seat_id = data.get('seat_id')
        session_id = request.session.session_key
        
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        seat = get_object_or_404(Seat, id=seat_id)
        
        if not seat.is_available:
            return JsonResponse({
                'success': False,
                'error': 'Seat is already booked'
            }, status=400)
        
        lock_key = f"seat_lock_{seat_id}"
        existing_lock = cache.get(lock_key)
        
        if existing_lock and existing_lock != session_id:
            return JsonResponse({
                'success': False,
                'error': 'Seat is currently being selected by another user'
            }, status=400)
        
        # Lock for 2 minutes
        cache.set(lock_key, session_id, 120)
        
        return JsonResponse({
            'success': True,
            'seat_id': seat_id,
            'expires_in': 120
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@require_http_methods(["POST"])
def api_unlock_seat(request):
    """API to unlock a temporarily locked seat"""
    try:
        data = json.loads(request.body)
        seat_id = data.get('seat_id')
        session_id = request.session.session_key
        
        lock_key = f"seat_lock_{seat_id}"
        existing_lock = cache.get(lock_key)
        
        if existing_lock == session_id:
            cache.delete(lock_key)
            return JsonResponse({'success': True})
        
        return JsonResponse({
            'success': False,
            'error': 'Seat not locked by this session'
        }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@require_http_methods(["GET"])
def api_get_boarding_points(request, trip_id):
    """API to get boarding and dropping points for a trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Get route stops
    stops = trip.route.stops.select_related('boarding_point__location').all()
    
    boarding_points = []
    dropping_points = []
    
    for stop in stops:
        # IMPORTANT: Return the RouteStop ID, not the BoardingPoint ID
        point_data = {
            'id': stop.id,  # This is the RouteStop ID - what the booking expects
            'boarding_point_id': stop.boarding_point.id,  # This is the actual BoardingPoint ID
            'name': stop.boarding_point.name,
            'location': stop.boarding_point.location.name,
            'address': stop.boarding_point.address,
            'display': f"{stop.boarding_point.name} - {stop.boarding_point.location.name}"
        }
        
        if stop.is_pickup:
            boarding_points.append(point_data)
        if stop.is_dropoff:
            dropping_points.append(point_data)
    
    return JsonResponse({
        'boarding_points': boarding_points,
        'dropping_points': dropping_points
    })



@require_http_methods(["POST"])
def api_calculate_total(request):
    """API to calculate total booking amount"""
    try:
        data = json.loads(request.body)
        seat_ids = data.get('seat_ids', [])
        
        if not seat_ids:
            return JsonResponse({'error': 'No seats selected'}, status=400)
        
        seats = Seat.objects.filter(id__in=seat_ids)
        
        if seats.count() != len(seat_ids):
            return JsonResponse({'error': 'Some seats not found'}, status=400)
        
        total = sum(seat.get_fare() for seat in seats)
        
        seat_details = [
            {
                'seat_number': seat.seat_number,
                'seat_class': seat.get_seat_class_display(),
                'fare': float(seat.get_fare())
            }
            for seat in seats
        ]
        
        return JsonResponse({
            'success': True,
            'total': float(total),
            'seats': seat_details,
            'seat_count': len(seat_ids)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@csrf_exempt  # Add this if you're getting CSRF token errors
@require_http_methods(["POST"])
def api_create_booking(request):
    """API to create a booking with payment initiation"""
    try:
        # Log the raw request body for debugging
        logger.info(f"Request body: {request.body.decode('utf-8')}")
        
        data = json.loads(request.body)
        logger.info(f"Parsed data: {data}")
        
        # Validate required fields
        required_fields = [
            'trip_id', 'seat_ids', 'boarding_point_id', 
            'dropping_point_id', 'full_name', 'id_number', 
            'email', 'phone'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            logger.error(error_msg)
            return JsonResponse({
                'error': error_msg,
                'missing_fields': missing_fields
            }, status=400)
        
        # Validate data types
        try:
            trip_id = int(data['trip_id'])
            boarding_point_id = int(data['boarding_point_id'])
            dropping_point_id = int(data['dropping_point_id'])
            seat_ids = [int(sid) for sid in data['seat_ids']]
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid data type: {str(e)}")
            return JsonResponse({
                'error': 'Invalid data type for numeric fields'
            }, status=400)
        
        # Validate seat_ids is not empty
        if not seat_ids:
            return JsonResponse({
                'error': 'At least one seat must be selected'
            }, status=400)
        
        trip = get_object_or_404(Trip, id=trip_id)
        
        # Verify session has locks on these seats
        if not request.session.session_key:
            request.session.create()
        
        session_id = request.session.session_key
        logger.info(f"Session ID: {session_id}")
        
        locked_seats = []
        unlocked_seats = []
        
        for seat_id in seat_ids:
            lock_key = f"seat_lock_{seat_id}"
            locked_by = cache.get(lock_key)
            logger.info(f"Seat {seat_id} locked by: {locked_by}")
            
            if locked_by == session_id:
                locked_seats.append(seat_id)
            else:
                unlocked_seats.append(seat_id)
        
        if unlocked_seats:
            return JsonResponse({
                'error': f'Seat locks expired or invalid for seats: {unlocked_seats}. Please reselect seats.'
            }, status=400)
        
        # Get seats and verify availability
        seats = Seat.objects.filter(id__in=seat_ids, is_available=True)
        
        if seats.count() != len(seat_ids):
            unavailable = set(seat_ids) - set(seats.values_list('id', flat=True))
            return JsonResponse({
                'error': f'Some seats are no longer available: {list(unavailable)}'
            }, status=400)
        
        # Validate boarding and dropping points
        try:
            boarding_route_stop = RouteStop.objects.select_related('boarding_point').get(id=boarding_point_id)
            dropping_route_stop = RouteStop.objects.select_related('boarding_point').get(id=dropping_point_id)
            
            boarding_point = boarding_route_stop.boarding_point
            dropping_point = dropping_route_stop.boarding_point
            
        except RouteStop.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid boarding or dropping point'
            }, status=400)
        
        # Calculate total
        total_amount = sum(seat.get_fare() for seat in seats)
        
        # Create booking
        booking = Booking.objects.create(
            trip=trip,
            customer_full_name=data['full_name'],
            customer_id_number=data['id_number'],
            customer_email=data['email'],
            customer_phone=data['phone'],
            boarding_point=boarding_point,
            dropping_point=dropping_point,
            total_amount=total_amount,
            status='pending'
        )
        
        logger.info(f"Created booking: {booking.booking_reference}")
        
        # Create seat bookings and mark seats as unavailable
        for seat in seats:
            SeatBooking.objects.create(
                booking=booking,
                seat=seat,
                fare=seat.get_fare()
            )
            seat.is_available = False
            seat.save()
            
            # Remove lock
            lock_key = f"seat_lock_{seat.id}"
            cache.delete(lock_key)
            logger.info(f"Removed lock for seat {seat.id}")
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            transaction_id=f"TXN{booking.booking_reference}",
            payment_method='mpesa',
            amount=total_amount,
            mpesa_phone=data['phone'],
            status='initiated'
        )
        
        logger.info(f"Payment initiated: {payment.transaction_id}")
        
        # TODO: Initiate M-Pesa STK Push here
        
        return JsonResponse({
            'success': True,
            'booking_reference': booking.booking_reference,
            'total_amount': float(total_amount),
            'payment_id': payment.id,
            'message': 'Booking created. Please complete payment.'
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({
            'error': 'Invalid JSON format',
            'details': str(e)
        }, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error in booking creation: {str(e)}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)