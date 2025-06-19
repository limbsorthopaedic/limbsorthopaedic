import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from staff_chat.models import StaffGroup, StaffGroupMember, StaffChatMessage

def create_staff_chat():
    """Create a staff chat group with the superuser as a member"""
    # Get the superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("No superuser found!")
        return
    
    # Create the staff group
    staff_group, created_group = StaffGroup.objects.get_or_create(
        name='Staff Communication',
        defaults={'description': 'Main communication channel for all staff members'}
    )
    print(f'Created staff group: {created_group}')
    
    # Add the superuser as a member
    membership, created_membership = StaffGroupMember.objects.get_or_create(
        user=superuser,
        group=staff_group,
        defaults={'is_admin': True}
    )
    print(f'Created superuser membership: {created_membership}')
    
    # Add a welcome message
    message, created_message = StaffChatMessage.objects.get_or_create(
        group=staff_group,
        sender=superuser,
        message='Welcome to the staff communication channel! This is where all staff members can communicate.',
        is_system_message=True
    )
    print(f'Created welcome message: {created_message}')
    
    print(f'Staff chat setup complete for superuser: {superuser.username}')

if __name__ == '__main__':
    create_staff_chat()