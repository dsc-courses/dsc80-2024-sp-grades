import pandas as pd
import numpy as np
import re
import json
import sys
import subprocess
import yaml
from datetime import datetime

current_dateTime = datetime.now().strftime("%Y-%m-%d")

sid = json.load(open("/autograder/submission/SID.json", "r"))[
    "SID"
]  # Needed for Gradescope

sys.path.append("${0%/*}")

df = pd.read_csv("../data/grades_for_grade_report.csv").set_index("SID").loc[sid]

stream = open("../configs.yaml", "r")
dictionary = yaml.safe_load(stream)

# Data Loading Fields
GRADES_FILENAME = dictionary["data_path"]["grades_filename"]

# Lab Fields
NUM_LABS = dictionary["labs"]["num_labs"]
MAX_LABS = dictionary["labs"]["max_labs"]

# Project Fields
NUM_PROJECTS = dictionary["projects"]["num_projects"]
MAX_PROJECTS = dictionary["projects"]["max_projects"]

NUM_PROJECT_CHECKPOINTS = dictionary["projects"]["num_checkpoints"]
MAX_PROJECT_CHECKPOINTS = dictionary["projects"]["max_checkpoints"]

# Midterm fields
YES_MIDTERM = dictionary["exams"]["midterm"]["enabled"]
MIDTERM_VERSIONS = dictionary["exams"]["midterm"]["versions"]
MIDTERM_BONUS = dictionary["exams"]["midterm"]["bonus"]
MIDTERM_HAS_BONUS = MIDTERM_BONUS > 0

# Final Fields
YES_FINAL = dictionary["exams"]["final"]["enabled"]
FINAL_VERSIONS = dictionary["exams"]["final"]["versions"]
FINAL_BONUS = dictionary["exams"]["final"]["bonus"]
FINAL_HAS_BONUS = FINAL_BONUS > 0

# Discussion Fields
NUM_DISC_AND_LECT_ATTENDENCE_REQUIRED = dictionary["discussions"][
    "num_discussions_and_lecture_attendence_required"
]

# Number of dropped assignments per category (set to 0 for no drops)
# For example, if NUM_DROPS = 2, then 2 Labs and 2 Homeworks will be dropped
# Note: Set this to 0 until the end of the quarter
NUM_DROPS = dictionary["drop_policy"]["num_drops"]

OVERALL_EC = dictionary["extra_credit"]["overall"]

DROPS = NUM_DROPS > 0

CURRENT_TOTAL_POSSIBLE_SCORE = df["Current Max Possible Score"].max()

ASSIGNMENT_WEIGHTS = dictionary["assignment_weights"]
DISCUSSION_ASSIGNMENT_WEIGHTS = dictionary["discussion_assignment_weights"]

DATE = current_dateTime

DECIMAL_ROUND_PLACE = 4


def even_round_str(n, round_place=DECIMAL_ROUND_PLACE):
    rounded = str(np.round(n, round_place))
    if len(rounded) < round_place + 2:
        return str(rounded) + "0" * (round_place + 2 - len(rounded))
    else:
        return str(rounded)


def output_letter_grade(df, gs_output):
    output = [f"{df['Name']}\n{df['Email']}\n{sid}\nlast updated on {DATE}\n"]
    output = np.append(
        output,
        [
            f"Your overall score in the course is {np.round(df['Overall Score'], 3)}%.\nNote that grades **will not** be rounded."
        ],
    )

    output = np.append(
        output,
        [
            f"Your current percentage based on your scores so far is {np.round(df['Overall Score'], DECIMAL_ROUND_PLACE)} / {np.round(CURRENT_TOTAL_POSSIBLE_SCORE, DECIMAL_ROUND_PLACE)} * 100 = {np.round(df['Current Score'], DECIMAL_ROUND_PLACE)}%."
        ],
    )

    if not DROPS:
        output = np.append(
            output,
            [
                f"Also note that this grade report accounts for dropped assignments but no for extra credit yet."
            ],
        )
    else:
        output = np.append(
            output,
            [
                "This accounts for dropped assignments – the lowest lab score was dropped"
            ],
        )

    gs_output["tests"].append(
        {
            "name": "Overall Score",
            "score": 0,
            "max_score": 0,
            "output": "\n".join(output),
            "visibility": "after_published",
        }
    )


def make_assignment_string(assignment):
    kind = assignment.split(" ")[0]
    exists = df.loc[assignment + " - Max Points"] != 0
    if exists:
        output = f'{assignment}: {even_round_str(df.loc[assignment + " Final Grade"])}'
        output += f' ({df.loc[assignment]} / {df.loc[assignment + " - Max Points"]})'
        if DROPS and "Lab" in assignment:
            if assignment in df[f"Dropped {kind}s"]:
                output += " [Dropped]"
        # if df[assignment + ' Slip Days'] > 0:
        #     if assignment in df['Accepted Late Assignments']:
        #         output += f' [{int(df[assignment + " Slip Days"])} slip day(s) used]'
    else:
        output = f"{assignment}: 0 (Not yet released or graded)"
        # if DROPS and 'Lab' in assignment:
        #     if assignment in df[f'Dropped {kind}s']:
        #         output += ' [Dropped]'

    return output


def output_lab_grades(df, gs_output):
    lab_score = df["Lab Average"]
    lab_weight = int(ASSIGNMENT_WEIGHTS["lab"] * 100)
    output = [
        f"Labs are worth {lab_weight}% of your grade. There are {MAX_LABS} labs total.\n"
    ]
    for lab in range(1, MAX_LABS + 1):
        if lab <= NUM_LABS:
            output = np.append(output, make_assignment_string(f"Lab {lab}"))
        else:
            output = np.append(output, f"Lab {lab}: 0 (not yet released or graded)")
    output = np.append(output, [f"Overall: {even_round_str(df.loc['Lab Average'])}"])
    gs_output["tests"].append(
        {
            "name": "Labs",
            "score": float(lab_score) * lab_weight,
            "max_score": lab_weight,
            "output": "\n".join(output),
            "visibility": "after_published",
        }
    )


def output_project_grades(df, gs_output):
    project_score = df.loc["Project Average"]
    project_weight = int(ASSIGNMENT_WEIGHTS["project"] * 100)
    output = [
        f"Projects are worth {project_weight}% of your grade. There are {MAX_PROJECTS} projects. There are no drops. \nProjects 1, 2, and 3 are each worth 6% of your overall grade, and Project 4 is worth 12%, for a total of 30%.\n"
    ]
    for project in range(1, MAX_PROJECTS + 1):
        # if project == 4:
        #     project_str = '4A'
        # elif project == 5:
        #     project_str = '4B'
        # else:
        project_str = str(project)
        if project <= NUM_PROJECTS:

            output = np.append(output, make_assignment_string(f"Project {project_str}"))
        else:
            output = np.append(
                output, f"Project {project_str}: 0 (not yet released or graded)"
            )

    output = np.append(
        output, [f"Overall: {even_round_str(df.loc['Project Average'])}"]
    )
    gs_output["tests"].append(
        {
            "name": "Projects",
            "score": float(project_score) * project_weight,
            "max_score": project_weight,
            "output": "\n".join(output),
            "visibility": "after_published",
        }
    )


def output_project_checkpoints(df, gs_output):
    checkpoint_score = df.loc["Project Checkpoint Average"]
    checkpoint_weight = int(ASSIGNMENT_WEIGHTS["project_checkpoint"] * 100)
    output = [
        f"Project Checkpoints are worth {checkpoint_weight}% of your grade. There are {MAX_PROJECT_CHECKPOINTS} project checkpoints. There are no drops. \nThe checkpoints for Projects 1, 2, and 3 are each worth 1% of your overall grade, and the checkpoint for Project 4 is worth 2%, for a total of 5%.\n"
    ]
    for checkpoint in range(1, MAX_PROJECT_CHECKPOINTS + 1):
        # if checkpoint == 4:
        #     checkpoint_str = '4A'
        # elif checkpoint == 5:
        #     checkpoint_str = '4B'
        # else:
        checkpoint_str = str(checkpoint)
        if checkpoint <= NUM_PROJECT_CHECKPOINTS:
            output = np.append(
                output, make_assignment_string(f"Project {checkpoint_str} Checkpoint")
            )
        else:
            output = np.append(
                output, f"Project {checkpoint_str}: 0 (not yet released or graded)"
            )

    output = np.append(
        output, [f"Overall: {even_round_str(df.loc['Project Checkpoint Average'])}"]
    )
    gs_output["tests"].append(
        {
            "name": "Project Checkpoints",
            "score": float(checkpoint_score) * checkpoint_weight,
            "max_score": checkpoint_weight,
            "output": "\n".join(output),
            "visibility": "after_published",
        }
    )


def output_midterm_exam_grade(df, gs_output):
    output = f"""The Midterm Exam is worth 20% of your grade.
- Your score on the original Midterm Exam was {even_round_str(df.loc["Midterm Exam Grade Pre-EC"])}. 
    Since the original Midterm Exam had a mean of {even_round_str(df.loc["Midterm Mean"])} and SD of {even_round_str(df.loc["Midterm std"])},
    your score as a z-score is {even_round_str(df.loc["Midterm Z-Score"])}.
- On the Final there will be questions to Redeem your Midterm Exam score. 
    If your Z-Score higher on these questions than your original Midterm Exam score, your Midterm Exam score will increase.
    If you score lower, your Midterm Exam score will not change."""

    # .format(
    #     A=,
    #     B=,
    #     C=,
    #     D=,
    #     E=even_round_str(df.loc["Midterm Exam Raw Post-Redemption Pre-EC"]),
    #     F=even_round_str(df.loc["Midterm Exam Raw Post-Redemption Post-EC"]),
    #     mean=even_round_str(df.loc['Midterm Mean']),
    #     sd=even_round_str(df.loc['Midterm std'])
    gs_output["tests"].append(
        {
            "name": "Midterm Exam",
            "score": float(df["Midterm Exam Grade Post-Redemption Post-EC"] * 15),
            "max_score": 20,
            "output": output,  #'\n'.join(output),
            "visibility": "after_published",
        }
    )


def output_final_exam_grade(df, gs_output):
    output = ["The Final Exam is worth 30% of your grade."]
    output = np.append(
        output,
        f'Score: {even_round_str(df.loc["Final Exam Raw"])} ({df.loc["Final Exam"]} / {df.loc["Final Exam - Max Points"]})',
    )
    gs_output["tests"].append(
        {
            "name": "Final Exam",
            "score": float(df["Final Exam Raw"] * 25),
            "max_score": 30,
            "output": "\n".join(output),
            "visibility": "after_published",
        }
    )


gs_output = {"tests": []}
output_letter_grade(df, gs_output)
# output_slip_day_summary(df, gs_output)
if NUM_LABS > 0:
    output_lab_grades(df, gs_output)
if NUM_PROJECTS > 0:
    output_project_grades(df, gs_output)
    output_project_checkpoints(df, gs_output)

if YES_MIDTERM:
    output_midterm_exam_grade(df, gs_output)

if YES_FINAL:
    output_final_exam_grade(df, gs_output)


out_path = "/autograder/results/results.json"
with open(out_path, "w") as f:
    f.write(json.dumps(gs_output))
