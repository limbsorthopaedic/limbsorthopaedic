from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings

import json
import os
from datetime import datetime

from .models import StaffGroup, StaffGroupMember, StaffChatMessage, ChatAttachment
from .forms import MessageForm

from core.models import SocialMedia

@login_required
def staff_chat(request):
    """Main view for the staff chat interface"""
    # Check if user is a member of any staff group
    if not StaffGroupMember.objects.filter(user=request.user).exists():
        messages.error(request, "You do not have access to the staff communication channel.")
        if request.user.is_superuser:
            return redirect('admin:index')
        elif hasattr(request.user, 'doctor'):
            return redirect('doctor_dashboard')
        else:
            return redirect('home')
    
    # Get the staff group (only the main one for now)
    staff_group = StaffGroup.objects.first()
    if not staff_group:
        messages.error(request, "Staff communication channel not found.")
        return redirect('home')
    
    # Get user's membership
    membership = get_object_or_404(StaffGroupMember, user=request.user, group=staff_group)
    
    # Mark messages as read
    membership.mark_messages_as_read()
    
    # Get all messages for this group with pagination
    messages_queryset = StaffChatMessage.objects.filter(group=staff_group).order_by('-created_at')
    paginator = Paginator(messages_queryset, 50)  # Show 50 messages per page
    page = request.GET.get('page', 1)
    chat_messages = paginator.get_page(page)
    
    # Reverse the messages for display (newest at the bottom)
    chat_messages_display = list(reversed(chat_messages.object_list))
    
    # Get all members of the group
    members = StaffGroupMember.objects.filter(group=staff_group).select_related('user')
    
    # Create message form
    message_form = MessageForm()
    
    # Get social media links for footer
    social_media = SocialMedia.objects.filter(is_active=True)
    
    context = {
        'staff_group': staff_group,
        'chat_messages': chat_messages,
        'chat_messages_display': chat_messages_display,
        'members': members,
        'current_user': request.user,
        'message_form': message_form,
        'social_media': social_media,  # Add social media for footer
    }
    
    return render(request, 'staff_chat/chat.html', context)

@login_required
@require_POST
def send_message(request):
    """View to handle sending a new message"""
    # Check if user is a member of any staff group
    if not StaffGroupMember.objects.filter(user=request.user).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': 'Access denied'})
        messages.error(request, "You do not have access to the staff communication channel.")
        return redirect('home')
    
    # Get the staff group (only the main one for now)
    staff_group = StaffGroup.objects.first()
    if not staff_group:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': 'Staff group not found'})
        messages.error(request, "Staff communication channel not found.")
        return redirect('home')
    
    # Process the form
    form = MessageForm(request.POST)
    if form.is_valid():
        # Create the message
        message = form.save(commit=False)
        message.group = staff_group
        message.sender = request.user
        message.save()
        
        # Handle file attachment if present
        if request.FILES.get('file'):
            attachment = ChatAttachment(message=message, file=request.FILES['file'])
            attachment.save()
        
        # If it's an AJAX request, return a JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return the rendered message HTML
            message_html = render_to_string(
                'staff_chat/message.html',
                {'message': message, 'current_user': request.user}
            )
            return JsonResponse({
                'status': 'success',
                'message_html': message_html,
                'message_id': message.id
            })
        
        # Otherwise redirect back to the chat
        return redirect('staff_chat:staff_chat')
    else:
        # Handle form errors
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors})
        
        messages.error(request, "There was an error sending your message.")
        return redirect('staff_chat:staff_chat')

@login_required
@require_GET
def get_new_messages(request):
    """AJAX view to get new messages since the last one the user has seen"""
    # Check if user is a member of any staff group
    if not StaffGroupMember.objects.filter(user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'Access denied'})
    
    # Get the staff group (only the main one for now)
    staff_group = StaffGroup.objects.first()
    if not staff_group:
        return JsonResponse({'status': 'error', 'message': 'Staff group not found'})
    
    # Get last message ID from request
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0
    
    # Get all new messages
    new_messages = StaffChatMessage.objects.filter(
        group=staff_group, 
        id__gt=last_id
    ).order_by('created_at')
    
    if not new_messages.exists():
        return JsonResponse({
            'status': 'success',
            'messages_html': [],
            'last_id': last_id
        })
    
    # Mark messages as read
    membership = get_object_or_404(StaffGroupMember, user=request.user, group=staff_group)
    membership.mark_messages_as_read()
    
    # Render each message to HTML
    messages_html = []
    for message in new_messages:
        html = render_to_string(
            'staff_chat/message.html',
            {'message': message, 'current_user': request.user}
        )
        messages_html.append(html)
    
    return JsonResponse({
        'status': 'success',
        'messages_html': messages_html,
        'last_id': new_messages.last().id
    })

@login_required
def download_attachment(request, attachment_id):
    """View to download a chat attachment"""
    # Get the attachment
    attachment = get_object_or_404(ChatAttachment, id=attachment_id)
    
    # Check if user has access to this attachment
    user_memberships = StaffGroupMember.objects.filter(user=request.user)
    user_groups = user_memberships.values_list('group', flat=True)
    message_group = attachment.message.group
    
    if message_group.id not in user_groups:
        raise Http404("Attachment not found")
    
    # Prepare the response
    response = HttpResponse(attachment.file, content_type=attachment.file_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
    return response

@login_required
def delete_message(request, message_id):
    """Delete a chat message"""
    # Get the message
    message = get_object_or_404(StaffChatMessage, id=message_id)
    
    # Check if user can delete this message (own message or superuser)
    if message.sender != request.user and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Permission denied'})
        messages.error(request, "You don't have permission to delete this message.")
        return redirect('staff_chat:staff_chat')
    
    # Delete the message
    message.delete()
    
    # Return response based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, "Message deleted successfully.")
    return redirect('staff_chat:staff_chat')

@login_required
@require_POST
def edit_message(request, message_id):
    """Edit a chat message"""
    # Get the message
    message = get_object_or_404(StaffChatMessage, id=message_id)
    
    # Check if user can edit this message (only own messages)
    if message.sender != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Permission denied'})
        messages.error(request, "You don't have permission to edit this message.")
        return redirect('staff_chat:staff_chat')
    
    # Update the message
    new_message_text = request.POST.get('message', '').strip()
    if not new_message_text:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'})
        messages.error(request, "Message cannot be empty.")
        return redirect('staff_chat:staff_chat')
    
    message.message = new_message_text
    message.is_edited = True
    message.save()
    
    # Return response based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return updated message HTML
        message_html = render_to_string(
            'staff_chat/message.html',
            {'message': message, 'current_user': request.user}
        )
        return JsonResponse({
            'status': 'success',
            'message_html': message_html
        })
    
    messages.success(request, "Message updated successfully.")
    return redirect('staff_chat:staff_chat')