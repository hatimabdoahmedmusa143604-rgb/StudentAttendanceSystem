
import streamlit as st
import pandas as pd
import os
from datetime import date

# Page Configuration
st.set_page_config(
    page_title="Student Attendance Management System",
    page_icon="🎓",
    layout="wide"
)

# Create Data Folder
os.makedirs("data", exist_ok=True)

# File Paths
STUDENTS_FILE = "data/students.csv"
ATTENDANCE_FILE = "data/attendance.csv"

# Load Data
def load_data(file_path, columns):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        for col in columns:
            if col not in df.columns:
                df[col] = ""

        return df[columns]

    return pd.DataFrame(columns=columns)


students = load_data(
    STUDENTS_FILE,
    ["Student ID", "Name", "Department", "Email"]
)

attendance = load_data(
    ATTENDANCE_FILE,
    ["Student ID", "Name", "Date", "Status"]
)


# Save Data
def save_data(data, file_path):
    data.to_csv(file_path, index=False)


# Application Title
st.title("🎓 Student Attendance Management System")

st.write(
    "A simple application to manage student details and attendance."
)


# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Manage Students",
        "Mark Attendance",
        "Attendance Records",
        "Reports"
    ]
)


# Dashboard
if page == "Dashboard":

    st.header("📊 Dashboard")

    total_students = len(students)

    today = str(date.today())

    today_records = attendance[
        attendance["Date"].astype(str) == today
    ]

    present = len(
        today_records[today_records["Status"] == "Present"]
    )

    absent = len(
        today_records[today_records["Status"] == "Absent"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total_students)
    col2.metric("Present Today", present)
    col3.metric("Absent Today", absent)

    st.subheader("Welcome")

    st.info(
        "Use the sidebar to manage students and attendance."
    )


# Manage Students
elif page == "Manage Students":

    st.header("👨‍🎓 Manage Students")

    st.subheader("Add New Student")

    with st.form("student_form"):

        student_id = st.text_input("Student ID")

        name = st.text_input("Student Name")

        department = st.selectbox(
            "Department",
            [
                "CSE",
                "AI/ML",
                "Data Science",
                "Cyber Security",
                "Other"
            ]
        )

        email = st.text_input("Email Address")

        submit = st.form_submit_button("Add Student")

        if submit:

            if not student_id or not name:

                st.error(
                    "Please enter Student ID and Name."
                )

            elif student_id in students["Student ID"].astype(str).values:

                st.error("Student ID already exists.")

            else:

                new_student = pd.DataFrame([{
                    "Student ID": student_id,
                    "Name": name,
                    "Department": department,
                    "Email": email
                }])

                students = pd.concat(
                    [students, new_student],
                    ignore_index=True
                )

                save_data(students, STUDENTS_FILE)

                st.success(
                    "Student added successfully!"
                )

                st.rerun()

    st.subheader("Student List")

    st.dataframe(
        students,
        use_container_width=True
    )


# Mark Attendance
elif page == "Mark Attendance":

    st.header("📝 Mark Student Attendance")

    if students.empty:

        st.warning("Please add students first.")

    else:

        selected_date = st.date_input(
            "Select Attendance Date",
            date.today()
        )

        student_options = (
            students["Student ID"].astype(str).tolist()
        )

        selected_id = st.selectbox(
            "Select Student",
            student_options
        )

        student = students[
            students["Student ID"].astype(str) == selected_id
        ].iloc[0]

        st.write("Student Name:", student["Name"])

        status = st.radio(
            "Attendance Status",
            ["Present", "Absent"],
            horizontal=True
        )

        if st.button("Save Attendance"):

            attendance = attendance[
                ~(
                    (attendance["Student ID"].astype(str) == selected_id) &
                    (attendance["Date"].astype(str) == str(selected_date))
                )
            ]

            new_record = pd.DataFrame([{
                "Student ID": selected_id,
                "Name": student["Name"],
                "Date": str(selected_date),
                "Status": status
            }])

            attendance = pd.concat(
                [attendance, new_record],
                ignore_index=True
            )

            save_data(attendance, ATTENDANCE_FILE)

            st.success(
                "Attendance saved successfully!"
            )

            st.rerun()


# Attendance Records
elif page == "Attendance Records":

    st.header("📋 Attendance Records")

    if attendance.empty:

        st.info(
            "No attendance records available yet."
        )

    else:

        st.subheader("All Attendance Records")

        st.dataframe(
            attendance,
            use_container_width=True
        )

        st.download_button(
            label="Download Attendance Records",
            data=attendance.to_csv(index=False).encode("utf-8"),
            file_name="attendance_records.csv",
            mime="text/csv"
        )


# Reports
elif page == "Reports":

    st.header("📈 Attendance Reports")

    if attendance.empty:

        st.info("No attendance data available.")

    else:

        # Calculate Attendance Report
        report = attendance.groupby(
            ["Student ID", "Name", "Status"]
        ).size().unstack(fill_value=0)

        if "Present" not in report.columns:
            report["Present"] = 0

        if "Absent" not in report.columns:
            report["Absent"] = 0

        report["Total Classes"] = (
            report["Present"] + report["Absent"]
        )

        report["Attendance Percentage"] = (
            report["Present"]
            .div(
                report["Total Classes"].where(
                    report["Total Classes"] != 0
                )
            )
            .fillna(0) * 100
        ).round(2)

        # Student Attendance Summary
        st.subheader("Student Attendance Summary")

        st.dataframe(
            report,
            use_container_width=True
        )

        # Horizontal Attendance Chart
        st.subheader("Attendance Percentage")

        chart_data = report.reset_index()

        chart_data["Student"] = (
            chart_data["Student ID"].astype(str)
            + " - "
            + chart_data["Name"].astype(str)
        )

        chart_data = chart_data[
            ["Student", "Attendance Percentage"]
        ].set_index("Student")

        st.bar_chart(
            chart_data,
            horizontal=True,
            height=max(300, len(chart_data) * 65)
        )

        # Download Attendance Report
        st.download_button(
            label="Download Attendance Report",
            data=report.to_csv().encode("utf-8"),
            file_name="attendance_report.csv",
            mime="text/csv"
        )
