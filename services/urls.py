from django.urls import path
from .views import ServiceListView, ServiceDetailView

urlpatterns = [
    path('', ServiceListView.as_view(), name='services'),
    path('category/<slug:category_slug>/', ServiceListView.as_view(), name='services_by_category'),
    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
]
