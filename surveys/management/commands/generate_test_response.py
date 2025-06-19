from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

from surveys.models import Survey, Response, Answer, Question


class Command(BaseCommand):
    help = 'Creates a test response for a specified survey or the first active survey found'

    def add_arguments(self, parser):
        parser.add_argument(
            '--survey-id',
            type=int,
            help='Specify the survey ID to use',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specify the user ID to associate with the response',
        )

    def handle(self, *args, **options):
        try:
            # Find a survey to use
            survey_id = options.get('survey_id')
            if survey_id:
                try:
                    survey = Survey.objects.get(id=survey_id)
                except Survey.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Survey with ID {survey_id} not found.'))
                    return
            else:
                # Get the first active survey
                survey = Survey.objects.filter(is_active=True).first()
                if not survey:
                    self.stdout.write(self.style.ERROR('No active surveys found.'))
                    return
                
            # Find a user to use
            user_id = options.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found.'))
                    return
            else:
                # Get a random user (preferably a regular user, not admin)
                user = User.objects.filter(is_superuser=False).first() or User.objects.first()
                if not user:
                    self.stdout.write(self.style.WARNING('No users found, creating anonymous response.'))
                    user = None
            
            # Get the questions for this survey
            questions = Question.objects.filter(survey=survey).order_by('order')
            if not questions.exists():
                self.stdout.write(self.style.ERROR(f'Survey "{survey.title}" has no questions.'))
                return
                
            # Begin transaction to ensure all or nothing
            with transaction.atomic():
                # Create a response
                response = Response.objects.create(
                    survey=survey,
                    user=user,
                    started_at=timezone.now() - timezone.timedelta(minutes=10),  # Started 10 minutes ago
                    completed_at=timezone.now(),  # Completed just now
                    is_complete=True,
                    ip_address='127.0.0.1',
                    user_agent='Test-Agent/1.0'
                )
                
                # Create sample answers for each question
                for question in questions:
                    answer = self._create_sample_answer(question, response)
                    if answer:
                        self.stdout.write(f'  Created answer for question: "{question.text[:30]}..."')
                    
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created test response for survey "{survey.title}" with {questions.count()} answers.'
                ))
                
                if user:
                    self.stdout.write(f'Response assigned to user: {user.username}')
                else:
                    self.stdout.write('Response is anonymous.')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test response: {e}'))
            
    def _create_sample_answer(self, question, response):
        """Create a sample answer based on the question type"""
        try:
            if question.question_type == 'rating':
                # Random rating between 3-5 (mostly positive)
                import random
                rating = random.randint(3, 5)
                return Answer.objects.create(
                    response=response,
                    question=question,
                    rating_answer=rating
                )
                
            elif question.question_type == 'emoji':
                # Random emoji rating between 3-5 (mostly positive)
                import random
                rating = random.randint(3, 5)
                return Answer.objects.create(
                    response=response,
                    question=question,
                    rating_answer=rating
                )
                
            elif question.question_type == 'yes_no':
                # Mostly 'yes' answers
                import random
                is_yes = random.random() > 0.2  # 80% yes
                return Answer.objects.create(
                    response=response,
                    question=question,
                    boolean_answer=is_yes
                )
                
            elif question.question_type == 'text':
                # Sample text responses
                text_responses = [
                    "Very satisfied with the service.",
                    "The staff was friendly and professional.",
                    "I appreciate the thorough explanation of my condition.",
                    "The wait time was reasonable and the clinic was clean.",
                    "All my questions were answered clearly."
                ]
                import random
                text = random.choice(text_responses)
                return Answer.objects.create(
                    response=response,
                    question=question,
                    text_answer=text
                )
                
            elif question.question_type in ('multiple_choice', 'single_choice'):
                # Select a random choice
                choices = question.get_choices_list()
                if choices:
                    import random
                    choice = random.choice(choices)
                    return Answer.objects.create(
                        response=response,
                        question=question,
                        choice_answer=choice
                    )
                    
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating answer for question {question.id}: {e}'))
            return None