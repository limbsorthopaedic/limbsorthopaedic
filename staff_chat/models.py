from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.html import format_html
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

class StaffGroup(models.Model):
    """A group of staff members for communication"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_members_count(self):
        """Get the number of members in this group"""
        return self.members.count()
    
    def get_active_members_count(self):
        """Get the number of active members in this group"""
        return self.members.filter(is_active=True).count()
    
    def get_unread_messages_count(self):
        """Get the total number of unread messages across all members"""
        # Calculate the sum of unread messages for all members
        return sum(
            member.get_unread_messages_count() 
            for member in self.members.all()
        )
    
    class Meta:
        verbose_name = "Staff Group"
        verbose_name_plural = "Staff Groups"
        ordering = ['-created_at']

class StaffGroupMember(models.Model):
    """A member of a staff group"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_memberships')
    group = models.ForeignKey(StaffGroup, on_delete=models.CASCADE, related_name='members')
    is_admin = models.BooleanField(default=False, help_text="Admin members can manage the group")
    is_active = models.BooleanField(default=True, help_text="Inactive members won't receive notifications")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} in {self.group.name}"
    
    def get_unread_messages_count(self):
        """Get the number of unread messages for this member"""
        return StaffChatMessage.objects.filter(
            group=self.group,
            created_at__gt=self.last_read_at
        ).exclude(sender=self.user).count()
    
    def mark_messages_as_read(self):
        """Mark all messages in the group as read"""
        self.last_read_at = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = "Staff Group Member"
        verbose_name_plural = "Staff Group Members"
        unique_together = ('user', 'group')
        ordering = ['group', 'user__username']

class StaffChatMessage(models.Model):
    """A message in a staff group chat"""
    group = models.ForeignKey(StaffGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_staff_messages')
    message = models.TextField()
    is_system_message = models.BooleanField(default=False, help_text="System messages are displayed differently")
    is_edited = models.BooleanField(default=False, help_text="Shows if the message has been edited")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.is_system_message:
            return f"System: {self.message[:50]}..."
        return f"{self.sender.get_full_name() or self.sender.username}: {self.message[:50]}..."
    
    def get_formatted_message(self):
        """Return a formatted version of the message with line breaks"""
        return format_html('<br>'.join(self.message.split('\n')))
    
    def get_time_display(self):
        """Format the time for display"""
        return self.created_at.strftime('%b %d, %Y at %I:%M %p')
    
    class Meta:
        verbose_name = "Staff Chat Message"
        verbose_name_plural = "Staff Chat Messages"
        ordering = ['-created_at']

class ChatAttachment(models.Model):
    """An attachment to a staff chat message"""
    message = models.ForeignKey(StaffChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='staff_chat_attachments/')
    file_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment: {self.file_name}"
    
    def save(self, *args, **kwargs):
        # Set file name from the file if not provided
        if not self.file_name and self.file:
            self.file_name = self.file.name.split('/')[-1]
        
        # Try to get file type from the file
        if self.file and not self.file_type:
            # Extract file extension
            file_extension = self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''
            
            # Map common extensions to types
            type_map = {
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'txt': 'text/plain',
            }
            
            self.file_type = type_map.get(file_extension, 'application/octet-stream')
            
        # Get file size if available
        if self.file and not self.file_size and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def get_icon_class(self):
        """Return a Font Awesome icon class based on file type"""
        if not self.file_type:
            return 'fas fa-file'
            
        if self.file_type.startswith('image/'):
            return 'fas fa-file-image'
        elif self.file_type == 'application/pdf':
            return 'fas fa-file-pdf'
        elif self.file_type in ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
            return 'fas fa-file-word'
        elif self.file_type in ('application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
            return 'fas fa-file-excel'
        elif self.file_type.startswith('text/'):
            return 'fas fa-file-alt'
        elif self.file_type.startswith('video/'):
            return 'fas fa-file-video'
        elif self.file_type.startswith('audio/'):
            return 'fas fa-file-audio'
        else:
            return 'fas fa-file'
    
    def get_formatted_size(self):
        """Return a human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    class Meta:
        verbose_name = "Chat Attachment"
        verbose_name_plural = "Chat Attachments"
        ordering = ['uploaded_at']

# Signal to automatically create the main staff group if it doesn't exist
@receiver(post_save, sender=User)
def create_main_staff_group(sender, instance=None, created=False, **kwargs):
    """Create the main staff group when the first superuser is created"""
    if created and instance.is_superuser:
        # Check if any staff group exists
        if StaffGroup.objects.count() == 0:
            # Create the main staff group
            main_group = StaffGroup.objects.create(
                name="Staff Communication",
                description="Main communication channel for all staff members"
            )
            
            # Add the superuser as an admin member
            StaffGroupMember.objects.create(
                user=instance,
                group=main_group,
                is_admin=True
            )
            
            # Add a welcome message
            StaffChatMessage.objects.create(
                group=main_group,
                sender=instance,
                message="Welcome to the staff communication channel! This is where all staff members can communicate.",
                is_system_message=True
            )

# Signal to automatically add users to the main staff group when they are added to staff groups
@receiver(m2m_changed, sender=User.groups.through)
def handle_user_group_changes(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    When a user is added to or removed from a group, update their status in the staff chat
    This handles the case when a user's group membership changes (e.g., promoted to admin)
    """
    if action in ('post_add', 'post_remove', 'post_clear'):
        update_staff_membership(instance)

def update_staff_membership(user):
    """
    Update a user's staff group membership based on their roles
    """
    # Get the main staff group (create it if it doesn't exist)
    main_group, created = StaffGroup.objects.get_or_create(
        name="Staff Communication",
        defaults={'description': "Main communication channel for all staff members"}
    )
    
    # Check if user is superuser or in the Doctor group
    is_staff_member = user.is_superuser or user.groups.filter(name='Doctor').exists()
    
    # If user should be in the staff group
    if is_staff_member:
        # Check if they are already a member
        membership, created = StaffGroupMember.objects.get_or_create(
            user=user,
            group=main_group,
            defaults={'is_admin': user.is_superuser}
        )
        
        # If not created (already exists), ensure admin status is correct
        if not created and membership.is_admin != user.is_superuser:
            membership.is_admin = user.is_superuser
            membership.save()
            
        # If newly created, add a welcome message
        if created:
            StaffChatMessage.objects.create(
                group=main_group,
                sender=user,
                message=f"{user.get_full_name() or user.username} has joined the staff communication channel.",
                is_system_message=True
            )
    # If user should not be in the staff group but is currently a member
    elif StaffGroupMember.objects.filter(user=user, group=main_group).exists():
        # Add a leaving message before removing
        StaffChatMessage.objects.create(
            group=main_group,
            sender=user,
            message=f"{user.get_full_name() or user.username} has left the staff communication channel.",
            is_system_message=True
        )
        
        # Remove from the group
        StaffGroupMember.objects.filter(user=user, group=main_group).delete()