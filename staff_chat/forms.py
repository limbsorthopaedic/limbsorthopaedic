from django import forms
from .models import StaffChatMessage, ChatAttachment

class MessageForm(forms.ModelForm):
    """Form for sending chat messages"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 1,
            'placeholder': 'Type a message...',
            'id': 'message-input',
            'style': 'border-radius: 20px; padding: 10px 15px; resize: none; width: 100%; min-height: 45px;'
        }),
        required=True
    )
    
    file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'id': 'file-input',
            'accept': 'image/*,.pdf,.doc,.docx,.txt'
        })
    )
    
    class Meta:
        model = StaffChatMessage
        fields = ['message']
        
    def clean_message(self):
        message = self.cleaned_data['message']
        if not message.strip():
            raise forms.ValidationError("Message cannot be empty")
        return message