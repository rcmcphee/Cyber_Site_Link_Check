#!/bin/bash

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install pip if it's not already installed
echo "Checking for pip installation..."
if ! command -v pip &> /dev/null
then
    echo "pip not found. Installing pip..."
    sudo apt-get install python3-pip -y
else
    echo "pip is already installed."
fi

# Install required Python packages using pip
echo "Installing required Python packages..."
pip install --upgrade pip
pip install requests beautifulsoup4

# Confirm installation
echo "Installation complete."

# Delete any existing lists
rm url_list.txt

# Run the scraping program to gather all of the links
echo "Scraping 'sci.fi.ncsu.edu/cybersecurity'"
python url_gather.py > url_list.txt

echo ""
echo "Done."