import pandas as pd
import numpy as np
import re
import json
import sys
import subprocess
import yaml
from datetime import datetime
current_dateTime = datetime.now().strftime("%Y-%m-%d")

metadata = json.load(open('/autograder/submission_metadata.json', 'r')) # Needed for Gradescope
import os

files = os.listdir('/autograder/submission')
for file in files:
    print(file)
sid =  json.load(open('/autograder/submission/SID.json', 'r'))["SID"] # Needed for Gradescope