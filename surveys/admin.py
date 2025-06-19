from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Survey, Question, Response, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('text', 'question_type', 'required', 'order', 'choices')
    ordering = ('order',)
    

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'survey_type', 'is_active', 'created_at', 'response_count', 'view_survey_link')
    list_filter = ('survey_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    inlines = [QuestionInline]
    
    fieldsets = (
        (_('Survey Information'), {
            'fields': ('title', 'description', 'survey_type', 'is_active', 'created_by', 'created_at', 'updated_at')
        }),
        (_('Survey Configuration'), {
            'fields': ('max_questions_per_session', 'show_progress', 'allow_anonymous', 'thank_you_message', 'email_thank_you')
        }),
        (_('Targeting Options'), {
            'fields': ('show_after_appointment', 'show_after_days')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Save the current user as created_by if this is a new survey"""
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def response_count(self, obj):
        """Display the number of responses for this survey"""
        count = obj.responses.count()
        url = reverse('admin:surveys_response_changelist') + f'?survey__id__exact={obj.id}'
        return format_html('<a href="{}">{} {}</a>', url, count, _('responses'))
    
    response_count.short_description = _('Responses')
    
    def view_survey_link(self, obj):
        """Link to view the survey on the frontend"""
        url = reverse('surveys:survey_detail', args=[obj.id])
        return format_html('<a href="{}" target="_blank">{}</a>', url, _('View Survey'))
    
    view_survey_link.short_description = _('View')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'required', 'order')
    list_filter = ('survey', 'question_type', 'required')
    search_fields = ('text', 'survey__title')
    ordering = ('survey', 'order')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'formatted_answer', 'created_at')
    fields = ('question', 'formatted_answer', 'created_at')
    can_delete = False
    
    def formatted_answer(self, obj):
        """Format the answer based on question type"""
        answer = obj.get_answer_value()
        
        if answer is None:
            return '-'
            
        question_type = obj.question.question_type
        
        if question_type == 'rating':
            # Create a visual representation of rating
            if answer > 0:
                stars = '★' * answer + '☆' * (5 - answer)
                return format_html('<span style="color: #FFD700;">{}</span> ({})', stars, answer)
            return '-'
        
        if question_type == 'yes_no':
            return _('Yes') if answer else _('No')
            
        if question_type == 'emoji':
            # Using emoji codes for ratings 1-5
            emojis = {
                1: '😞',
                2: '🙁',
                3: '😐',
                4: '🙂',
                5: '😀'
            }
            return format_html('<span style="font-size: 1.5em;">{}</span>', emojis.get(answer, '-'))
            
        return answer
        
    formatted_answer.short_description = _('Answer')
    

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'respondent', 'is_complete', 'started_at', 'completed_at', 'updated_count')
    list_filter = ('survey', 'is_complete', 'started_at')
    
    def updated_count(self, obj):
        """Show how many times this user has updated their response"""
        if obj.user:
            return Response.objects.filter(
                survey=obj.survey,
                user=obj.user,
                is_complete=True
            ).count() - 1
        return 0
    updated_count.short_description = _('Updates')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('survey', 'user', 'started_at', 'completed_at', 'ip_address', 'user_agent', 'appointment_id')
    inlines = [AnswerInline]
    
    def respondent(self, obj):
        """Format the respondent name"""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return _('Anonymous')
    
    respondent.short_description = _('Respondent')


# We don't need to register Answer model separately as it's used via inline