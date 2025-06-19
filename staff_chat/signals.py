from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

from .models import StaffGroup, StaffGroupMember, StaffChatMessage

# Signal to automatically create the main staff group if it doesn't exist
@receiver(post_save, sender=User)
def create_or_update_staff_membership(sender, instance=None, created=False, **kwargs):
    """
    When a user is created or updated, check if they should be in the staff chat group
    based on their superuser status or Doctor group membership
    """
    # Get the main staff group (create it if it doesn't exist)
    main_group, created_group = StaffGroup.objects.get_or_create(
        name="Staff Communication",
        defaults={'description': "Main communication channel for all staff members"}
    )
    
    # If this is a new group, add a welcome message
    if created_group:
        # Find a superuser to be the sender of the welcome message
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            StaffChatMessage.objects.create(
                group=main_group,
                sender=superuser,
                message="Welcome to the staff communication channel! This is where all staff members can communicate.",
                is_system_message=True
            )
    
    # Check if user is superuser or in the Doctor group
    is_staff_member = instance.is_superuser or instance.groups.filter(name='Doctor').exists()
    
    # Check if user is already a member
    existing_membership = StaffGroupMember.objects.filter(user=instance, group=main_group).first()
    
    # If user should be in the staff group
    if is_staff_member:
        if not existing_membership:
            # Add user to the group
            membership = StaffGroupMember.objects.create(
                user=instance,
                group=main_group,
                is_admin=instance.is_superuser
            )
            
            # Add a welcome message
            StaffChatMessage.objects.create(
                group=main_group,
                sender=instance,
                message=f"{instance.get_full_name() or instance.username} has joined the staff communication channel.",
                is_system_message=True
            )
        elif existing_membership.is_admin != instance.is_superuser:
            # Update admin status if it changed
            existing_membership.is_admin = instance.is_superuser
            existing_membership.save()
    
    # If user should not be in the staff group but is currently a member
    elif existing_membership:
        # Add a leaving message
        StaffChatMessage.objects.create(
            group=main_group,
            sender=instance,
            message=f"{instance.get_full_name() or instance.username} has left the staff communication channel.",
            is_system_message=True
        )
        
        # Remove from the group
        existing_membership.delete()

# Signal to update staff membership when a user's group membership changes
@receiver(m2m_changed, sender=User.groups.through)
def handle_user_group_changes(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    When a user is added to or removed from a group, check if their staff chat membership
    should be updated based on whether they are in the Doctor group
    """
    if action in ('post_add', 'post_remove', 'post_clear'):
        # Update staff membership
        create_or_update_staff_membership(sender=User, instance=instance, created=False)