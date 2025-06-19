#!/bin/bash

# Script to create a Django superuser 
# with improved error handling and database connection retries

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}LIMBS Orthopaedic Admin Creation Tool${NC}"
echo "========================================="
echo

# Default credentials
DEFAULT_USERNAME="admin"
DEFAULT_EMAIL="limbsorthopaedic@gmail.com"
DEFAULT_PASSWORD="adminpassword123"

# Ask if user wants to use custom credentials
echo -e "Do you want to use custom credentials? (y/N)"
read -r use_custom

if [[ $use_custom =~ ^[Yy]$ ]]; then
    # Get username
    echo -e "Enter username (leave empty for '${DEFAULT_USERNAME}'):"
    read -r username
    username=${username:-$DEFAULT_USERNAME}
    
    # Get email
    echo -e "Enter email (leave empty for '${DEFAULT_EMAIL}'):"
    read -r email
    email=${email:-$DEFAULT_EMAIL}
    
    # Get password
    echo -e "Enter password (leave empty for '${DEFAULT_PASSWORD}'):"
    read -rs password
    echo
    password=${password:-$DEFAULT_PASSWORD}
    
    echo -e "Creating superuser with custom credentials..."
    python -c "from create_superuser import create_custom_superuser; create_custom_superuser('$username', '$email', '$password')"
else
    echo -e "Creating superuser with default credentials..."
    echo -e "Username: ${GREEN}${DEFAULT_USERNAME}${NC}"
    echo -e "Email: ${GREEN}${DEFAULT_EMAIL}${NC}"
    echo -e "Password: ${GREEN}${DEFAULT_PASSWORD}${NC}"
    
    python -c "from create_superuser import create_superuser; create_superuser()"
fi

echo
echo -e "${YELLOW}Superuser creation attempt completed.${NC}"
echo -e "If successful, you can now log in at:"
echo -e "- Main admin: ${GREEN}/admin/${NC}"
echo -e "- Alternative admin: ${GREEN}/adminlimbsorth/${NC}"
echo "========================================="