from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.home_view, name='home'),
    path('search/', views.search_results_view, name='search_results'),
    
    # AJAX API endpoints
    path('api/autocomplete/', views.api_autocomplete_locations, name='api_autocomplete'),
    path('api/search-trips/', views.api_search_trips, name='api_search_trips'),
    path('api/trips/<int:trip_id>/seats/', views.api_get_seats, name='api_get_seats'),
    path('api/trips/<int:trip_id>/boarding-points/', views.api_get_boarding_points, name='api_boarding_points'),
    path('api/seats/lock/', views.api_lock_seat, name='api_lock_seat'),
    path('api/seats/unlock/', views.api_unlock_seat, name='api_unlock_seat'),
    path('api/calculate-total/', views.api_calculate_total, name='api_calculate_total'),
    path('api/create-booking/', views.api_create_booking, name='api_create_booking'),
]
