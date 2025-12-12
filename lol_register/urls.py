from django.urls import path
from . import views

app_name = 'lol_register'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    
    # Visits
    path('visits/', views.visit_list, name='visit_list'),
    path('visits/create/', views.visit_create_step1, name='visit_create_step1'),
    path('visits/create/<int:patient_id>/', views.visit_create_step2, name='visit_create_step2'),
    path('visits/<int:pk>/', views.visit_detail, name='visit_detail'),
    path('visits/<int:pk>/clinician/', views.visit_update_clinician, name='visit_update_clinician'),
    
    # Visit Products
    path('visits/<int:visit_id>/products/', views.visit_products_list, name='visit_products_list'),
    path('visits/<int:visit_id>/products/add/', views.visit_product_add, name='visit_product_add'),
    path('visit-products/<int:pk>/update/', views.visit_product_update, name='visit_product_update'),
    path('visit-products/<int:pk>/delete/', views.visit_product_delete, name='visit_product_delete'),
    
    # Payments (Cash Book)
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/create/<int:visit_id>/', views.payment_create_for_visit, name='payment_create_for_visit'),
    path('payments/<int:pk>/edit/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    
    # Workshop Orders
    path('workshop/', views.workshop_list, name='workshop_list'),
    path('workshop/create/', views.workshop_create, name='workshop_create'),
    path('workshop/create/<int:visit_product_id>/', views.workshop_create_for_product, name='workshop_create_for_product'),
    path('workshop/<int:pk>/', views.workshop_detail, name='workshop_detail'),
    path('workshop/<int:pk>/edit/', views.workshop_update, name='workshop_update'),
    
    # Exports
    path('export/visits/', views.export_visits, name='export_visits'),
    path('export/payments/', views.export_payments, name='export_payments'),
    path('export/products/', views.export_products, name='export_products'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # API endpoints for AJAX
    path('api/patient-search/', views.api_patient_search, name='api_patient_search'),
    path('api/product-price/<int:product_id>/', views.api_product_price, name='api_product_price'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
