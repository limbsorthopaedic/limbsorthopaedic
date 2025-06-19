import os
import sys
from create_superuser import create_custom_superuser

def main():
    """
    Create a custom superuser with the provided credentials.
    Usage: python create_custom_superuser.py username email password
    """
    if len(sys.argv) != 4:
        print("Usage: python create_custom_superuser.py username email password")
        return
        
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    success = create_custom_superuser(username, email, password)
    if success:
        print("Custom superuser creation completed.")
    else:
        print("Failed to create custom superuser.")

if __name__ == '__main__':
    main()