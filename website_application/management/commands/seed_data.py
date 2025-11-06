# website_application/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal
from website_application.models import (
    BusOperator, Amenity, SeatLayout, Bus, Location, 
    BoardingPoint, Route, RouteStop, Trip, Seat
)


class Command(BaseCommand):
    help = 'Seeds the database with Kenyan bus booking data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Clear existing data (preserves SeatLayout)
        self.clear_existing_data()
        
        # Create data in order
        amenities = self.create_amenities()
        operators = self.create_bus_operators()
        locations = self.create_locations()
        boarding_points = self.create_boarding_points(locations)
        
        # Get or create seat layout
        seat_layout = self.get_seat_layout()
        
        buses = self.create_buses(operators, seat_layout, amenities)
        routes = self.create_routes(locations)
        self.create_route_stops(routes, boarding_points)
        trips = self.create_trips(buses, routes)
        self.create_seats_for_trips(trips)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.print_summary()

    def clear_existing_data(self):
        """Clear only data created by this seeding script, preserve SeatLayout"""
        self.stdout.write('Clearing existing seeded data (preserving SeatLayout)...')
        
        # Delete in reverse order of dependencies
        Seat.objects.all().delete()
        Trip.objects.all().delete()
        RouteStop.objects.all().delete()
        Route.objects.all().delete()
        BoardingPoint.objects.all().delete()
        Location.objects.all().delete()
        Bus.objects.all().delete()
        BusOperator.objects.all().delete()
        Amenity.objects.all().delete()
        # Note: SeatLayout is NOT deleted
        
        self.stdout.write(self.style.SUCCESS('✓ Existing data cleared (SeatLayout preserved)'))

    def create_amenities(self):
        self.stdout.write('Creating amenities...')
        amenities_data = [
            {'name': 'WiFi', 'icon': '📶', 'description': 'Free WiFi on board'},
            {'name': 'AC', 'icon': '❄️', 'description': 'Air conditioning'},
            {'name': 'TV', 'icon': '📺', 'description': 'Entertainment screens'},
            {'name': 'USB Charging', 'icon': '🔌', 'description': 'USB charging ports'},
            {'name': 'Reclining Seats', 'icon': '🪑', 'description': 'Comfortable reclining seats'},
            {'name': 'Music System', 'icon': '🎵', 'description': 'Quality sound system'},
            {'name': 'Reading Lights', 'icon': '💡', 'description': 'Individual reading lights'},
            {'name': 'Blankets', 'icon': '🛏️', 'description': 'Complimentary blankets'},
            {'name': 'Water', 'icon': '💧', 'description': 'Complimentary water'},
            {'name': 'GPS Tracking', 'icon': '📍', 'description': 'Real-time GPS tracking'},
        ]
        
        amenities = []
        for data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=data['name'],
                defaults={'icon': data['icon'], 'description': data['description']}
            )
            amenities.append(amenity)
            if created:
                self.stdout.write(f'  ✓ Created amenity: {amenity.name}')
        
        return amenities

    def create_bus_operators(self):
        self.stdout.write('Creating bus operators...')
        operators_data = [
            {
                'name': 'Modern Coast',
                'contact_phone': '+254700000001',
                'contact_email': 'info@moderncoast.co.ke',
                'description': 'Leading bus operator in Kenya'
            },
            {
                'name': 'Easy Coach',
                'contact_phone': '+254700000002',
                'contact_email': 'info@easycoach.co.ke',
                'description': 'Affordable and reliable transport'
            },
            {
                'name': 'Mombasa Raha',
                'contact_phone': '+254700000003',
                'contact_email': 'info@mombasaraha.co.ke',
                'description': 'Premium travel experience'
            },
            {
                'name': 'Dreamline Express',
                'contact_phone': '+254700000004',
                'contact_email': 'info@dreamline.co.ke',
                'description': 'Your dream journey partner'
            },
            {
                'name': 'Guardian Coach',
                'contact_phone': '+254700000005',
                'contact_email': 'info@guardiancoach.co.ke',
                'description': 'Safe and comfortable travel'
            },
            {
                'name': 'Tahmeed Coach',
                'contact_phone': '+254700000006',
                'contact_email': 'info@tahmeed.co.ke',
                'description': 'Quality service since 1997'
            }
        ]
        
        operators = []
        for data in operators_data:
            operator, created = BusOperator.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            operators.append(operator)
            if created:
                self.stdout.write(f'  ✓ Created operator: {operator.name}')
        
        return operators

    def create_locations(self):
        self.stdout.write('Creating locations...')
        locations_data = [
            {'name': 'Nairobi', 'slug': 'nairobi', 'county': 'Nairobi'},
            {'name': 'Mombasa', 'slug': 'mombasa', 'county': 'Mombasa'},
            {'name': 'Kisumu', 'slug': 'kisumu', 'county': 'Kisumu'},
            {'name': 'Nakuru', 'slug': 'nakuru', 'county': 'Nakuru'},
            {'name': 'Eldoret', 'slug': 'eldoret', 'county': 'Uasin Gishu'},
            {'name': 'Machakos', 'slug': 'machakos', 'county': 'Machakos'},
            {'name': 'Kitui', 'slug': 'kitui', 'county': 'Kitui'},
            {'name': 'Thika', 'slug': 'thika', 'county': 'Kiambu'},
            {'name': 'Meru', 'slug': 'meru', 'county': 'Meru'},
            {'name': 'Nyeri', 'slug': 'nyeri', 'county': 'Nyeri'},
            {'name': 'Embu', 'slug': 'embu', 'county': 'Embu'},
            {'name': 'Malindi', 'slug': 'malindi', 'county': 'Kilifi'},
            {'name': 'Kisii', 'slug': 'kisii', 'county': 'Kisii'},
            {'name': 'Kakamega', 'slug': 'kakamega', 'county': 'Kakamega'},
        ]
        
        locations = {}
        for data in locations_data:
            location, created = Location.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            locations[data['name']] = location
            if created:
                self.stdout.write(f'  ✓ Created location: {location.name}')
        
        return locations

    def create_boarding_points(self, locations):
        self.stdout.write('Creating boarding points...')
        boarding_points_data = {
            'Nairobi': [
                {'name': 'Nairobi CBD Office', 'address': 'Accra Road, Nairobi', 'landmark': 'Near Nation Centre'},
                {'name': 'South C', 'address': 'Mombasa Road, South C', 'landmark': 'Near Shell Petrol Station'},
                {'name': 'Embakasi', 'address': 'Mombasa Road, Embakasi', 'landmark': 'Pipeline Area'},
                {'name': 'Westlands', 'address': 'Waiyaki Way, Westlands', 'landmark': 'Near Sarit Centre'},
            ],
            'Mombasa': [
                {'name': 'Mombasa Main Office', 'address': 'Moi Avenue, Mombasa', 'landmark': 'CBD'},
                {'name': 'Likoni', 'address': 'Likoni Ferry', 'landmark': 'Ferry Terminus'},
                {'name': 'Nyali', 'address': 'Links Road, Nyali', 'landmark': 'City Mall'},
            ],
            'Kisumu': [
                {'name': 'Kisumu CBD', 'address': 'Oginga Odinga Road', 'landmark': 'Near Main Bus Station'},
                {'name': 'Kisumu Airport Road', 'address': 'Airport Road', 'landmark': 'Near Airport'},
            ],
            'Nakuru': [
                {'name': 'Nakuru Town', 'address': 'Kenyatta Avenue', 'landmark': 'CBD'},
                {'name': 'Pipeline', 'address': 'Nakuru Pipeline', 'landmark': 'Industrial Area'},
            ],
            'Eldoret': [
                {'name': 'Eldoret CBD', 'address': 'Uganda Road', 'landmark': 'Main Matatu Stage'},
                {'name': 'Eldoret West', 'address': 'Eldoret-Kitale Road', 'landmark': 'West Eldoret'},
            ],
            'Machakos': [
                {'name': 'Machakos Town', 'address': 'Machakos CBD', 'landmark': 'Main Bus Park'},
            ],
            'Thika': [
                {'name': 'Thika Town', 'address': 'Thika Road', 'landmark': 'Main Stage'},
            ],
            'Meru': [
                {'name': 'Meru Town', 'address': 'Meru CBD', 'landmark': 'Bus Park'},
            ],
            'Malindi': [
                {'name': 'Malindi Town', 'address': 'Lamu Road', 'landmark': 'Main Stage'},
            ],
        }
        
        boarding_points = {}
        for location_name, points in boarding_points_data.items():
            if location_name in locations:
                location = locations[location_name]
                boarding_points[location_name] = []
                
                for point_data in points:
                    point, created = BoardingPoint.objects.get_or_create(
                        location=location,
                        name=point_data['name'],
                        defaults={
                            'address': point_data['address'],
                            'landmark': point_data['landmark']
                        }
                    )
                    boarding_points[location_name].append(point)
                    if created:
                        self.stdout.write(f'  ✓ Created boarding point: {point}')
        
        return boarding_points

    def get_seat_layout(self):
        self.stdout.write('Getting seat layout...')
        try:
            layout = SeatLayout.objects.get(name='Standard 38-Seater (Mixed Class)')
            self.stdout.write(f'  ✓ Using layout: {layout.name}')
            return layout
        except SeatLayout.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ Seat layout not found. Please run: python manage.py seed_layout'))
            raise

    def create_buses(self, operators, seat_layout, amenities):
        self.stdout.write('Creating buses...')
        buses_data = [
            {'operator': operators[0], 'reg': 'KBZ001A', 'name': 'Modern Express 1', 'type': 'luxury', 'rating': 4.5},
            {'operator': operators[0], 'reg': 'KBZ002B', 'name': 'Modern Express 2', 'type': 'luxury', 'rating': 4.3},
            {'operator': operators[1], 'reg': 'KCA003C', 'name': 'Easy Rider 1', 'type': 'standard', 'rating': 4.0},
            {'operator': operators[1], 'reg': 'KCA004D', 'name': 'Easy Rider 2', 'type': 'standard', 'rating': 4.2},
            {'operator': operators[2], 'reg': 'KCB005E', 'name': 'Raha Deluxe', 'type': 'vip', 'rating': 4.8},
            {'operator': operators[3], 'reg': 'KCC006F', 'name': 'Dream Cruiser', 'type': 'luxury', 'rating': 4.6},
            {'operator': operators[4], 'reg': 'KCD007G', 'name': 'Guardian Star', 'type': 'standard', 'rating': 4.1},
            {'operator': operators[5], 'reg': 'KCE008H', 'name': 'Tahmeed Elite', 'type': 'luxury', 'rating': 4.4},
        ]
        
        buses = []
        for data in buses_data:
            bus, created = Bus.objects.get_or_create(
                registration_number=data['reg'],
                defaults={
                    'operator': data['operator'],
                    'bus_name': data['name'],
                    'bus_type': data['type'],
                    'seat_layout': seat_layout,
                    'rating': Decimal(str(data['rating'])),
                    'total_ratings': 120
                }
            )
            
            # Add random amenities
            if created:
                if data['type'] == 'vip':
                    bus.amenities.set(amenities)  # VIP gets all amenities
                elif data['type'] == 'luxury':
                    bus.amenities.set(amenities[:7])  # Luxury gets most amenities
                else:
                    bus.amenities.set(amenities[:4])  # Standard gets basic amenities
                
                self.stdout.write(f'  ✓ Created bus: {bus.bus_name}')
            
            buses.append(bus)
        
        return buses

    def create_routes(self, locations):
        self.stdout.write('Creating routes...')
        routes_data = [
            {
                'origin': 'Nairobi', 'destination': 'Mombasa',
                'distance': 480, 'duration': timedelta(hours=8, minutes=30)
            },
            {
                'origin': 'Nairobi', 'destination': 'Kisumu',
                'distance': 350, 'duration': timedelta(hours=6, minutes=30)
            },
            {
                'origin': 'Nairobi', 'destination': 'Eldoret',
                'distance': 310, 'duration': timedelta(hours=5, minutes=30)
            },
            {
                'origin': 'Nairobi', 'destination': 'Nakuru',
                'distance': 160, 'duration': timedelta(hours=2, minutes=30)
            },
            {
                'origin': 'Nairobi', 'destination': 'Meru',
                'distance': 230, 'duration': timedelta(hours=4, minutes=0)
            },
            {
                'origin': 'Mombasa', 'destination': 'Malindi',
                'distance': 120, 'duration': timedelta(hours=2, minutes=0)
            },
            {
                'origin': 'Nakuru', 'destination': 'Eldoret',
                'distance': 150, 'duration': timedelta(hours=3, minutes=0)
            },
        ]
        
        routes = []
        for data in routes_data:
            route, created = Route.objects.get_or_create(
                origin=locations[data['origin']],
                destination=locations[data['destination']],
                defaults={
                    'distance_km': Decimal(str(data['distance'])),
                    'estimated_duration': data['duration']
                }
            )
            routes.append(route)
            if created:
                self.stdout.write(f'  ✓ Created route: {route}')
        
        return routes

    def create_route_stops(self, routes, boarding_points):
        self.stdout.write('Creating route stops...')
        
        # Define stops for Nairobi to Mombasa route
        nairobi_mombasa = routes[0]
        stops_data = [
            # Nairobi stops (pickup only)
            {'point': 'Nairobi', 'name': 'Nairobi CBD Office', 'order': 1, 'time': timedelta(hours=0), 'pickup': True, 'dropoff': False},
            {'point': 'Nairobi', 'name': 'South C', 'order': 2, 'time': timedelta(minutes=20), 'pickup': True, 'dropoff': False},
            {'point': 'Nairobi', 'name': 'Embakasi', 'order': 3, 'time': timedelta(minutes=40), 'pickup': True, 'dropoff': False},
            # Intermediate stops
            {'point': 'Machakos', 'name': 'Machakos Town', 'order': 4, 'time': timedelta(hours=1, minutes=30), 'pickup': True, 'dropoff': True},
            # Mombasa stops (dropoff only)
            {'point': 'Mombasa', 'name': 'Nyali', 'order': 5, 'time': timedelta(hours=8), 'pickup': False, 'dropoff': True},
            {'point': 'Mombasa', 'name': 'Mombasa Main Office', 'order': 6, 'time': timedelta(hours=8, minutes=30), 'pickup': False, 'dropoff': True},
        ]
        
        for stop_data in stops_data:
            if stop_data['point'] in boarding_points:
                point = next((p for p in boarding_points[stop_data['point']] if p.name == stop_data['name']), None)
                if point:
                    stop, created = RouteStop.objects.get_or_create(
                        route=nairobi_mombasa,
                        stop_order=stop_data['order'],
                        defaults={
                            'boarding_point': point,
                            'time_from_origin': stop_data['time'],
                            'is_pickup': stop_data['pickup'],
                            'is_dropoff': stop_data['dropoff']
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✓ Created route stop: {stop}')

    def create_trips(self, buses, routes):
        self.stdout.write('Creating trips...')
        trips = []
        
        # Create trips for the next 7 days
        today = timezone.now().date()
        
        # Nairobi to Mombasa trips (most popular route)
        nairobi_mombasa = routes[0]
        trip_times = [
            (time(6, 30), time(15, 0), 1800, 1500, 1400),  # Morning
            (time(8, 0), time(16, 30), 1800, 1500, 1400),
            (time(10, 0), time(18, 30), 1800, 1500, 1400),
            (time(14, 0), time(22, 30), 1800, 1500, 1400),
            (time(20, 0), time(4, 30), 2000, 1700, 1600),   # Night trip (more expensive)
        ]
        
        # Create trips ensuring unique (bus, date, time) combinations
        for day in range(7):
            date = today + timedelta(days=day)
            for time_idx, (dep_time, arr_time, vip_fare, bus_fare, norm_fare) in enumerate(trip_times):
                # Use modulo to cycle through buses, ensuring different bus for each time slot
                bus = buses[time_idx % len(buses)]
                
                trip, created = Trip.objects.get_or_create(
                    bus=bus,
                    departure_date=date,
                    departure_time=dep_time,
                    defaults={
                        'route': nairobi_mombasa,
                        'arrival_time': arr_time,
                        'base_fare_vip': Decimal(str(vip_fare)),
                        'base_fare_business': Decimal(str(bus_fare)),
                        'base_fare_normal': Decimal(str(norm_fare)),
                        'status': 'scheduled'
                    }
                )
                if created:
                    trips.append(trip)
                    self.stdout.write(f'  ✓ Created trip: {trip}')
        
        # Create trips for other routes (2 trips per day with different buses)
        for route_idx, route in enumerate(routes[1:4], start=1):  # Other popular routes
            for day in range(7):
                date = today + timedelta(days=day)
                for trip_num, hour in enumerate([7, 15]):  # Morning and afternoon
                    # Ensure unique bus selection for each route/time combination
                    bus_idx = (route_idx * 2 + day + trip_num) % len(buses)
                    bus = buses[bus_idx]
                    dep_time = time(hour, 0)
                    arr_time = time((hour + 6) % 24, 0)
                    
                    trip, created = Trip.objects.get_or_create(
                        bus=bus,
                        departure_date=date,
                        departure_time=dep_time,
                        defaults={
                            'route': route,
                            'arrival_time': arr_time,
                            'base_fare_vip': Decimal('1500'),
                            'base_fare_business': Decimal('1200'),
                            'base_fare_normal': Decimal('1000'),
                            'status': 'scheduled'
                        }
                    )
                    if created:
                        trips.append(trip)
        
        self.stdout.write(f'  ✓ Created {len(trips)} trips total')
        return trips

    def create_seats_for_trips(self, trips):
        self.stdout.write('Creating seats for trips...')
        total_seats = 0
        
        for trip in trips:
            layout_config = trip.bus.seat_layout.layout_config
            
            for row_data in layout_config['rows']:
                row_number = row_data['row']
                
                for seat_data in row_data['seats']:
                    seat, created = Seat.objects.get_or_create(
                        trip=trip,
                        seat_number=seat_data['number'],
                        defaults={
                            'row_number': row_number,
                            'seat_class': seat_data['class'],
                            'position': seat_data['type'],
                            'is_available': True
                        }
                    )
                    if created:
                        total_seats += 1
        
        self.stdout.write(f'  ✓ Created {total_seats} seats across all trips')

    def print_summary(self):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Database Seeding Summary'))
        self.stdout.write('='*60)
        self.stdout.write(f'Bus Operators: {BusOperator.objects.count()}')
        self.stdout.write(f'Amenities: {Amenity.objects.count()}')
        self.stdout.write(f'Buses: {Bus.objects.count()}')
        self.stdout.write(f'Locations: {Location.objects.count()}')
        self.stdout.write(f'Boarding Points: {BoardingPoint.objects.count()}')
        self.stdout.write(f'Routes: {Route.objects.count()}')
        self.stdout.write(f'Route Stops: {RouteStop.objects.count()}')
        self.stdout.write(f'Trips: {Trip.objects.count()}')
        self.stdout.write(f'Seats: {Seat.objects.count()}')
        self.stdout.write(f'Seat Layouts: {SeatLayout.objects.count()} (preserved)')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\nYou can now start using the application!'))