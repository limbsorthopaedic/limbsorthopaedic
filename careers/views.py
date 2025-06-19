from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Career, CareerApplication
from .forms import CareerApplicationForm

def career_list(request):
    careers = Career.objects.filter(is_active=True)
    return render(request, 'careers/careers.html', {
        'careers': careers
    })

def job_application(request, career_id):
    career = get_object_or_404(Career, id=career_id, is_active=True)
    return render(request, 'careers/job_application.html', {
        'career': career
    })

def submit_application(request):
    if request.method == 'POST':
        form = CareerApplicationForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                application = form.save()

                try:
                    # Send confirmation email
                    context = {'application': application}
                    subject = 'Application Received - LIMBS Orthopaedic'
                    html_message = render_to_string('careers/email/application_confirmation.html', context)
                    send_mail(
                        subject,
                        '',
                        settings.DEFAULT_FROM_EMAIL,
                        [application.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")
                    messages.warning(request, 'Your application was submitted, but there was an issue sending the confirmation email.')

                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('careers:success')
            else:
                print("Form errors:", form.errors)
                messages.error(request, 'Please check your form inputs and try again.')
                return redirect('careers:job_application', career_id=request.POST.get('career'))
        except Exception as e:
            print(f"Error saving application: {e}")
            messages.error(request, 'There was an error processing your application. Please try again.')
            return redirect('careers:job_application', career_id=request.POST.get('career'))

    messages.error(request, 'Invalid request method.')
    return redirect('careers:career_list')

def success(request):
    return render(request, 'careers/success.html')

def career_success(request):
    return render(request, 'careers/success.html')