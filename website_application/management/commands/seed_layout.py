# website_application/management/commands/seed_layout.py

from django.core.management.base import BaseCommand
from website_application.models import SeatLayout


class Command(BaseCommand):
    help = 'Creates seat layouts for buses based on the provided image'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating seat layouts...')
        
        # Define the exact layout from the image
        # Row structure: row_number, seats with their positions and classes
        layout_config = {
            "door_position": "front-left",
            "rows": [
                # Row 1 - Door row (VIP seat on right)
                {
                    "row": 1,
                    "seats": [
                        {"number": "1", "position": "A", "class": "vip", "type": "aisle"}
                    ]
                },
                # Row 2 - Normal row
                {
                    "row": 2,
                    "seats": [
                        {"number": "2", "position": "A", "class": "business", "type": "window"},
                        {"number": "3", "position": "B", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 3
                {
                    "row": 3,
                    "seats": [
                        {"number": "4", "position": "A", "class": "business", "type": "window"},
                        {"number": "5", "position": "B", "class": "business", "type": "middle"},
                        {"number": "6", "position": "C", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 4
                {
                    "row": 4,
                    "seats": [
                        {"number": "7", "position": "A", "class": "business", "type": "window"},
                        {"number": "8", "position": "B", "class": "business", "type": "middle"},
                        {"number": "9", "position": "C", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 5
                {
                    "row": 5,
                    "seats": [
                        {"number": "10", "position": "A", "class": "business", "type": "window"},
                        {"number": "11", "position": "B", "class": "business", "type": "middle"},
                        {"number": "12", "position": "C", "class": "business", "type": "aisle"},
                        {"number": "13", "position": "D", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 6
                {
                    "row": 6,
                    "seats": [
                        {"number": "14", "position": "A", "class": "business", "type": "window"},
                        {"number": "15", "position": "B", "class": "business", "type": "middle"},
                        {"number": "16", "position": "C", "class": "business", "type": "aisle"},
                        {"number": "17", "position": "D", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 7
                {
                    "row": 7,
                    "seats": [
                        {"number": "18", "position": "A", "class": "business", "type": "window"},
                        {"number": "19", "position": "B", "class": "business", "type": "middle"},
                        {"number": "20", "position": "C", "class": "business", "type": "aisle"},
                        {"number": "21", "position": "D", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 8
                {
                    "row": 8,
                    "seats": [
                        {"number": "22", "position": "A", "class": "business", "type": "window"},
                        {"number": "23", "position": "B", "class": "business", "type": "middle"},
                        {"number": "24", "position": "C", "class": "business", "type": "aisle"},
                        {"number": "25", "position": "D", "class": "business", "type": "aisle"}
                    ]
                },
                # Row 9
                {
                    "row": 9,
                    "seats": [
                        {"number": "26", "position": "A", "class": "business", "type": "window"},
                        {"number": "27", "position": "B", "class": "normal", "type": "middle"},
                        {"number": "28", "position": "C", "class": "normal", "type": "aisle"},
                        {"number": "29", "position": "D", "class": "normal", "type": "aisle"}
                    ]
                },
                # Row 10
                {
                    "row": 10,
                    "seats": [
                        {"number": "30", "position": "A", "class": "normal", "type": "window"},
                        {"number": "31", "position": "B", "class": "normal", "type": "middle"},
                        {"number": "32", "position": "C", "class": "normal", "type": "aisle"},
                        {"number": "33", "position": "D", "class": "normal", "type": "aisle"}
                    ]
                },
                # Row 11 - Back row with 3 seats
                {
                    "row": 11,
                    "seats": [
                        {"number": "34", "position": "A", "class": "normal", "type": "window"},
                        {"number": "35", "position": "B", "class": "normal", "type": "middle"},
                        {"number": "36", "position": "C", "class": "normal", "type": "aisle"},
                        {"number": "37", "position": "D", "class": "normal", "type": "aisle"},
                        {"number": "38", "position": "E", "class": "normal", "type": "window"}
                    ]
                }
            ]
        }
        
        # Create the seat layout
        layout, created = SeatLayout.objects.update_or_create(
            name='Standard 38-Seater (Mixed Class)',
            defaults={
                'total_rows': 11,
                'seats_per_row': 4,  # Average, actual varies by row
                'total_seats': 38,
                'layout_config': layout_config
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created layout: {layout.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated layout: {layout.name}'))
        
        # Display layout summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Layout Summary:'))
        self.stdout.write('='*60)
        self.stdout.write(f'Name: {layout.name}')
        self.stdout.write(f'Total Seats: {layout.total_seats}')
        self.stdout.write(f'Total Rows: {layout.total_rows}')
        
        # Count seats by class
        vip_count = sum(1 for row in layout_config['rows'] for seat in row['seats'] if seat['class'] == 'vip')
        business_count = sum(1 for row in layout_config['rows'] for seat in row['seats'] if seat['class'] == 'business')
        normal_count = sum(1 for row in layout_config['rows'] for seat in row['seats'] if seat['class'] == 'normal')
        
        self.stdout.write(f'\nSeat Distribution:')
        self.stdout.write(f'  VIP: {vip_count} seat(s)')
        self.stdout.write(f'  Business: {business_count} seats')
        self.stdout.write(f'  Normal/Economy: {normal_count} seats')
        self.stdout.write('='*60)
        
        # Create additional common layouts
        self.create_additional_layouts()
        
        self.stdout.write(self.style.SUCCESS('\n✓ All layouts created successfully!'))

    def create_additional_layouts(self):
        """Create additional common bus layouts"""
        
        # 2x2 Standard 44-Seater
        standard_44_config = {
            "door_position": "front-left",
            "rows": []
        }
        
        seat_num = 1
        for row in range(1, 12):
            row_data = {"row": row, "seats": []}
            
            # 4 seats per row (2x2 configuration)
            positions = ["A", "B", "C", "D"]
            types = ["window", "aisle", "aisle", "window"]
            
            for i in range(4):
                seat_class = "vip" if row <= 2 else ("business" if row <= 6 else "normal")
                row_data["seats"].append({
                    "number": str(seat_num),
                    "position": positions[i],
                    "class": seat_class,
                    "type": types[i]
                })
                seat_num += 1
            
            standard_44_config["rows"].append(row_data)
        
        SeatLayout.objects.update_or_create(
            name='Standard 44-Seater (2x2)',
            defaults={
                'total_rows': 11,
                'seats_per_row': 4,
                'total_seats': 44,
                'layout_config': standard_44_config
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Created layout: Standard 44-Seater (2x2)'))
        
        # VIP 28-Seater (2x1 configuration)
        vip_28_config = {
            "door_position": "front-right",
            "rows": []
        }
        
        seat_num = 1
        for row in range(1, 15):
            row_data = {"row": row, "seats": []}
            
            # 2 seats per row (2x1 configuration - more spacious)
            positions = ["A", "B"]
            types = ["window", "aisle"]
            
            for i in range(2):
                row_data["seats"].append({
                    "number": str(seat_num),
                    "position": positions[i],
                    "class": "vip",
                    "type": types[i]
                })
                seat_num += 1
            
            vip_28_config["rows"].append(row_data)
        
        SeatLayout.objects.update_or_create(
            name='VIP 28-Seater (2x1)',
            defaults={
                'total_rows': 14,
                'seats_per_row': 2,
                'total_seats': 28,
                'layout_config': vip_28_config
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Created layout: VIP 28-Seater (2x1)'))
        
        # Economy 51-Seater (2x3 configuration)
        economy_51_config = {
            "door_position": "front-left",
            "rows": []
        }
        
        seat_num = 1
        for row in range(1, 11):
            row_data = {"row": row, "seats": []}
            
            # 5 seats per row (2x3 configuration)
            positions = ["A", "B", "C", "D", "E"]
            types = ["window", "aisle", "middle", "aisle", "window"]
            
            for i in range(5):
                row_data["seats"].append({
                    "number": str(seat_num),
                    "position": positions[i],
                    "class": "normal",
                    "type": types[i]
                })
                seat_num += 1
            
            economy_51_config["rows"].append(row_data)
        
        # Add last row with 1 seat
        economy_51_config["rows"].append({
            "row": 11,
            "seats": [{"number": "51", "position": "A", "class": "normal", "type": "aisle"}]
        })
        
        SeatLayout.objects.update_or_create(
            name='Economy 51-Seater (2x3)',
            defaults={
                'total_rows': 11,
                'seats_per_row': 5,
                'total_seats': 51,
                'layout_config': economy_51_config
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Created layout: Economy 51-Seater (2x3)'))