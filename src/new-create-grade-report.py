import pandas as pd
import numpy as np
import re
import json
import sys
import subprocess
import yaml
from datetime import datetime
current_dateTime = datetime.now().strftime("%Y-%m-%d")


# metadata = json.load(open('/autograder/submission_metadata.json', 'r')) # Needed for Gradescope
# import os

# files = os.listdir('/autograder/submission')
# for file in files:
#     print(file)
sid =  json.load(open('/autograder/submission/SID.json', 'r'))["SID"] # Needed for Gradescope


sys.path.append("${0%/*}")
# subprocess.run('ls')

df = pd.read_csv('data/grades_for_grade_report.csv').set_index('Student ID').loc[sid]

stream = open("configs.yaml", 'r')
dictionary = yaml.safe_load(stream)

# Data Loading Fields
GRADES_FILENAME = dictionary['data_path']['grades_filename']
# ROSTER_FILENAME = 'sheets/dsc10-sp23-roster-final.csv'
# ATTENDANCE_PATH = 'sheets/discussions'

# Lab Fields
NUM_LABS = dictionary['labs']['num_labs']
MAX_LABS = dictionary['labs']['max_labs']

# Project Fields
NUM_PROJECTS = dictionary['projects']['num_projects']
MAX_PROJECTS = dictionary['projects']['max_projects']

NUM_PROJECT_CHECKPOINTS = dictionary['projects']['num_checkpoints']
MAX_PROJECT_CHECKPOINTS = dictionary['projects']['max_checkpoints']


# Midterm fields
YES_MIDTERM = dictionary['exams']['midterm']['enabled']
MIDTERM_VERSIONS = dictionary['exams']['midterm']['versions']
MIDTERM_BONUS = dictionary['exams']['midterm']['bonus']

# Final Fields
YES_FINAL = dictionary['exams']['final']['enabled']
FINAL_VERSIONS = dictionary['exams']['final']['versions']


# Discussion Fields
NUM_DI = dictionary['discussions']['num_dis']
print(NUM_DI)
MAX_DI = dictionary['discussions']['max_dis']

# Number of dropped assignments per category (set to 0 for no drops)
# For example, if NUM_DROPS = 2, then 2 Labs and 2 Homeworks will be dropped
# Note: Set this to 0 until the end of the quarter
NUM_DROPS = dictionary['drop_policy']['num_drops']

OVERALL_EC = dictionary['extra_credit']['overall']

DROPS = NUM_DROPS > 0

CURRENT_TOTAL_POSSIBLE_SCORE = df['Current Max Possible Score'].max()

DATE = current_dateTime

DECIMAL_ROUND_PLACE = 4
def even_round_str(n):
    rounded = str(np.round(n, DECIMAL_ROUND_PLACE))
    if len(rounded) < DECIMAL_ROUND_PLACE + 2:
        return str(rounded) + '0' * (DECIMAL_ROUND_PLACE + 2 - len(rounded))
    else:
        return str(rounded)

def output_letter_grade(df, gs_output):
    # delta = np.round(CURRENT_TOTAL_POSSIBLE_SCORE-df['Overall Score'], 3)
    # percent_of_curr_points = df['Current Score']
    # if delta < 0:
    #     max_pos = np.round(df['Overall Score'], 3)
    # else:
    #     max_pos = 100 - delta
    # score_no_ec = delta - df['Discussion Raw'] * 0.3
    # section = re.findall('---(\w)\w+-', df['Sections'])[0].upper()
    # output = [f"{df['Name']}\n{df['Email']}\n{sid}\nSection {section}00\n"]
    output = [f"{df['Name']}\n{df['Email']}\n{sid}\nlast updated on {DATE}\n"]
    # output = np.append(output, [f"Your overall score in the course is {np.round(df['Overall Score'], 3)}% out of a maximum possible score of {round(df['Max Score'], 3)}%.\nThis means you have obtained {np.round(df['Overall Score'], 3)} / {round(df['Max Score'], 3)} = {round(100*(df['Overall Score']/df['Max Score']), 3)}% of the points available so far.\nNote that grades **will not** be rounded.\n"])

    # output = np.append(output, [f"Before every assignment/exam is graded, the below interpretation is more suitable:\nYou have currently lost {np.round(df['Overall Loss'], 3)}% of the total grade.\n"])
    output = np.append(output, [f"Your overall score in the course is {np.round(df['Overall Score'], 3)}%.\nNote that grades **will not** be rounded."])
    
    # if df["Grade Option"] == "P":
    #     output = np.append(output, f"Letter Grade: {df['Letter Grade']} (but since you're taking the class P/NP, we will submit {df['Final_Assigned_Egrade']})")
    # else:
    #     output = np.append(output, f"Letter Grade: {df['Letter Grade']}")
    
    output = np.append(output, [f"Your current percentage based on your scores so far is {np.round(df['Overall Score'], DECIMAL_ROUND_PLACE)} / {np.round(TOTAL_POSSIBLE_SCORE, DECIMAL_ROUND_PLACE)} * 100 = {np.round(100*df['Current Score'], DECIMAL_ROUND_PLACE)}%."])
    # output = np.append(output, [f"Your maximum possible score in the course is {max_pos}% if you get perfect scores on all remaining assignments (not including extra credit from discussion)."])
    
    if not DROPS:
        output = np.append(output, [f"Also note that this grade report accounts for dropped assignments but no for extra credit yet."])
    else:
        output = np.append(output, ["This accounts for dropped assignments – the lowest lab score was dropped"])
        # – and all possible extra credit (discussion attendance, midterm SETs bonus, final SETs bonus, and Lab 9).



    # output = np.append(output, ["The Discussion 10 Extra Credit Opportunities are not included in this grade report yet."])

    #output = np.append(output, [f"Your overall score in the course is {np.round(df['Overall Score'], 4)}%.\nLetter Grade: {df['Letter Grade']}"])
    # output = np.append(output, [f"\nLetter Grade: {df['Letter Grade']}"])

    gs_output['tests'].append({
        'name': 'Overall Score',
        'score': 0,
        'max_score': 0,
        'output': '\n'.join(output),
        'visibility': 'after_published'
    })

# def output_slip_day_summary(df, gs_output):
#     output = f'You used {int(df["Used Slip Days"])} slip day(s), and have {int(df["Slip Days Remaining"])} remaining.'
#     late_accepted = df['Accepted Late Assignments'].replace('[', '').replace("'", '').replace(']', '').split(', ')
#     not_accepted = df['Late Assignments Past 7 Slip Days'].replace('[', '').replace("'", '').replace(']', '').split(', ')
    
#     if late_accepted[0] != '':
#         output += '\n\nYou used slip days on the following assignments:\n'
#         for assignment in late_accepted:
#             output += f'{assignment}: {int(df[assignment + " Slip Days"])}\n'
    
#     if not_accepted[0] != '':
#         output += '\nYou received 0s on the following assignments since you ran out of slip days:\n'
#         for assignment in not_accepted:
#             output += f'{assignment}: Needed {int(df[assignment + " Slip Days"])} more slip day(s)\n'
    
#     gs_output['tests'].append({
#         'name': 'Slip Day Summary',
#         'score': 0,
#         'max_score': 0,
#         'output': output,
#         'visibility': 'after_published'
#     })

def make_assignment_string(assignment):
    kind = assignment.split(' ')[0]
    exists = df.loc[assignment + ' - Max Points'] != 0
    if exists:
        output = f'{assignment}: {even_round_str(df.loc[assignment + " Raw"])}'
        output += f' ({df.loc[assignment]} / {df.loc[assignment + " - Max Points"]})'
        if DROPS and 'Lab' in assignment:
            if assignment in df[f'Dropped {kind}s']:
                output += ' [Dropped]'
        # if df[assignment + ' Slip Days'] > 0:
        #     if assignment in df['Accepted Late Assignments']:
        #         output += f' [{int(df[assignment + " Slip Days"])} slip day(s) used]'
    else:
        output = f'{assignment}: 0 (Not yet released or graded)'
        # if DROPS and 'Lab' in assignment:
        #     if assignment in df[f'Dropped {kind}s']:
        #         output += ' [Dropped]'
            
    return output

def output_lab_grades(df, gs_output):
    lab_score = df['Lab Total']
    output = [f'Labs are worth 20% of your grade. There are {MAX_LABS} labs total.\n']
    for lab in range(1, MAX_LABS+1):
        if lab <= NUM_LABS:
            output = np.append(output, make_assignment_string(f'Lab {lab}'))
        else:
            output = np.append(output, f'Lab {lab}: 0 (not yet released or graded)')
    output = np.append(output, [f"Overall: {even_round_str(df.loc['Lab Total'])}"])
    gs_output['tests'].append({
        'name': 'Labs',
        'score': float(lab_score) * 20,
        'max_score': 20,
        'output': '\n'.join(output),
        'visibility': 'after_published'
    })

def output_project_grades(df, gs_output):
    project_score = df.loc['Project Total']
    output = [f'Projects are worth 25% of your grade. There are {MAX_PROJECTS} projects. There are no drops. \nProjects 1, 2, and 3 are each worth 6% of your overall grade, and Project 4 is worth 12%, for a total of 30%.\n']
    for project in range(1, MAX_PROJECTS+1):
        # if project == 4:
        #     project_str = '4A'
        # elif project == 5:
        #     project_str = '4B'
        # else:
        project_str = str(project)
        if project <= NUM_PROJECTS:
        
            output = np.append(output, make_assignment_string(f'Project {project_str}'))
        else:
            output = np.append(output, f'Project {project_str}: 0 (not yet released or graded)')

    output = np.append(output, [f"Overall: {even_round_str(df.loc['Project Total'])}"])
    gs_output['tests'].append({
        'name': 'Projects',
        'score': float(project_score) * 25,
        'max_score': 25,
        'output': '\n'.join(output),
        'visibility': 'after_published'
    })

def output_project_checkpoints(df, gs_output):    
    checkpoint_score = df.loc['Project Checkpoint Total']
    output = [f'Project Checkpoints are worth 5% of your grade. There are {MAX_PROJECT_CHECKPOINTS} project checkpoints. There are no drops. \nThe checkpoints for Projects 1, 2, and 3 are each worth 1% of your overall grade, and the checkpoint for Project 4 is worth 2%, for a total of 5%.\n']
    for checkpoint in range(1, MAX_PROJECT_CHECKPOINTS+1):
        # if checkpoint == 4:
        #     checkpoint_str = '4A'
        # elif checkpoint == 5:
        #     checkpoint_str = '4B'
        # else:
        checkpoint_str = str(checkpoint)
        if checkpoint <= NUM_PROJECT_CHECKPOINTS:
            output = np.append(output, make_assignment_string(f'Project {checkpoint_str} (Checkpoint)'))
        else:
            output = np.append(output, f'Project {checkpoint_str}: 0 (not yet released or graded)')

    output = np.append(output, [f"Overall: {even_round_str(df.loc['Project Checkpoint Total'])}"])
    gs_output['tests'].append({
        'name': 'Project Checkpoints',
        'score': float(checkpoint_score) * 5,
        'max_score': 5,
        'output': '\n'.join(output),
        'visibility': 'after_published'
    })

def output_midterm_exam_grade(df, gs_output):    
    # output = ['The Midterm Exam is worth 15% of your grade.']
    # output = np.append(output, f'Score: {even_round_str(df.loc["Midterm Exam Raw"])} ({df.loc["Midterm Exam"]} / {df.loc["Midterm Exam - Max Points"]} + {MIDTERM_BONUS} bonus points)')
    # # if df['Midterm Clobbered']:
    # #     output = np.append(output, f"Since you made a special arrangement to replace your Midterm Exam score with your Final Exam score, the score you see above is the same in standard units as your Final Exam score.")

    # output = np.append(output, f"The redemption questions on the final exam are marked with \"(R)\".")

    # output = np.append(output, f'Midterm Exam z-score: {even_round_str(df.loc["Midterm z-score"])}; Redemption z-score: {even_round_str(df.loc["Midterm Redemption Part z-score"])}; Midterm std: {even_round_str(df.loc["Midterm std"])}; Midterm mean: {even_round_str(df.loc["Midterm Mean"])}')

    # if df['Redemption Successful']:
    #     output = np.append(output, f"Redemption Successful: new midterm score is {even_round_str(df['Midterm Final Raw'])} = {even_round_str(df['Midterm Redemption Part z-score'])} * {even_round_str(df.loc['Midterm std'])} + {even_round_str(df.loc['Midterm Mean'])}.")
    # else:
    #     output = np.append(output, f"Redemption Unsuccessful: your new z-score is not higher than your old z-score.")

    # output = np.append(output, f'Midterm Final Score: {even_round_str(df.loc["Midterm Final Raw"])}')

    C=even_round_str(df.loc["Redemption Score"]), 
    D=even_round_str(df.loc["Midterm Redemption Part z-score"]), 

    output = f"""The Midterm Exam is worth 20% of your grade.
- Your score on the original Midterm Exam, without the 2 point (2.5%) bonus we gave everyone on the Midterm Exam, was {even_round_str(df.loc["Midterm Exam Raw Pre-EC"])}. 
    Since the original Midterm Exam had a mean of {even_round_str(df.loc["Midterm Mean"])} and SD of {even_round_str(df.loc["Midterm std"])},
    your score as a z-score is {even_round_str(df.loc["Midterm z-score"])}.
- Your score on the redemption questions on the Final Exam (Questions 1-3) was {even_round_str(df.loc["Redemption Score"])}. 
    Converted to a z-score, this is {even_round_str(df.loc["Midterm Redemption Part z-score"])}."""

    if df.loc["Midterm Redemption Part z-score"] > df.loc["Midterm z-score"]:
        output += f'''

Congrats! Since your redemption z-score is higher than your original z-score, your Midterm Exam score will increase.
Specifically, it will increase from {even_round_str(df.loc["Midterm Exam Raw Pre-EC"])} to {even_round_str(df.loc["Midterm Mean"])} + ({even_round_str(df.loc["Midterm Redemption Part z-score"])}) * {even_round_str(df.loc["Midterm std"])} = {even_round_str(df.loc["Midterm Exam Raw Post-Redemption Pre-EC"])}.
'''
        
    else:
        output += f'''

Since your redemption z-score is lower than your original z-score, your Midterm Exam score will not change.
'''
    
    output += f'''
Including the 2 point (2.5% bonus), your Midterm Exam score will be entered as {even_round_str(df.loc["Midterm Exam Raw Post-Redemption Pre-EC"])} + 0.025 = {even_round_str(df.loc["Midterm Exam Raw Post-Redemption Post-EC"])}.
'''

#.format(
#     A=, 
#     B=, 
#     C=, 
#     D=, 
#     E=even_round_str(df.loc["Midterm Exam Raw Post-Redemption Pre-EC"]), 
#     F=even_round_str(df.loc["Midterm Exam Raw Post-Redemption Post-EC"]),
#     mean=even_round_str(df.loc['Midterm Mean']),
#     sd=even_round_str(df.loc['Midterm std'])
    gs_output['tests'].append({
        'name': 'Midterm Exam',
        'score': float(df['Midterm Exam Raw Post-Redemption Post-EC'] * 15),
        'max_score': 15,
        'output': output, #'\n'.join(output),
        'visibility': 'after_published'
    })

def output_final_exam_grade(df, gs_output):  
    output = ['The Final Exam is worth 30% of your grade.']
    output = np.append(output, f'Score: {even_round_str(df.loc["Final Exam Raw"])} ({df.loc["Final Exam"]} / {df.loc["Final Exam - Max Points"]})')
    gs_output['tests'].append({
        'name': 'Final Exam',
        'score': float(df['Final Exam Raw'] * 25),
        'max_score': 25,
        'output': '\n'.join(output),
        'visibility': 'after_published'
    })

# def output_disc_grades(df, gs_output):
#     disc_score = df.loc['Discussion Raw']

    
#     di_weeks = eval(df['Discussion Weeks'])
#     # print(di_weeks)
#     # print(len(di_weeks))
#     credit_received = [str(i + 1) for i in range(len(di_weeks)) if di_weeks[i] != 0]
#     print(credit_received)

#     # TODO Remove this because it only mattered for the first grade report
#     attended = str(df.loc['Discussion Raw'])
#     if attended == '0':
#         disc_text = "So far, you haven't attended any discussions or turned in any lab reflections.\n"
#     else:
#         # disc_text = ""
#         disc_text = f"Of the first {NUM_DI} discussions and currently graded lab reflections, you got credit for: Week(s) {', '.join(credit_received)}."

#     # if not isinstance(df["Discussions Attended"], str):
#     #     disc_text = "So far, you haven't attended any discussions or turned in any lab reflections.\n"
#     # else:
#     #     num_disc_attended = len(df["Discussions Attended"].split(','))

#     output = [f'Each week that you submit a lab, attended discussion, and submit the COMPLETE corresponding lab reflection form,\nwe will add 0.2% of extra credit to your overall grade at the end of the quarter.\n']
#     output = np.append(output, disc_text)
#     output = np.append(output, f"This will add {round(0.2*disc_score, 2)}% extra credit to your total grade at the end of the quarter.\n")
#     output = np.append(output, 'Since over 80% of the course filled out both SETs and the End of Quarter Survey, we added an extra 1% to your overall grade.')
#     gs_output['tests'].append({
#         'name': 'Extra Credits',
#         'score': float(disc_score)*0.2 + float(OVERALL_EC) * 100,
#         'max_score': 0,
#         'output': '\n'.join(output),
#         'visibility': 'after_published'
#     })

# def output_ec_grades(df, gs_output):
#     output = ['Since over 80% of the course filled out both SET and the End of Quarter Survey, everyone earned an extra 1%.']
#     print(OVERALL_EC)
#     print(type(OVERALL_EC))
#     gs_output['tests'].append({
#         'name': 'Extra Credit',
#         'score': float(OVERALL_EC) * 100,
#         'max score': 0,
#         'output': '\n'.join(output),
#         'visibility': 'after_published'
#     })

gs_output = {'tests': []}
output_letter_grade(df, gs_output)
# output_slip_day_summary(df, gs_output)
if NUM_LABS > 0:
    output_lab_grades(df, gs_output)
if NUM_PROJECTS > 0:
    output_project_grades(df, gs_output)
    output_project_checkpoints(df, gs_output)
    
output_midterm_exam_grade(df, gs_output)
output_final_exam_grade(df, gs_output)

# output_ec_grades(df, gs_output)

# output_disc_grades(df, gs_output)



# # Comment this cell out before exporting
# for i in range(len(gs_output['tests'])):
#     print(gs_output['tests'][i]['output'], '\n')
#     print('---')

out_path = '/autograder/results/results.json'
with open(out_path, 'w') as f:
    f.write(json.dumps(gs_output))

