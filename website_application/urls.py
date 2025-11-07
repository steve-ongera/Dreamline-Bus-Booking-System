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

    #admin views
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Bus URLs
    path('buses/', views.bus_list, name='bus_list'),
    path('buses/add/', views.bus_form, name='bus_add'),
    path('buses/<int:pk>/', views.bus_detail, name='bus_detail'),
    path('buses/<int:pk>/edit/', views.bus_form, name='bus_edit'),
    path('buses/<int:pk>/delete/', views.bus_delete, name='bus_delete'),
    path('buses/<int:pk>/toggle-status/', views.bus_toggle_status, name='bus_toggle_status'),
    
    # Operator URLs
    path('operators/', views.operator_list, name='operator_list'),
    path('operators/add/', views.operator_form, name='operator_add'),
    path('operators/<int:pk>/', views.operator_detail, name='operator_detail'),
    path('operators/<int:pk>/edit/', views.operator_form, name='operator_edit'),
    path('operators/<int:pk>/delete/', views.operator_delete, name='operator_delete'),
    
    # Seat Layout URLs
    path('layouts/', views.layout_list, name='layout_list'),
    path('layouts/add/', views.layout_form, name='layout_add'),
    path('layouts/<int:pk>/', views.layout_detail, name='layout_detail'),
    path('layouts/<int:pk>/edit/', views.layout_form, name='layout_edit'),
    path('layouts/<int:pk>/delete/', views.layout_delete, name='layout_delete'),
    
    # AJAX/API URLs
    path('buses/layout/<int:pk>/preview/', views.get_layout_preview, name='layout_preview'),
    
]
