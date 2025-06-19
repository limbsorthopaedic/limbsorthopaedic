from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('example/', TemplateView.as_view(template_name='example_content_usage.html'), name='content_example'),
]