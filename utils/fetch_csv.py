import requests
import os
from bs4 import BeautifulSoup
import yaml

stream = open("../configs.yaml", 'r')
dictionary = yaml.safe_load(stream)

username, password = dictionary['gradescope_credentials']['email'], dictionary['gradescope_credentials']['password']
course_id = dictionary['course_info']['course_id']
roster_path = dictionary['course_info']['roster_path']
YES_FINAL = dictionary['exams']['final']['enabled']
if YES_FINAL:
    container_id = dictionary['exams']['final']['container_id']
    container_path = dictionary['exams']['final']['container_path']

def get_csv(email, pswd):
    session = requests.Session()
    init_resp = session.get("https://www.gradescope.com/")
    parsed_init_resp = BeautifulSoup(init_resp.text, 'html.parser')
    for form in parsed_init_resp.find_all('form'):
        if form.get("action") == "/login":
            for inp in form.find_all('input'):
                if inp.get('name') == "authenticity_token":
                    auth_token = inp.get('value')

    login_data = {
        "utf8": "✓",
        "session[email]": email,
        "session[password]": pswd,
        "session[remember_me]": 0,
        "commit": "Log In",
        "session[remember_me_sso]": 0,
        "authenticity_token": auth_token,
    }
    login_resp = session.post("https://www.gradescope.com/login", params=login_data)
    if len(login_resp.history) != 0:
        if login_resp.history[0].status_code == requests.codes.found:
            print('Login successful')
            account_resp = session.get(f"https://www.gradescope.com/courses/{course_id}/gradebook.csv")
            
            # Ensure the request was successful
            if account_resp.status_code == 200:
                print('CSV download successful')
                file_path = roster_path
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Open the file in write mode
                with open(file_path, 'wb') as f:
                    # Write the content of the response to the file
                    f.write(account_resp.content)
                print(f'CSV file saved to {file_path}')

            if YES_FINAL:
                # get the zip file
                final_resp = session.get(f"https://www.gradescope.com/courses/{course_id}/assignment_containers/{container_id}/scores/csv.zip")
                # Ensure the request was successful
                if final_resp.status_code == 200:
                    print('Final exam download successful')
                    file_path = container_path
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(final_resp.content)
                    print(f'Final exam file saved to {file_path}')

                    # unzip the file
                    import zipfile
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(file_path[:-4])
                    # rm the zip file
                    os.remove(file_path)
                    print(f'Final exam file unzipped to {file_path[:-4]}')
                    


        return True
    else:
        print('Login failed')
        return False

if __name__=="__main__":
    get_csv(username, password)
