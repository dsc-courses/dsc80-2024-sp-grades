cd utils
python3 fetch_csv.py

cd ..
cd src
jupyter nbconvert --to notebook --execute --inplace calculating-grades.ipynb

echo "Grades have been calculated. You may now push the new data to GitHub and rerun Autograder on Gradescope!"