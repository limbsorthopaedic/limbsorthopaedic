from django.urls import path
from . import views

app_name = 'limbs_cyber'

urlpatterns = [
    path('', views.cyber_pos_dashboard, name='cyber_pos_dashboard'),
    path('create-sale/', views.create_sale, name='cyber_create_sale'),
    path('daily-report/', views.daily_report, name='cyber_daily_report'),
    path('daily-report/<str:date>/', views.daily_report, name='cyber_daily_report_date'),
    path('daily-report/<str:date>/pdf/', views.daily_report_pdf, name='cyber_daily_report_pdf'),
    path('period-report/<str:period_type>/', views.period_report, name='cyber_period_report'),
    path('period-report/<str:period_type>/pdf/', views.period_report_pdf, name='cyber_period_report_pdf'),
    path('delete-sale/<int:sale_id>/', views.delete_sale, name='cyber_delete_sale'),
    path('sale/<int:sale_id>/', views.sale_detail, name='cyber_sale_detail'),
    path('all-sales/', views.all_sales, name='cyber_all_sales'),
    path('receipt/<int:sale_id>/', views.generate_receipt, name='cyber_generate_receipt'),
]