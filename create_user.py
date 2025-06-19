#!/usr/bin/env python

"""
Script to create Django users (both regular and superusers)
with improved error handling and database connection retries.

Examples:
    # Create a default superuser (admin/)
    python create_user.py

    # Create a custom superuser
    python create_user.py --superuser --username=owner --email=admin@limbsorthopaedic.org --password=secretpass123

    # Create a regular user
    python create_user.py --username=mail --email=mail@limbsorthopaedic.org --password=userpass123
"""

import os
import django
import time
import sys
import argparse
from django.db import connection, connections, OperationalError

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def wait_for_db(max_attempts=10):
    """Wait for database to be available"""
    print("Testing database connection...")
    for attempt in range(max_attempts):
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
            if attempt < max_attempts - 1:
                wait_time = min(2 ** attempt, 30)  # Exponential backoff with max 30 seconds
                print(f"Database connection failed. Retrying in {wait_time} seconds... ({str(e)})")
                time.sleep(wait_time)
            else:
                print(f"Database connection failed after {max_attempts} attempts: {str(e)}")
                return False
        except Exception as e:
            print(f"Unexpected database error: {str(e)}")
            if attempt < max_attempts - 1:
                wait_time = min(2 ** attempt, 30)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_attempts} attempts.")
                return False

def create_user(username, email, password, is_superuser=False):
    """Create a user with the given credentials"""
    try:
        if not wait_for_db():
            print("Could not connect to database. Aborting user creation.")
            return False
        
        # Ensure we have a fresh connection
        for conn in connections.all():
            conn.close()
        connection.connect()
        
        # Check if user exists
        try:
            user_exists = User.objects.filter(username=username).exists()
            if not user_exists:
                if is_superuser:
                    User.objects.create_superuser(username, email, password)
                    print(f"Superuser '{username}' created successfully!")
                else:
                    User.objects.create_user(username, email, password)
                    print(f"User '{username}' created successfully!")
                return True
            else:
                print(f"User '{username}' already exists.")
                return True
        except OperationalError as e:
            print(f"Database error while creating user: {str(e)}")
            print("Trying again with a different approach...")
            
            # Alternative approach using raw SQL
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = %s", [username])
                if cursor.fetchone()[0] == 0:
                    # Generate a properly hashed password
                    hashed_password = make_password(password)
                    
                    # Insert the user directly
                    cursor.execute(
                        "INSERT INTO auth_user (username, email, password, is_superuser, is_staff, is_active, date_joined) "
                        "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                        [username, email, hashed_password, is_superuser, is_superuser, True]
                    )
                    user_type = "superuser" if is_superuser else "user"
                    print(f"{user_type.capitalize()} '{username}' created successfully using raw SQL!")
                    return True
                else:
                    print(f"User '{username}' already exists (verified with raw SQL).")
                    return True
            except Exception as inner_e:
                print(f"Failed to create user using raw SQL: {str(inner_e)}")
                return False
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create Django users or superusers")
    parser.add_argument('--username', default='admin', help='Username for the new user')
    parser.add_argument('--email', default='limbsorthopaedic@gmail.com', help='Email for the new user')
    parser.add_argument('--password', default='adminpassword123', help='Password for the new user')
    parser.add_argument('--superuser', action='store_true', help='Create a superuser instead of a regular user')

    args = parser.parse_args()
    
    print(f"Creating {'superuser' if args.superuser else 'user'}: {args.username}")
    create_user(args.username, args.email, args.password, args.superuser)


if __name__ == '__main__':
    main()