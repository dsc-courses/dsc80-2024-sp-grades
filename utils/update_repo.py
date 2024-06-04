import yaml

# Read the configs.yaml file
with open('../configs.yaml', 'r') as file:
    config_data = yaml.safe_load(file)
    github_repo = config_data['github_repo']

# Read the run_autograder script
with open('../autograder/run_autograder', 'r') as file:
    lines = file.readlines()

# Replace the line containing the git clone command
with open('../autograder/run_autograder', 'w') as file:
    for line in lines:
        if line.strip().startswith('git clone git@github.com:'):
            # Construct the new clone command with the repo from configs.yaml
            new_line = f"git clone git@github.com:{github_repo} > /autograder/results/log.txt\n"
            file.write(new_line)
            print(f"Updated the git repo to {github_repo}")
        elif line.strip().startswith('bash'):
            new_line = f"bash {(github_repo.split('/')[1]).split('.')[0]}/run"
            file.write(new_line)
            print(f"Updated the run script to {new_line}")
        else:
            file.write(line)
