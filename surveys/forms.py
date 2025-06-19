from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Survey, Question, Response, Answer, QUESTION_TYPES


class SurveyForm(forms.ModelForm):
    """Form for creating and editing surveys"""
    class Meta:
        model = Survey
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'rows': 3}),
            'thank_you_message': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'rows': 2}),
        }


class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions"""
    class Meta:
        model = Question
        exclude = []
        widgets = {
            'text': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'rows': 2}),
            'choices': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 
                'rows': 3,
                'placeholder': _('Enter each choice on a new line')
            }),
        }


class DynamicSurveyForm:
    """
    Dynamic form class that generates form fields based on question types.
    This is not a Django Form class but a wrapper that creates fields dynamically.
    """
    def __init__(self, survey, *args, **kwargs):
        self.survey = survey
        self.questions = survey.questions.all().order_by('order')
        self.fields = {}
        
        # Create a field for each question
        for question in self.questions:
            field_name = f'question_{question.id}'
            self.fields[field_name] = self._create_field_for_question(question)
            
    def _create_field_for_question(self, question):
        """Create the appropriate form field based on question type"""
        required = question.required
        field_attrs = {
            'label': question.text,
            'required': required,
        }
        
        if question.question_type == 'rating':
            choices = [(i, str(i)) for i in range(1, 6)]  # 1-5 rating
            return forms.ChoiceField(
                choices=choices, 
                widget=forms.RadioSelect(attrs={'class': 'inline-flex gap-4'}),
                **field_attrs
            )
            
        elif question.question_type == 'emoji':
            emoji_choices = [
                (1, '😞'),
                (2, '🙁'),
                (3, '😐'),
                (4, '🙂'),
                (5, '😀'),
            ]
            return forms.ChoiceField(
                choices=emoji_choices, 
                widget=forms.RadioSelect(attrs={'class': 'inline-flex gap-4 text-2xl'}),
                **field_attrs
            )
            
        elif question.question_type == 'yes_no':
            return forms.BooleanField(
                widget=forms.RadioSelect(choices=[(True, _('Yes')), (False, _('No'))]),
                **field_attrs
            )
            
        elif question.question_type == 'text':
            return forms.CharField(
                widget=forms.Textarea(attrs={
                    'class': 'w-full px-4 py-2 border rounded-md',
                    'rows': 3
                }),
                **field_attrs
            )
            
        elif question.question_type == 'multiple_choice':
            choices = [(c, c) for c in question.get_choices_list()]
            return forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline-flex gap-4'}),
                **field_attrs
            )
            
        elif question.question_type == 'single_choice':
            choices = [(c, c) for c in question.get_choices_list()]
            return forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'inline-flex gap-4'}),
                **field_attrs
            )
            
        # Default fallback to text field
        return forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}), **field_attrs)