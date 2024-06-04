apt-get update
apt-get install -y python3 python3-pip

pip3 install -r /autograder/source/requirements.txt

ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts