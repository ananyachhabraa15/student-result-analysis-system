# Student Result Analysis System

A Streamlit-based academic result management and analysis application based on the supplied major-project report.

## Features
- Add, view, update and delete student records
- Enter and update marks for Python, SQL and Machine Learning
- Automatic total, percentage, pass/fail result and grade calculation
- Topper and top-three ranking
- Subject-wise and department-wise averages
- Interactive student, subject, department, pass/fail and grade charts
- CSV export of the result sheet

## Run locally
1. Install Python 3.9 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```

The hosted demo uses SQLite so it can run on Streamlit Community Cloud without requiring a separately hosted database server. The `database.sql` file contains the MySQL schema corresponding to the report's CollegeDB design. The application creates a local SQLite database and loads sample records on first run.

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Open https://share.streamlit.io/
3. Sign in with GitHub and authorize access to the repository.
4. Select this repository, branch `main`, and main file path `app.py`.
5. Click **Deploy**.

## Database design
- `Students(Roll_No, Name, Department)`
- `Marks(Roll_No, Python, SQL_Marks, ML)`
- Marks.Roll_No references Students.Roll_No.
- A student passes only if all three subject marks are at least 40.
- Percentage = (Total / 300) × 100.

## Important note
The PDF report describes a console-based Python/MySQL application. This repository provides a web-dashboard implementation of the same core workflow for a clearer live demonstration. If your faculty requires the exact MySQL connector implementation, use the included MySQL schema and adapt the connection layer to a hosted MySQL service.
