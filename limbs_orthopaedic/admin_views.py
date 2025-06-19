from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
import json

from accounts.models import Doctor, Profile
from analytics.models import PageVisit
from appointments.models import Appointment
from blog.models import BlogPost, BlogCategory, Comment
from products.models import CustomProductRequest, Product
from core.models import Contact
from surveys.models import Survey, Response, Question, Answer
from services.models import Service
from gallery.models import Gallery 
from staff_chat.models import StaffChatMessage
from testimonials.models import Testimonial
from careers.models import Career, CareerApplication
from django.utils import timezone
from datetime import datetime

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view with statistics and recent data"""

    # Get time filter from query params
    time_filter = request.GET.get('time_filter', 'all')

    # Define date range based on filter
    now = timezone.now()
    if time_filter == 'year':
        start_date = now - timedelta(days=365)
    elif time_filter == 'month':
        start_date = now - timedelta(days=30)
    elif time_filter == 'week':
        start_date = now - timedelta(days=7)
    elif time_filter == 'day':
        start_date = now - timedelta(days=1)
    else:
        start_date = None  # All time

    # Base querysets - can be filtered by date later
    users_qs = User.objects.all()
    appointments_qs = Appointment.objects.all()
    surveys_qs = Response.objects.filter(is_complete=True)

    # Apply date filters if needed
    if start_date:
        users_qs = users_qs.filter(date_joined__gte=start_date)
        appointments_qs = appointments_qs.filter(preferred_date__gte=start_date)
        surveys_qs = surveys_qs.filter(completed_at__gte=start_date)

    # Get staff messages count

    # Get counts for statistics
    total_users = User.objects.count()  # All registered users
    doctor_count = Doctor.objects.count()  # Count all doctors
    appointment_count = appointments_qs.count()
    blog_count = BlogPost.objects.count()
    blog_comments_count = Comment.objects.count()  # Count blog comments
    survey_count = Survey.objects.count()  # Count all surveys
    surveys_done_count = surveys_qs.count()  # Count completed surveys
    service_count = Service.objects.count()  # Count services
    contact_count = Contact.objects.count()  # Count contact requests
    testimonial_count = Testimonial.objects.count()  # Count testimonials
    
    # Get career statistics
    careers = Career.objects.filter(is_active=True)
    now = timezone.now()
    for career in careers:
        career.applications_this_month = CareerApplication.objects.filter(
            career=career,
            created_at__year=now.year,
            created_at__month=now.month
        ).count()
        career.applications_this_year = CareerApplication.objects.filter(
            career=career,
            created_at__year=now.year
        ).count()
        career.total_applications = CareerApplication.objects.filter(career=career).count()
    product_count = Product.objects.filter(is_active=True).count()  # Count active products
    product_inquiry_count = CustomProductRequest.objects.count()  # Count product inquiries
    gallery_count = Gallery.objects.filter(is_active=True).count()  # Count active gallery items
    male_users = Profile.objects.filter(gender='M').count()
    female_users = Profile.objects.filter(gender='F').count()
    gender_users = male_users + female_users  # Users who have set their gender
    staff_messages_count = StaffChatMessage.objects.count()  # Count staff messages


    # Get recent appointments
    recent_appointments = appointments_qs.order_by('-preferred_date')[:5]

    # Get doctors
    doctors = Doctor.objects.filter(is_active=True)[:5]

    # Get recent blog posts
    recent_blog_posts = BlogPost.objects.all().order_by('-published_date')[:5]

    # Get recent custom product requests
    recent_custom_product_requests = CustomProductRequest.objects.all().order_by('-created_at')[:5]

    # Get recent contact messages
    recent_contact_messages = Contact.objects.all().order_by('-created_at')[:5]

    # Get recent survey responses
    recent_survey_responses = Response.objects.filter(is_complete=True).order_by('-completed_at')[:5]

    # Prepare data for visualizations
    # 1. Appointments by month
    appointments_by_month = []

    # Get months data
    month_data = appointments_qs.annotate(
        month=TruncMonth('preferred_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            appointments_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 2. Survey responses by month
    surveys_by_month = []

    # Get survey response data by month
    survey_month_data = surveys_qs.annotate(
        month=TruncMonth('completed_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in survey_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            surveys_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 3. Custom Products by month
    # Using the already imported CustomProductRequest from line 15
    custom_products_qs = CustomProductRequest.objects.all()
    if start_date:
        custom_products_qs = custom_products_qs.filter(created_at__gte=start_date)

    custom_products_by_month = []
    custom_products_month_data = custom_products_qs.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in custom_products_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            custom_products_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 4. Testimonials by month
    testimonials_qs = Testimonial.objects.all()
    if start_date:
        testimonials_qs = testimonials_qs.filter(created_at__gte=start_date)

    testimonials_by_month = []
    testimonials_month_data = testimonials_qs.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in testimonials_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            testimonials_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 5. Contact messages by month
    # Using the already imported Contact from line 16
    contacts_qs = Contact.objects.all()
    if start_date:
        contacts_qs = contacts_qs.filter(created_at__gte=start_date)

    contacts_by_month = []
    contacts_month_data = contacts_qs.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in contacts_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            contacts_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 6. User registrations by month
    # Using the already imported User model from line 4
    users_reg_qs = User.objects.all()
    if start_date:
        users_reg_qs = users_reg_qs.filter(date_joined__gte=start_date)

    users_by_month = []
    users_month_data = users_reg_qs.annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in users_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            users_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 7. Blog posts by month
    # Using the already imported BlogPost and Comment models from line 14
    blogs_qs = BlogPost.objects.all()
    if start_date:
        blogs_qs = blogs_qs.filter(published_date__gte=start_date)

    blogs_by_month = []
    blogs_month_data = blogs_qs.annotate(
        month=TruncMonth('published_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in blogs_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            blogs_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # 8. Blog comments by month
    comments_qs = Comment.objects.all()
    if start_date:
        comments_qs = comments_qs.filter(created_date__gte=start_date)

    comments_by_month = []
    comments_month_data = comments_qs.annotate(
        month=TruncMonth('created_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    for data in comments_month_data:
        if data['month']:
            month_name = data['month'].strftime('%b %Y')
            comments_by_month.append({
                'month': month_name,
                'count': data['count']
            })

    # Prepare chart data as JSON
    chart_data = {
        'appointments_by_month': json.dumps(appointments_by_month),
        'surveys_by_month': json.dumps(surveys_by_month),
        'custom_products_by_month': json.dumps(custom_products_by_month),
        'testimonials_by_month': json.dumps(testimonials_by_month),
        'contacts_by_month': json.dumps(contacts_by_month),
        'users_by_month': json.dumps(users_by_month),
        'blogs_by_month': json.dumps(blogs_by_month),
        'comments_by_month': json.dumps(comments_by_month),
    }

    # Get visit statistics
    visit_counts = PageVisit.get_visit_counts()
    
    context = {
        'visit_counts': visit_counts,
        'total_users': total_users,
        'male_users': male_users,
        'female_users': female_users,
        'doctor_count': doctor_count,
        'appointment_count': appointment_count,
        'blog_count': blog_count,
        'blog_comments_count': blog_comments_count,
        'survey_count': survey_count,
        'surveys_done_count': surveys_done_count,
        'service_count': service_count,
        'contact_count': contact_count,
        'testimonial_count': testimonial_count,
        'product_count': product_count,
        'product_inquiry_count': product_inquiry_count,
        'gallery_count': gallery_count,
        'staff_messages_count': staff_messages_count,
        'recent_appointments': recent_appointments,
        'doctors': doctors,
        'careers': careers,
        'recent_blog_posts': recent_blog_posts,
        'recent_custom_product_requests': recent_custom_product_requests,
        'recent_contact_messages': recent_contact_messages,
        'recent_survey_responses': recent_survey_responses,
        'chart_data': chart_data,
        'time_filter': time_filter,
    }

    return render(request, 'admin/dashboard.html', context)


@require_POST
def admin_logout_view(request):
    """Custom admin logout view that redirects to homepage"""
    logout(request)
    return redirect('/')