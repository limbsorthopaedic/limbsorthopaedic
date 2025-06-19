from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Avg, F
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from .models import Survey, Question, Response, Answer
from .forms import DynamicSurveyForm
from appointments.models import Appointment
from core.models import SocialMedia


def survey_list(request):
    """Display list of active surveys available to the user"""
    surveys = Survey.objects.filter(is_active=True).annotate(
        question_count=Count('questions'),
        response_count=Count('responses', distinct=True)
    )

    # Get completed surveys for this user to avoid showing them again
    completed_survey_ids = []
    if request.user.is_authenticated:
        completed_survey_ids = Response.objects.filter(
            user=request.user,
            is_complete=True
        ).values_list('survey_id', flat=True)

    context = {
        'surveys': surveys,
        'completed_survey_ids': completed_survey_ids,
        'page_title': _('Patient Feedback Surveys'),
        'social_media': SocialMedia.objects.filter(is_active=True)
    }
    return render(request, 'surveys/survey_list.html', context)


def survey_detail(request, survey_id):
    """Display a specific survey and its description"""
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)

    # Check if this is an update request
    is_update = request.session.get('is_update', False)

    # Check if user has already completed this survey
    user_completed = False
    if request.user.is_authenticated and not is_update:
        user_completed = Response.objects.filter(
            survey=survey,
            user=request.user,
            is_complete=True
        ).exists()

    # Initialize response and questions
    active_response = None
    questions = None
    active_response_id = request.session.get('active_response_id')

    if active_response_id:
        try:
            active_response = Response.objects.get(id=active_response_id, survey=survey, is_complete=False)
            questions = survey.questions.all().order_by('order')
        except Response.DoesNotExist:
            # Clear invalid session
            if 'active_response_id' in request.session:
                del request.session['active_response_id']

    context = {
        'survey': survey,
        'user_completed': user_completed,
        'active_response': active_response,
        'questions': questions,
        'question_count': survey.questions.count(),
        'page_title': survey.title,
        'social_media': SocialMedia.objects.filter(is_active=True)
    }
    return render(request, 'surveys/survey_detail.html', context)


def start_survey(request, survey_id):
    """Initialize a new survey response and redirect to the survey form"""
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)

    # Check for existing incomplete response in session
    active_response_id = request.session.get('active_response_id')
    if active_response_id:
        try:
            # Verify the response exists and is for this survey
            response = Response.objects.get(id=active_response_id, survey=survey, is_complete=False)
            return redirect('surveys:survey_detail', survey_id=survey_id)
        except Response.DoesNotExist:
            # Clear invalid session data
            if 'active_response_id' in request.session:
                del request.session['active_response_id']

    # Create a new response object
    response = Response(
        survey=survey,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    response.save()

    # Store response ID in session
    request.session['active_response_id'] = response.id
    request.session.modified = True

    return redirect('surveys:survey_detail', survey_id=survey_id)


@require_POST
def submit_answer(request):
    """AJAX endpoint to submit individual answers as the user progresses"""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("AJAX requests only")

    response_id = request.session.get('active_response_id')
    if not response_id:
        return JsonResponse({'error': 'No active survey session'}, status=400)

    try:
        response = Response.objects.get(id=response_id)
        question_id = request.POST.get('question_id')
        answer_value = request.POST.get('answer')

        question = Question.objects.get(id=question_id)

        # Create or update the answer
        answer, created = Answer.objects.update_or_create(
            response=response,
            question=question,
            defaults=_get_answer_fields(question.question_type, answer_value)
        )

        return JsonResponse({
            'success': True,
            'message': _('Answer saved')
        })

    except (Response.DoesNotExist, Question.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=400)


def _get_answer_fields(question_type, value):
    """Helper method to get the appropriate field values based on question type"""
    fields = {
        'text_answer': None,
        'choice_answer': None,
        'rating_answer': None,
        'boolean_answer': None,
    }

    if question_type == 'text':
        fields['text_answer'] = value
    elif question_type in ('multiple_choice', 'single_choice'):
        fields['choice_answer'] = value
    elif question_type in ('rating', 'emoji'):
        fields['rating_answer'] = int(value) if value.isdigit() else None
    elif question_type == 'yes_no':
        fields['boolean_answer'] = value.lower() == 'true'

    return fields


@require_POST
def submit_survey(request, survey_id):
    """Process the survey submission and mark it as complete"""
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)

    response_id = request.session.get('active_response_id')
    if not response_id:
        messages.error(request, _('Survey session expired or invalid.'))
        return redirect('surveys:survey_list')

    try:
        response = Response.objects.get(id=response_id)

        # Process all form data
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                try:
                    question = Question.objects.get(id=question_id, survey=survey)

                    # Create or update answer
                    answer, created = Answer.objects.update_or_create(
                        response=response,
                        question=question,
                        defaults=_get_answer_fields(question.question_type, value)
                    )
                except Question.DoesNotExist:
                    pass

        # Mark response as complete
        response.complete()

        # Clear the session variables
        if 'active_response_id' in request.session:
            del request.session['active_response_id']
        if 'is_update' in request.session:
            del request.session['is_update']

        # Send thank you email
        try:
            _send_thank_you_email(request, response)
        except Exception as e:
            logger.exception(f"Error sending thank you email: {e}")

        # Redirect to thank you page
        return redirect('surveys:thank_you', survey_id=survey_id)

    except Response.DoesNotExist:
        messages.error(request, _('Invalid survey response.'))
        return redirect('surveys:survey_list')


def _send_thank_you_email(request, response):
    """Sends a thank you email after survey completion."""
    if response.user and response.user.email:  # Only send if we have a user with email
        subject = 'Thank you for your feedback!'
        html_message = render_to_string('surveys/email/survey_thank_you.html', {'response': response})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [response.user.email]

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


def thank_you(request, survey_id):
    """Display thank you page after survey completion"""
    survey = get_object_or_404(Survey, pk=survey_id)

    context = {
        'survey': survey,
        'page_title': _('Thank You'),
        'social_media': SocialMedia.objects.filter(is_active=True)
    }
    return render(request, 'surveys/thank_you.html', context)


def get_survey_questions(request, survey_id):
    """AJAX endpoint to get survey questions in JSON format"""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("AJAX requests only")

    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)
    questions = survey.questions.all().order_by('order')

    questions_data = []
    for question in questions:
        question_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'required': question.required,
            'order': question.order
        }

        if question.question_type in ('single_choice', 'multiple_choice'):
            question_data['choices'] = question.get_choices_list()

        questions_data.append(question_data)

    return JsonResponse({
        'survey_id': survey.id,
        'title': survey.title,
        'description': survey.description,
        'questions': questions_data,
        'show_progress': survey.show_progress
    })


@login_required
def appointment_survey(request, appointment_id):
    """Display survey specifically for an appointment"""
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    # Security check - only allow access to the patient who had the appointment
    if request.user != appointment.user and not request.user.is_staff:
        messages.error(request, _('You do not have permission to access this survey.'))
        return redirect('accounts:profile')

    # Get satisfaction survey type
    try:
        survey = Survey.objects.get(survey_type='satisfaction', is_active=True)
    except Survey.DoesNotExist:
        messages.warning(request, _('No feedback survey is currently available.'))
        return redirect('accounts:profile')

    # Check if user has already completed this survey for this appointment
    already_completed = Response.objects.filter(
        survey=survey,
        user=request.user,
        appointment_id=appointment_id,
        is_complete=True
    ).exists()

    if already_completed:
        messages.info(request, _('You have already completed a feedback survey for this appointment.'))
        return redirect('accounts:profile')

    # Create a new response linked to this appointment
    response = Response(
        survey=survey,
        user=request.user,
        appointment_id=appointment_id,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    response.save()

    # Store response ID in session
    request.session['active_response_id'] = response.id

    context = {
        'survey': survey,
        'appointment': appointment,
        'page_title': _('Appointment Feedback'),
        'social_media': SocialMedia.objects.filter(is_active=True)
    }
    return render(request, 'surveys/appointment_survey.html', context)


@login_required
def update_survey(request, survey_id):
    """Allow users to update their previous survey responses"""
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)

    # Get user's previous response
    previous_response = Response.objects.filter(
        survey=survey,
        user=request.user,
        is_complete=True
    ).order_by('-completed_at').first()

    if not previous_response:
        messages.error(request, _('No previous response found for this survey.'))
        return redirect('surveys:survey_list')

    # Create a new response with previous answers
    new_response = Response.objects.create(
        survey=survey,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    # Copy previous answers
    for answer in previous_response.answers.all():
        Answer.objects.create(
            response=new_response,
            question=answer.question,
            text_answer=answer.text_answer,
            choice_answer=answer.choice_answer,
            rating_answer=answer.rating_answer,
            boolean_answer=answer.boolean_answer
        )

    # Store new response ID and update flag in session
    request.session['active_response_id'] = new_response.id
    request.session['is_update'] = True
    request.session.modified = True

    return redirect('surveys:survey_detail', survey_id=survey_id)