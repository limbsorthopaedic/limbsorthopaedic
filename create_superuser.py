import os
import django
import time
import sys
from django.db import connection, connections, OperationalError

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
django.setup()

from django.contrib.auth.models import User

def wait_for_db():
    """Wait for database to be available"""
    print("Testing database connection...")
    max_retries = 10  # Increased retries
    for attempt in range(max_retries):
        try:
            # Close all existing connections first
            for conn in connections.all():
                conn.close()
                
            # Try to establish a new connection
            connection.ensure_connection()
            connection.connect()
            
            # Test with a simple query
            connection.cursor().execute("SELECT 1")
            
            print("Database connection successful!")
            return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 30)  # Exponential backoff with max 30 seconds
                print(f"Database connection failed. Retrying in {wait_time} seconds... ({str(e)})")
                time.sleep(wait_time)
            else:
                print(f"Database connection failed after {max_retries} attempts: {str(e)}")
                return False
        except Exception as e:
            print(f"Unexpected database error: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 30)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts.")
                return False

def create_superuser(username='admin', email='limbsorthopaedic@gmail.com', password='adminP@ssword123'):
    """Create a superuser with the given credentials"""
    try:
        if not wait_for_db():
            print("Could not connect to database. Aborting superuser creation.")
            return False
        
        # Ensure we have a fresh connection
        for conn in connections.all():
            conn.close()
        connection.connect()
        
        # Check if user exists
        try:
            user_exists = User.objects.filter(username=username).exists()
            if not user_exists:
                User.objects.create_superuser(username, email, password)
                print(f"Superuser '{username}' created successfully!")
                return True
            else:
                print(f"Superuser '{username}' already exists.")
                return True
        except OperationalError as e:
            print(f"Database error while creating superuser: {str(e)}")
            print("Trying again with a different approach...")
            
            # Alternative approach using raw SQL
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = %s", [username])
                if cursor.fetchone()[0] == 0:
                    # Import for password hashing
                    from django.contrib.auth.hashers import make_password
                    
                    # Generate a properly hashed password
                    hashed_password = make_password(password)
                    
                    # Insert the superuser directly
                    cursor.execute(
                        "INSERT INTO auth_user (username, email, password, is_superuser, is_staff, is_active, date_joined) "
                        "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                        [username, email, hashed_password, True, True, True]
                    )
                    print(f"Superuser '{username}' created successfully using raw SQL!")
                    return True
                else:
                    print(f"Superuser '{username}' already exists (verified with raw SQL).")
                    return True
            except Exception as inner_e:
                print(f"Failed to create superuser using raw SQL: {str(inner_e)}")
                return False
    except Exception as e:
        print(f"Error creating superuser: {str(e)}")
        return False

def create_custom_superuser(username, email, password):
    """Create a superuser with custom credentials"""
    return create_superuser(username, email, password)

if __name__ == '__main__':
    create_superuser()