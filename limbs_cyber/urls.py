
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cyber_pos_dashboard, name='cyber_pos_dashboard'),
    path('sale/create/', views.create_sale, name='cyber_create_sale'),
    path('sale/<int:sale_id>/', views.sale_detail, name='cyber_sale_detail'),
    path('sale/<int:sale_id>/delete/', views.delete_sale, name='cyber_delete_sale'),
    path('sales/all/', views.all_sales, name='cyber_all_sales'),
    path('report/daily/', views.daily_report, name='cyber_daily_report_today'),
    path('report/daily/<str:date>/', views.daily_report, name='cyber_daily_report'),
    path('report/daily/<str:date>/pdf/', views.daily_report_pdf, name='cyber_daily_report_pdf'),
    path('report/period/<str:period_type>/', views.period_report, name='cyber_period_report'),
    path('report/period/<str:period_type>/pdf/', views.period_report_pdf, name='cyber_period_report_pdf'),
    path('receipt/<int:sale_id>/', views.generate_receipt, name='cyber_generate_receipt'),
]
