import os
import django
import sys
from django.utils import timezone
from datetime import date, timedelta

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
django.setup()

# Import models after Django is configured
from appointments.models import Appointment, Service
from accounts.utils import send_appointment_confirmation_email
from django.contrib.auth.models import User

def create_test_appointment():
    """Create a test appointment to demonstrate email functionality"""
    # Find an existing service or create one
    try:
        service = Service.objects.first()
        if not service:
            print("No services found in database. Please create a service first.")
            return None
    except Exception as e:
        print(f"Error fetching service: {e}")
        return None
    
    # Create a test appointment
    tomorrow = date.today() + timedelta(days=1)
    
    try:
        appointment = Appointment.objects.create(
            full_name="Test Patient",
            email="mail@limbsorthopaedic.org",
            phone="+254719628276",
            service=service,
            preferred_date=tomorrow,
            preferred_time=timezone.now().time(),
            notes="This is a test appointment to verify email functionality."
        )
        print(f"Created test appointment: {appointment}")
        return appointment
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return None

def confirm_appointment(appointment):
    """Update appointment status to 'confirmed' and send confirmation email"""
    if not appointment:
        print("No appointment to confirm.")
        return
    
    try:
        # Change status to confirmed
        appointment.status = 'confirmed'
        
        # Assign doctor if available
        try:
            from accounts.models import Doctor
            doctor = Doctor.objects.first()
            if doctor:
                appointment.assigned_doctor = doctor
                print(f"Assigned doctor: {doctor}")
        except Exception as e:
            print(f"Could not assign doctor: {e}")
        
        # Save changes
        appointment.save()
        print(f"Updated appointment status to: {appointment.status}")
        
        # Send confirmation email
        email_sent = send_appointment_confirmation_email(appointment)
        if email_sent:
            print(f"✅ Confirmation email sent successfully to {appointment.email}")
        else:
            print(f"❌ Failed to send confirmation email to {appointment.email}")
    
    except Exception as e:
        print(f"Error confirming appointment: {e}")

if __name__ == "__main__":
    print("Creating and confirming a test appointment...")
    
    # Process command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'create':
        # Only create without confirming
        appointment = create_test_appointment()
        if appointment:
            print(f"Test appointment created with ID {appointment.id} and status '{appointment.status}'")
            print("To confirm this appointment and send a confirmation email, run:")
            print(f"python {__file__} confirm {appointment.id}")
    
    elif len(sys.argv) > 2 and sys.argv[1] == 'confirm' and sys.argv[2].isdigit():
        # Confirm an existing appointment
        appointment_id = int(sys.argv[2])
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            confirm_appointment(appointment)
        except Appointment.DoesNotExist:
            print(f"Appointment with ID {appointment_id} not found.")
        except Exception as e:
            print(f"Error: {e}")
    
    else:
        # Default: create and immediately confirm
        appointment = create_test_appointment()
        if appointment:
            print("Confirming appointment...")
            confirm_appointment(appointment)
    
    print("Done.")