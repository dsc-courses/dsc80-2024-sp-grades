#!/bin/bash

# Check if the configs directory exists
if [[ ! -d ./autograder ]]; then
    echo "The autograder directory does not exist. Creating it now..."
    mkdir ./autograder
fi

# Replace new repo name

cd utils
python3 update_repo.py
cd ..

# Check if the ~/.ssh/id_rsa file exists
if [[ ! -f ~/.ssh/id_rsa ]]; then
    echo "The id_rsa file does not exist in the ~/.ssh directory. Please create it and try again."
    exit 1
fi

# Copy the id_rsa file to the configs directory
cp ~/.ssh/id_rsa ./autograder/id_rsa

# Set strict permissions on the copied id_rsa file
chmod 600 ./autograder/id_rsa

echo "id_rsa has been copied to the autograder directory."

cd autograder

# Create the autograder zip file
zip -r autograder.zip ./*

rm id_rsa

echo "Autograder zip file has been created. You may now upload autograder.zip to Gradescope!"

cd ..

cd utils
python fetch_csv.py
python submit.py
