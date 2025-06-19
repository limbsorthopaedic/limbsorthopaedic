from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from surveys.models import Survey, Question


class Command(BaseCommand):
    help = 'Creates predefined survey templates for common feedback use cases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force create even if templates already exist',
        )

    def handle(self, *args, **options):
        # Check if we already have survey templates
        if Survey.objects.exists() and not options['force']:
            self.stdout.write(self.style.WARNING(
                'Survey templates already exist. Use --force to recreate them.'
            ))
            return

        try:
            # Get admin user or create a default one if needed
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
            except User.DoesNotExist:
                admin_user = None

            if not admin_user:
                self.stdout.write(self.style.WARNING('No admin user found.'))

            # Begin transaction to ensure all or nothing
            with transaction.atomic():
                self.create_satisfaction_survey(admin_user)
                self.create_nps_survey(admin_user)
                self.create_appointment_feedback_survey(admin_user)

            self.stdout.write(self.style.SUCCESS('Successfully created survey templates'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating survey templates: {e}'))

    def create_satisfaction_survey(self, admin_user):
        """Create a general satisfaction survey"""
        self.stdout.write('Creating satisfaction survey template...')
        
        survey = Survey.objects.create(
            title=_('Patient Satisfaction Survey'),
            description=_('Please help us improve our services by providing your feedback.'),
            survey_type='satisfaction',
            is_active=True,
            created_by=admin_user,
            max_questions_per_session=5,
            show_progress=True,
            thank_you_message=_('Thank you for your valuable feedback! Your input helps us improve our services.')
        )
        
        # Create questions
        questions = [
            {
                'text': _('How would you rate your overall experience with our clinic?'),
                'question_type': 'rating',
                'required': True,
                'order': 0,
            },
            {
                'text': _('Did the staff treat you with courtesy and respect?'),
                'question_type': 'yes_no',
                'required': True,
                'order': 1,
            },
            {
                'text': _('How satisfied are you with the quality of care you received?'),
                'question_type': 'emoji',
                'required': True,
                'order': 2,
            },
            {
                'text': _('What aspects of our service could be improved?'),
                'question_type': 'text',
                'required': False,
                'order': 3,
            },
            {
                'text': _('Would you recommend our clinic to friends and family?'),
                'question_type': 'yes_no',
                'required': True,
                'order': 4,
            },
        ]
        
        for question_data in questions:
            Question.objects.create(
                survey=survey,
                **question_data
            )
            
        self.stdout.write(self.style.SUCCESS(f'  Created satisfaction survey with {len(questions)} questions'))
        return survey
        
    def create_nps_survey(self, admin_user):
        """Create a Net Promoter Score (NPS) survey"""
        self.stdout.write('Creating NPS survey template...')
        
        survey = Survey.objects.create(
            title=_('Patient Loyalty Survey'),
            description=_('Help us understand how likely you are to recommend our clinic to others.'),
            survey_type='nps',
            is_active=True,
            created_by=admin_user,
            max_questions_per_session=2,
            show_progress=True,
        )
        
        # Create questions
        questions = [
            {
                'text': _('On a scale of 0-10, how likely are you to recommend LIMBS Orthopaedic to a friend or family member?'),
                'question_type': 'single_choice',
                'required': True,
                'order': 0,
                'choices': '0 - Not at all likely\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10 - Extremely likely',
            },
            {
                'text': _('What is the main reason for your score?'),
                'question_type': 'text',
                'required': False,
                'order': 1,
            },
        ]
        
        for question_data in questions:
            Question.objects.create(
                survey=survey,
                **question_data
            )
            
        self.stdout.write(self.style.SUCCESS(f'  Created NPS survey with {len(questions)} questions'))
        return survey
        
    def create_appointment_feedback_survey(self, admin_user):
        """Create a survey specifically for appointment feedback"""
        self.stdout.write('Creating appointment feedback survey template...')
        
        survey = Survey.objects.create(
            title=_('Appointment Feedback'),
            description=_('Please provide feedback about your recent appointment.'),
            survey_type='feedback',
            is_active=True,
            created_by=admin_user,
            show_after_appointment=True,
            show_after_days=1,
        )
        
        # Create questions
        questions = [
            {
                'text': _('How would you rate the ease of scheduling your appointment?'),
                'question_type': 'rating',
                'required': True,
                'order': 0,
            },
            {
                'text': _('Was the doctor on time for your appointment?'),
                'question_type': 'yes_no',
                'required': True,
                'order': 1,
            },
            {
                'text': _('How would you rate the doctor\'s attention to your concerns?'),
                'question_type': 'rating',
                'required': True,
                'order': 2,
            },
            {
                'text': _('Were your questions addressed to your satisfaction?'),
                'question_type': 'yes_no',
                'required': True,
                'order': 3,
            },
            {
                'text': _('How would you rate the clarity of information about your treatment plan?'),
                'question_type': 'rating',
                'required': True,
                'order': 4,
            },
            {
                'text': _('What went well during your appointment?'),
                'question_type': 'text',
                'required': False,
                'order': 5,
            },
            {
                'text': _('What could have been better about your appointment?'),
                'question_type': 'text',
                'required': False,
                'order': 6,
            },
        ]
        
        for question_data in questions:
            Question.objects.create(
                survey=survey,
                **question_data
            )
            
        self.stdout.write(self.style.SUCCESS(f'  Created appointment feedback survey with {len(questions)} questions'))
        return survey