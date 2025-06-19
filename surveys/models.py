from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

# Survey types - specifically for micro-surveys
SURVEY_TYPES = (
    ('satisfaction', _('Satisfaction Survey')),
    ('feedback', _('Feedback Survey')),
    ('experience', _('Patient Experience')),
    ('nps', _('Net Promoter Score')),
    ('service_quality', _('Service Quality')),
    ('follow_up', _('Follow-up Survey')),
)

# Question types
QUESTION_TYPES = (
    ('rating', _('Rating Scale (1-5)')),
    ('yes_no', _('Yes/No')),
    ('text', _('Text Answer')),
    ('multiple_choice', _('Multiple Choice')),
    ('single_choice', _('Single Choice')),
    ('emoji', _('Emoji Rating')),
)

class Survey(models.Model):
    """Model for micro surveys to gather patient feedback"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    survey_type = models.CharField(max_length=20, choices=SURVEY_TYPES, default='satisfaction')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_surveys')
    
    # Survey configuration
    max_questions_per_session = models.PositiveSmallIntegerField(default=5, 
                                help_text=_("Maximum number of questions to show in a single session"))
    show_progress = models.BooleanField(default=True,
                                help_text=_("Show progress bar during the survey"))
    allow_anonymous = models.BooleanField(default=True,
                                help_text=_("Allow anonymous responses (without login)"))
    thank_you_message = models.TextField(default=_("Thank you for completing this survey!"))
    email_thank_you = models.BooleanField(default=False,
                                help_text=_("Send thank you email after completion"))
    
    # Targeting options
    show_after_appointment = models.BooleanField(default=False,
                                help_text=_("Show after appointment completion"))
    show_after_days = models.PositiveSmallIntegerField(default=0,
                                help_text=_("Days after appointment to show survey"))
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('surveys:survey_detail', args=[str(self.id)])
    
    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')
        ordering = ['-created_at']


class Question(models.Model):
    """Individual survey questions"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    choices = models.TextField(blank=True, null=True, 
                help_text=_("For multiple/single choice questions, separate options with newlines"))
    
    def __str__(self):
        return f"{self.text[:50]}..."
    
    def get_choices_list(self):
        """Return choices as a list if defined, otherwise empty list"""
        if self.choices:
            return [choice.strip() for choice in self.choices.split('\n') if choice.strip()]
        return []
    
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['survey', 'order']


class Response(models.Model):
    """Survey responses from patients"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='survey_responses')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    is_complete = models.BooleanField(default=False)
    
    # Link to appointment if this is related to an appointment
    appointment_id = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f"Response by {self.user.get_full_name() or self.user.username}"
        return f"Anonymous response #{self.id}"
    
    def complete(self):
        """Mark the response as complete and record completion time"""
        self.is_complete = True
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = _('Response')
        verbose_name_plural = _('Responses')
        ordering = ['-started_at']


class Answer(models.Model):
    """Individual answers to survey questions"""
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    
    # Store different types of answers in appropriate fields
    text_answer = models.TextField(blank=True, null=True)
    choice_answer = models.CharField(max_length=255, blank=True, null=True)
    rating_answer = models.PositiveSmallIntegerField(null=True, blank=True)
    boolean_answer = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer to {self.question}"
    
    def get_answer_value(self):
        """Return the answer value based on the question type"""
        question_type = self.question.question_type
        
        if question_type == 'text':
            return self.text_answer
        elif question_type in ('multiple_choice', 'single_choice'):
            return self.choice_answer
        elif question_type == 'rating' or question_type == 'emoji':
            return self.rating_answer
        elif question_type == 'yes_no':
            return self.boolean_answer
        return None
    
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')