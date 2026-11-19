import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "student_results.db"
SUBJECTS = ["Python", "SQL_Marks", "ML"]
PASS_MARK = 40

st.set_page_config(page_title="Student Result Analysis", page_icon="🎓", layout="wide")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Students (
                Roll_No INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Department TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Marks (
                Roll_No INTEGER PRIMARY KEY,
                Python INTEGER NOT NULL CHECK(Python BETWEEN 0 AND 100),
                SQL_Marks INTEGER NOT NULL CHECK(SQL_Marks BETWEEN 0 AND 100),
                ML INTEGER NOT NULL CHECK(ML BETWEEN 0 AND 100),
                FOREIGN KEY (Roll_No) REFERENCES Students(Roll_No) ON DELETE CASCADE
            )
        """)
        conn.commit()

def seed_demo_data():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM Students").fetchone()[0]
        if count:
            return
        students = [
            (101, "Aarav Sharma", "CSE"), (102, "Priya Verma", "CSE"),
            (103, "Rohan Gupta", "CSE"), (104, "Sneha Singh", "CSE"),
            (105, "Vikram Yadav", "IT"), (106, "Ananya Mehta", "IT"),
            (107, "Karan Malhotra", "IT"), (108, "Neha Kapoor", "IT"),
            (109, "Aditya Joshi", "ECE"), (110, "Pooja Nair", "ECE"),
            (111, "Rahul Chauhan", "ECE"), (112, "Simran Kaur", "ME"),
            (113, "Manish Dahiya", "ME"), (114, "Isha Rathi", "ME"),
            (115, "Deepak Hooda", "ME")
        ]
        marks = [
            (101,92,88,95),(102,85,90,82),(103,72,65,70),(104,58,62,55),
            (105,78,84,80),(106,91,94,89),(107,35,48,52),(108,66,71,60),
            (109,45,50,42),(110,74,69,77),(111,38,41,33),(112,55,60,58),
            (113,81,76,79),(114,62,58,64),(115,49,44,47)
        ]
        conn.executemany("INSERT INTO Students VALUES (?,?,?)", students)
        conn.executemany("INSERT INTO Marks VALUES (?,?,?,?)", marks)
        conn.commit()

def load_results():
    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT s.Roll_No, s.Name, s.Department,
                   m.Python, m.SQL_Marks, m.ML
            FROM Students s
            LEFT JOIN Marks m ON s.Roll_No = m.Roll_No
            ORDER BY s.Roll_No
        """, conn)
    for col in SUBJECTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Total"] = df[SUBJECTS].sum(axis=1, min_count=1)
    df["Percentage"] = (df["Total"] / 300 * 100).round(2)
    complete = df[SUBJECTS].notna().all(axis=1)
    passed = complete & (df[SUBJECTS].ge(PASS_MARK).all(axis=1))
    df["Result"] = "Pending"
    df.loc[complete & passed, "Result"] = "Pass"
    df.loc[complete & ~passed, "Result"] = "Fail"
    def grade(row):
        if row["Result"] == "Pending": return "—"
        if row["Result"] == "Fail": return "F"
        p = row["Percentage"]
        if p >= 90: return "A+"
        if p >= 80: return "A"
        if p >= 70: return "B"
        if p >= 60: return "C"
        return "D"
    df["Grade"] = df.apply(grade, axis=1)
    return df

init_db()
seed_demo_data()

st.title("🎓 Student Result Analysis System")
st.caption("A database-driven academic performance management and analysis dashboard")
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Students", "Marks Management", "Result Analysis", "Visualizations", "About Project"])
    st.divider()
    st.caption("Demo dataset is preloaded. You can add, edit or delete records.")

df = load_results()
complete_df = df[df["Result"] != "Pending"].copy()

if page == "Dashboard":
    st.subheader("Class Overview")
    total = len(df)
    pending = int((df["Result"] == "Pending").sum())
    passed = int((df["Result"] == "Pass").sum())
    failed = int((df["Result"] == "Fail").sum())
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Students", total)
    c2.metric("Passed", passed)
    c3.metric("Failed", failed)
    c4.metric("Marks Pending", pending)
    if not complete_df.empty:
        avg = complete_df["Percentage"].mean()
        pass_pct = passed / len(complete_df) * 100
        a,b = st.columns(2)
        a.metric("Class Average", f"{avg:.2f}%")
        b.metric("Pass Percentage", f"{pass_pct:.2f}%")
        topper = complete_df.sort_values("Percentage", ascending=False).iloc[0]
        st.success(f"🏆 Current topper: **{topper['Name']}** — {topper['Percentage']:.2f}%")
    st.subheader("Recent Student Records")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Students":
    st.subheader("Student Records")
    with st.expander("➕ Add a student", expanded=False):
        with st.form("add_student"):
            roll = st.number_input("Roll number", min_value=1, step=1)
            name = st.text_input("Student name")
            dept = st.selectbox("Department", ["CSE", "IT", "ECE", "ME", "Other"])
            submitted = st.form_submit_button("Add student")
        if submitted:
            if not name.strip():
                st.error("Please enter the student's name.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute("INSERT INTO Students VALUES (?,?,?)", (int(roll), name.strip(), dept))
                        conn.commit()
                    st.success("Student added.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That roll number already exists.")
    st.dataframe(df[["Roll_No","Name","Department"]], use_container_width=True, hide_index=True)
    st.markdown("#### Update student")
    if not df.empty:
        selected = st.selectbox("Choose roll number to edit", df["Roll_No"].tolist(), key="edit_student")
        row = df[df.Roll_No == selected].iloc[0]
        with st.form("update_student"):
            new_name = st.text_input("Name", value=row["Name"])
            new_dept = st.text_input("Department", value=row["Department"])
            save = st.form_submit_button("Save changes")
        if save:
            with get_connection() as conn:
                conn.execute("UPDATE Students SET Name=?, Department=? WHERE Roll_No=?", (new_name.strip(), new_dept.strip().upper(), int(selected)))
                conn.commit()
            st.success("Student updated.")
            st.rerun()
        st.markdown("#### Delete student")
        confirm = st.checkbox("I understand that deleting a student also deletes their marks.", key="confirm_delete")
        if st.button("Delete selected student", disabled=not confirm):
            with get_connection() as conn:
                conn.execute("DELETE FROM Marks WHERE Roll_No=?", (int(selected),))
                conn.execute("DELETE FROM Students WHERE Roll_No=?", (int(selected),))
                conn.commit()
            st.success("Student and associated marks deleted.")
            st.rerun()

elif page == "Marks Management":
    st.subheader("Enter or Update Marks")
    students = df[["Roll_No","Name"]].to_dict("records")
    if not students:
        st.info("Add a student first.")
    else:
        labels = {f"{x['Roll_No']} — {x['Name']}": x["Roll_No"] for x in students}
        chosen = st.selectbox("Select student", list(labels.keys()))
        roll = labels[chosen]
        current = df[df.Roll_No == roll].iloc[0]
        with st.form("marks_form"):
            p = st.number_input("Python marks", 0, 100, int(current["Python"]) if pd.notna(current["Python"]) else 0)
            s = st.number_input("SQL marks", 0, 100, int(current["SQL_Marks"]) if pd.notna(current["SQL_Marks"]) else 0)
            m = st.number_input("Machine Learning marks", 0, 100, int(current["ML"]) if pd.notna(current["ML"]) else 0)
            save_marks = st.form_submit_button("Save marks")
        if save_marks:
            with get_connection() as conn:
                conn.execute("""INSERT INTO Marks (Roll_No,Python,SQL_Marks,ML) VALUES (?,?,?,?)
                    ON CONFLICT(Roll_No) DO UPDATE SET Python=excluded.Python,
                    SQL_Marks=excluded.SQL_Marks, ML=excluded.ML""", (int(roll),int(p),int(s),int(m)))
                conn.commit()
            st.success("Marks saved successfully.")
            st.rerun()
    st.subheader("Marks Register")
    st.dataframe(df[["Roll_No","Name","Python","SQL_Marks","ML"]], use_container_width=True, hide_index=True)

elif page == "Result Analysis":
    st.subheader("Complete Result Sheet")
    st.caption("Each subject is out of 100. A student passes only when they score at least 40 in every subject.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not complete_df.empty:
        ranked = complete_df.sort_values(["Percentage","Roll_No"], ascending=[False,True]).copy()
        ranked.insert(0, "Rank", ranked["Percentage"].rank(method="min", ascending=False).astype(int))
        st.subheader("Top Three Students")
        st.dataframe(ranked.head(3)[["Rank","Roll_No","Name","Department","Total","Percentage","Grade"]], use_container_width=True, hide_index=True)
        st.subheader("Subject-wise Average")
        st.dataframe(complete_df[SUBJECTS].mean().round(2).rename("Average Marks").to_frame(), use_container_width=True)
        st.subheader("Department-wise Average")
        dept = complete_df.groupby("Department")[SUBJECTS + ["Percentage"]].mean().round(2).sort_values("Percentage", ascending=False)
        st.dataframe(dept, use_container_width=True)

elif page == "Visualizations":
    st.subheader("Performance Visualizations")
    if complete_df.empty:
        st.info("Enter marks for students to generate charts.")
    else:
        chart_data = complete_df.sort_values("Percentage", ascending=False)
        st.plotly_chart(px.bar(chart_data, x="Name", y="Percentage", color="Result", hover_data=["Department","Total"], title="Student-wise Percentage", range_y=[0,100]), use_container_width=True)
        subject_avg = complete_df[SUBJECTS].mean().rename_axis("Subject").reset_index(name="Average Marks")
        st.plotly_chart(px.bar(subject_avg, x="Subject", y="Average Marks", title="Subject-wise Average Marks", range_y=[0,100]), use_container_width=True)
        dept_avg = complete_df.groupby("Department", as_index=False)["Percentage"].mean()
        st.plotly_chart(px.bar(dept_avg, x="Department", y="Percentage", title="Department-wise Average Percentage", range_y=[0,100]), use_container_width=True)
        result_counts = complete_df["Result"].value_counts().rename_axis("Result").reset_index(name="Students")
        st.plotly_chart(px.pie(result_counts, names="Result", values="Students", title="Pass / Fail Distribution", hole=.35), use_container_width=True)
        grade_counts = complete_df["Grade"].value_counts().rename_axis("Grade").reset_index(name="Students")
        st.plotly_chart(px.pie(grade_counts, names="Grade", values="Students", title="Grade Distribution"), use_container_width=True)

elif page == "About Project":
    st.subheader("Project Overview")
    st.write("The Student Result Analysis System stores student details and subject marks, calculates academic results, and summarizes performance through tables and visualizations.")
    st.markdown("""
    **Technologies used**
    - Python — application logic
    - SQLite for the hosted demo; MySQL schema is included for the database implementation described in the report
    - Pandas — result calculations and analysis
    - Streamlit — interactive web interface
    - Plotly — charts and visualizations

    **Result rules**
    - Total marks = Python + SQL + Machine Learning (out of 300)
    - Percentage = (Total / 300) × 100
    - Pass requires at least 40 marks in every subject
    - A+ ≥ 90, A ≥ 80, B ≥ 70, C ≥ 60, D below 60 if passed, F if failed
    """)
    st.info("For a simple public deployment, the app uses a local SQLite database file. The included database.sql provides the MySQL table design from the project report.")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download result sheet (CSV)", csv, "student_results.csv", "text/csv")

st.divider()
st.caption("Student Result Analysis System • Academic Project")
