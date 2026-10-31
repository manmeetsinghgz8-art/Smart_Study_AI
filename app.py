
import streamlit as st
from modules.database import (
    initialize_database,
    get_profile,
    save_profile,
    get_database_info,
    get_subjects,
    add_subject,
    update_subject,
    delete_subject,
    save_study_task,
    get_study_tasks,
    update_study_task_status
)

from modules.planner import generate_study_plan

from modules.ml_model import (
    predict_performance,
    get_feature_importance,
    get_model_metrics
)

from modules.utils import (
    validate_profile,
    validate_subject
)
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, datetime, timedelta

# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SmartStudy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "assets" / "style.css"


# --------------------------------------------------
# 2. LOAD CUSTOM CSS
# --------------------------------------------------

def load_css():
    if CSS_FILE.exists():
        with open(CSS_FILE, "r", encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()
# Initialize the database automatically
try:
    initialize_database()
except Exception as error:
    st.error(f"Database initialization failed: {error}")
    st.stop()


# --------------------------------------------------
# 3. SAMPLE DASHBOARD DATA
# Temporary data for the first development stage.
# It will later come from SQLite.
# --------------------------------------------------

subjects = pd.DataFrame({
    "Subject": [
        "Data Structures",
        "Mathematics",
        "Artificial Intelligence",
        "Operating Systems",
        "Python Programming"
    ],
    "Marks": [62, 74, 81, 69, 86],
    "Attendance": [78, 85, 91, 76, 94],
    "Completion": [55, 70, 65, 48, 85],
    "Priority": [92, 65, 58, 88, 35]
})

weekly_data = pd.DataFrame({
    "Day": ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"],
    "Planned": [3, 3, 4, 3, 4, 3, 2],
    "Completed": [2, 3, 3, 2, 3, 2, 1]
})


# --------------------------------------------------
# 4. SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown("# 🎓 SmartStudy AI")
    st.caption("Your intelligent study companion")

    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Student Profile",
            "Subjects",
            "AI Performance Prediction",
            "Smart Study Planner",
            "Progress Tracking",
            "Recommendations",
            "Analytics",
            "Settings/About"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("### 👨‍🎓 Student")
    st.write("Manmeet Singh")
    st.caption("B.Tech CSE | Semester 3")

    st.divider()

    st.caption("SmartStudy AI v1.0")
    st.caption("Academic Project")


# --------------------------------------------------
# 5. COMMON PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">SmartStudy AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Smart Study Planner & Student '
    'Performance Prediction System'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 6. DASHBOARD PAGE - LIVE DATABASE DATA
# --------------------------------------------------

if page == "Dashboard":

    st.subheader("👋 Welcome to SmartStudy AI")

    # Load the student's saved profile
    try:
        profile = get_profile()
    except Exception as error:
        st.error(f"Unable to load student profile: {error}")
        profile = None

    if not profile:
        st.info(
            "👨‍🎓 Welcome! Please open Student Profile "
            "and save your profile first."
        )

    else:
        student_id = profile["id"]

        st.write(
            f"Here is your academic overview, "
            f"**{profile['name']}**."
        )

        # Load actual subjects from SQLite
        try:
            subject_list = get_subjects(student_id)
        except Exception as error:
            st.error(f"Unable to load subjects: {error}")
            subject_list = []

        if not subject_list:

            st.info(
                "📚 No subjects found. Open Subjects and "
                "add your academic subjects to see your dashboard."
            )

        else:

            # Calculate actual academic metrics
            total_subjects = len(subject_list)

            total_maximum = sum(
                float(s["maximum_marks"])
                for s in subject_list
            )

            total_obtained = sum(
                float(s["obtained_marks"])
                for s in subject_list
            )

            overall_marks = (
                total_obtained / total_maximum * 100
                if total_maximum > 0 else 0
            )

            average_attendance = sum(
                float(s["attendance"])
                for s in subject_list
            ) / total_subjects

            total_units = sum(
                int(s["total_units"])
                for s in subject_list
            )

            completed_units = sum(
                int(s["completed_units"])
                for s in subject_list
            )

            study_progress = (
                completed_units / total_units * 100
                if total_units > 0 else 0
            )

            today = date.today()

            upcoming_exams = []

            for subject in subject_list:
                try:
                    exam_day = date.fromisoformat(
                        subject["exam_date"]
                    )

                    days_left = (exam_day - today).days

                    if days_left >= 0:
                        upcoming_exams.append(
                            (days_left, subject["subject_name"])
                        )

                except (ValueError, TypeError):
                    continue

            upcoming_exams.sort(key=lambda item: item[0])

            # Dashboard metric cards
            st.markdown(
                '<div class="section-title">'
                '📊 Academic Overview</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Overall Marks",
                f"{overall_marks:.1f}%"
            )

            col2.metric(
                "Syllabus Completed",
                f"{study_progress:.1f}%"
            )

            col3.metric(
                "Average Attendance",
                f"{average_attendance:.1f}%"
            )

            col4.metric(
                "Total Subjects",
                total_subjects
            )

            # Upcoming exam
            st.markdown("### 🗓️ Upcoming Examination")

            if upcoming_exams:
                days_left, exam_subject = upcoming_exams[0]

                if days_left == 0:
                    exam_message = "Exam is today!"
                elif days_left == 1:
                    exam_message = "1 day remaining"
                else:
                    exam_message = f"{days_left} days remaining"

                st.info(
                    f"**{exam_subject}** — {exam_message}"
                )

            else:
                st.info(
                    "No upcoming examination dates are available."
                )

            # Prepare actual subject data for charts
            chart_data = []

            for subject in subject_list:

                maximum = float(subject["maximum_marks"])
                obtained = float(subject["obtained_marks"])

                marks_percentage = (
                    obtained / maximum * 100
                    if maximum > 0 else 0
                )

                total = int(subject["total_units"])
                completed = int(subject["completed_units"])

                completion = (
                    completed / total * 100
                    if total > 0 else 0
                )

                chart_data.append({
                    "Subject": subject["subject_name"],
                    "Marks": round(marks_percentage, 2),
                    "Attendance": float(subject["attendance"]),
                    "Completion": round(completion, 2),
                    "Priority": max(
                        1,
                        100 - float(subject["confidence"]) * 10
                    )
                })

            chart_df = pd.DataFrame(chart_data)

            # Subject-wise marks and attendance
            left, right = st.columns(2)

            with left:

                st.markdown("### 📚 Subject-wise Marks")

                fig = px.bar(
                    chart_df,
                    x="Subject",
                    y="Marks",
                    color="Marks",
                    color_continuous_scale="Blues",
                    range_y=[0, 100]
                )

                fig.update_layout(
                    showlegend=False,
                    yaxis_title="Marks (%)",
                    xaxis_title="Subject",
                    plot_bgcolor="white",
                    paper_bgcolor="white"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with right:

                st.markdown("### 📈 Subject-wise Attendance")

                fig = px.bar(
                    chart_df,
                    x="Subject",
                    y="Attendance",
                    color="Attendance",
                    color_continuous_scale="Teal",
                    range_y=[0, 100]
                )

                fig.update_layout(
                    showlegend=False,
                    yaxis_title="Attendance (%)",
                    xaxis_title="Subject",
                    plot_bgcolor="white",
                    paper_bgcolor="white"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # Actual syllabus completion
            st.markdown("### 🎯 Syllabus Progress")

            for _, subject in chart_df.iterrows():

                st.write(
                    f"**{subject['Subject']}** — "
                    f"{subject['Completion']:.1f}%"
                )

                st.progress(
                    int(subject["Completion"])
                )

            # Actual subject table
            st.markdown("### 📋 Academic Summary")

            st.dataframe(
                chart_df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Dashboard values are calculated from the "
                "subjects currently saved in your SQLite database."
            )

# --------------------------------------------------
# 7. STUDENT PROFILE PAGE
# --------------------------------------------------


elif page == "Student Profile":

    st.subheader("👨‍🎓 Student Profile")

    st.write(
        "Manage your academic information. "
        "Your details are saved permanently in SQLite."
    )

    # Retrieve saved profile
    try:
        profile = get_profile()
    except Exception as error:
        st.error(f"Unable to retrieve profile: {error}")
        profile = None

    # Default values for a new student
    defaults = {
        "name": "Manmeet Singh",
        "roll_number": "2025A1R018",
        "semester": 2,
        "branch": "B.Tech CSE",
        "available_hours": 3.0,
        "preferred_time": "Evening",
        "target_percentage": 85.0,
        "current_percentage": 72.0,
        "attendance": 82.0
    }

    # Load saved data when available
    if profile:
        defaults.update(profile)

    st.markdown("### Personal Information")

    with st.form("profile_form", clear_on_submit=False):

        name = st.text_input(
            "Student Name",
            value=defaults["name"]
        )

        roll = st.text_input(
            "Roll Number",
            value=defaults["roll_number"]
        )

        col1, col2 = st.columns(2)

        with col1:
            semester = st.number_input(
                "Semester",
                min_value=1,
                max_value=8,
                value=int(defaults["semester"])
            )

            branch = st.text_input(
                "Branch",
                value=defaults["branch"]
            )

            study_hours = st.number_input(
                "Available Study Hours Per Day",
                min_value=0.5,
                max_value=16.0,
                value=float(defaults["available_hours"]),
                step=0.5
            )

        with col2:
            target = st.number_input(
                "Target Percentage",
                min_value=0.0,
                max_value=100.0,
                value=float(defaults["target_percentage"])
            )

            current = st.number_input(
                "Current Percentage",
                min_value=0.0,
                max_value=100.0,
                value=float(defaults["current_percentage"])
            )

            attendance = st.number_input(
                "Average Attendance",
                min_value=0.0,
                max_value=100.0,
                value=float(defaults["attendance"])
            )

        time_options = [
            "Morning", "Afternoon", "Evening", "Night"
        ]

        preferred_time = st.selectbox(
            "Preferred Study Time",
            options=time_options,
            index=time_options.index(
                defaults["preferred_time"]
            )
        )

        submitted = st.form_submit_button(
            "💾 Save Profile",
            type="primary",
            use_container_width=True
        )

        if submitted:

            new_profile = {
                "name": name.strip(),
                "roll_number": roll.strip(),
                "semester": int(semester),
                "branch": branch.strip(),
                "available_hours": float(study_hours),
                "preferred_time": preferred_time,
                "target_percentage": float(target),
                "current_percentage": float(current),
                "attendance": float(attendance)
            }

            valid, message = validate_profile(new_profile)

            if not valid:
                st.error(message)

            else:
                try:
                    save_profile(new_profile)

                    st.success(
                        "Student profile saved successfully!"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        f"Unable to save profile: {error}"
                    )

    # Display saved profile information
    st.divider()

    st.markdown("### 📋 Saved Profile Information")

    if profile:

        st.success("A student profile is saved in SQLite.")

        col1, col2, col3 = st.columns(3)

        col1.metric("Semester", profile["semester"])
        col2.metric(
            "Study Hours",
            f"{profile['available_hours']} hrs/day"
        )
        col3.metric(
            "Attendance",
            f"{profile['attendance']}%"
        )

        st.write("**Student:**", profile["name"])
        st.write("**Roll Number:**", profile["roll_number"])
        st.write("**Branch:**", profile["branch"])
        st.write("**Preferred Time:**", profile["preferred_time"])

    else:
        st.info(
            "No saved profile yet. "
            "Complete the form and click Save Profile."
        )


# --------------------------------------------------
# 8. SUBJECT MANAGEMENT PAGE
# --------------------------------------------------


elif page == "Subjects":

    st.subheader("📚 Subject Management")

    st.write(
        "Add, edit and manage your academic subjects. "
        "All information is stored in SQLite."
    )

    # Get the saved student profile
    profile = get_profile()

    if not profile:
        st.warning(
            "Please save your Student Profile before "
            "adding subjects."
        )
        st.stop()

    student_id = profile["id"]

    # Retrieve subjects
    try:
        subject_list = get_subjects(student_id)
    except Exception as error:
        st.error(f"Unable to load subjects: {error}")
        subject_list = []

    # ----------------------------------------------
    # SUBJECT OVERVIEW
    # ----------------------------------------------

    st.markdown("### 📊 Subject Overview")

    total_subjects = len(subject_list)

    if total_subjects > 0:

        average_marks = sum(
            (s["obtained_marks"] / s["maximum_marks"]) * 100
            for s in subject_list
        ) / total_subjects

        average_attendance = sum(
            s["attendance"] for s in subject_list
        ) / total_subjects

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Subjects", total_subjects)
        col2.metric("Average Marks", f"{average_marks:.1f}%")
        col3.metric("Average Attendance", f"{average_attendance:.1f}%")

    else:
        st.info("No subjects added yet. Add your first subject below.")

    st.divider()

    # ----------------------------------------------
    # DISPLAY SUBJECT TABLE
    # ----------------------------------------------

    st.markdown("### 📋 Your Subjects")

    if subject_list:

        display_data = []

        for subject in subject_list:

            percentage = (
                subject["obtained_marks"]
                / subject["maximum_marks"]
            ) * 100

            completion = (
                subject["completed_units"]
                / subject["total_units"]
            ) * 100

            display_data.append({
                "Subject": subject["subject_name"],
                "Code": subject["subject_code"],
                "Marks (%)": round(percentage, 2),
                "Attendance (%)": subject["attendance"],
                "Difficulty": subject["difficulty"],
                "Exam Date": subject["exam_date"],
                "Syllabus (%)": round(completion, 2),
                "Pending Assignments": subject["pending_assignments"],
                "Confidence": subject["confidence"]
            })

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### 📖 Syllabus Progress")

        for subject in subject_list:

            percentage = (
                subject["completed_units"]
                / subject["total_units"]
            )

            st.write(
                f"**{subject['subject_name']}** "
                f"({percentage * 100:.1f}%)"
            )

            st.progress(percentage)

    # ----------------------------------------------
    # ADD SUBJECT
    # ----------------------------------------------

    st.divider()
    st.markdown("### ➕ Add New Subject")

    with st.form("add_subject_form"):

        subject_name = st.text_input(
            "Subject Name",
            placeholder="Example: Data Structures"
        )

        subject_code = st.text_input(
            "Subject Code",
            placeholder="Example: CSE201"
        )

        col1, col2 = st.columns(2)

        with col1:

            obtained_marks = st.number_input(
                "Obtained Marks",
                min_value=0.0,
                value=60.0,
                step=1.0
            )

            maximum_marks = st.number_input(
                "Maximum Marks",
                min_value=1.0,
                value=100.0,
                step=1.0
            )

            attendance = st.number_input(
                "Attendance (%)",
                min_value=0.0,
                max_value=100.0,
                value=80.0
            )

            difficulty = st.selectbox(
                "Difficulty Level",
                ["Easy", "Medium", "Hard"]
            )

        with col2:

            exam_date = st.date_input(
                "Examination Date",
                value=date.today() + timedelta(days=20),
                min_value=date.today()
            )

            total_units = st.number_input(
                "Total Syllabus Units",
                min_value=1,
                max_value=100,
                value=10
            )

            completed_units = st.number_input(
                "Completed Units",
                min_value=0,
                max_value=100,
                value=5
            )

            pending_assignments = st.number_input(
                "Pending Assignments",
                min_value=0,
                max_value=100,
                value=0
            )

        preparation_hours = st.number_input(
            "Estimated Preparation Hours",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            step=1.0
        )

        confidence = st.slider(
            "Current Confidence Level",
            min_value=1,
            max_value=10,
            value=5
        )

        add_button = st.form_submit_button(
            "➕ Add Subject",
            type="primary",
            use_container_width=True
        )

        if add_button:

            new_subject = {
                "subject_name": subject_name.strip(),
                "subject_code": subject_code.strip(),
                "obtained_marks": float(obtained_marks),
                "maximum_marks": float(maximum_marks),
                "attendance": float(attendance),
                "difficulty": difficulty,
                "exam_date": exam_date.isoformat(),
                "total_units": int(total_units),
                "completed_units": int(completed_units),
                "pending_assignments": int(pending_assignments),
                "preparation_hours": float(preparation_hours),
                "confidence": int(confidence)
            }

            valid, message = validate_subject(new_subject)

            if not valid:
                st.error(message)

            elif exam_date < date.today():
                st.error("Examination date cannot be in the past.")

            else:

                try:
                    add_subject(student_id, new_subject)

                    st.success(
                        f"{subject_name} added successfully!"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(f"Unable to add subject: {error}")

    # ----------------------------------------------
    # EDIT SUBJECT
    # ----------------------------------------------

    st.divider()
    st.markdown("### ✏️ Edit Existing Subject")

    if subject_list:

        subject_options = {
            f"{s['subject_name']} ({s['subject_code'] or 'No code'}) - ID {s['id']}": s
            for s in subject_list
        }

        selected_label = st.selectbox(
            "Select Subject to Edit",
            list(subject_options.keys())
        )

        selected_subject = subject_options[selected_label]

        with st.form("edit_subject_form"):

            edit_name = st.text_input(
                "Subject Name",
                value=selected_subject["subject_name"]
            )

            edit_code = st.text_input(
                "Subject Code",
                value=selected_subject["subject_code"] or ""
            )

            col1, col2 = st.columns(2)

            with col1:

                edit_marks = st.number_input(
                    "Obtained Marks",
                    min_value=0.0,
                    value=float(selected_subject["obtained_marks"])
                )

                edit_maximum = st.number_input(
                    "Maximum Marks",
                    min_value=1.0,
                    value=float(selected_subject["maximum_marks"])
                )

                edit_attendance = st.number_input(
                    "Attendance (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(selected_subject["attendance"])
                )

                edit_difficulty = st.selectbox(
                    "Difficulty",
                    ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(
                        selected_subject["difficulty"]
                    )
                )

            with col2:

                saved_exam_date = date.fromisoformat(
                    selected_subject["exam_date"]
                )

                edit_exam_date = st.date_input(
                    "Examination Date",
                    value=saved_exam_date,
                    min_value=date.today()
                )

                edit_total = st.number_input(
                    "Total Units",
                    min_value=1,
                    max_value=100,
                    value=int(selected_subject["total_units"])
                )

                edit_completed = st.number_input(
                    "Completed Units",
                    min_value=0,
                    max_value=100,
                    value=int(selected_subject["completed_units"])
                )

                edit_pending = st.number_input(
                    "Pending Assignments",
                    min_value=0,
                    max_value=100,
                    value=int(selected_subject["pending_assignments"])
                )

            edit_hours = st.number_input(
                "Preparation Hours",
                min_value=0.0,
                max_value=500.0,
                value=float(selected_subject["preparation_hours"])
            )

            edit_confidence = st.slider(
                "Confidence Level",
                1,
                10,
                int(selected_subject["confidence"])
            )

            update_button = st.form_submit_button(
                "💾 Update Subject",
                type="primary",
                use_container_width=True
            )

            if update_button:

                updated_subject = {
                    "subject_name": edit_name.strip(),
                    "subject_code": edit_code.strip(),
                    "obtained_marks": float(edit_marks),
                    "maximum_marks": float(edit_maximum),
                    "attendance": float(edit_attendance),
                    "difficulty": edit_difficulty,
                    "exam_date": edit_exam_date.isoformat(),
                    "total_units": int(edit_total),
                    "completed_units": int(edit_completed),
                    "pending_assignments": int(edit_pending),
                    "preparation_hours": float(edit_hours),
                    "confidence": int(edit_confidence)
                }

                valid, message = validate_subject(updated_subject)

                if not valid:
                    st.error(message)

                elif edit_exam_date < date.today():
                    st.error("Examination date cannot be in the past.")

                else:

                    try:
                        updated = update_subject(
                            selected_subject["id"],
                            student_id,
                            updated_subject
                        )

                        if updated:
                            st.success("Subject updated successfully!")
                            st.rerun()
                        else:
                            st.error("Subject could not be found.")

                    except Exception as error:
                        st.error(f"Update failed: {error}")

    # ----------------------------------------------
    # DELETE SUBJECT
    # ----------------------------------------------

    st.divider()
    st.markdown("### 🗑️ Delete Subject")

    if subject_list:

        delete_options = {
            f"{s['subject_name']} - ID {s['id']}": s["id"]
            for s in subject_list
        }

        selected_delete = st.selectbox(
            "Select Subject to Delete",
            list(delete_options.keys()),
            key="delete_subject_selection"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to permanently delete this subject."
        )

        if st.button("🗑️ Delete Selected Subject", type="secondary"):

            if not confirm_delete:
                st.warning("Please confirm before deleting.")

            else:

                try:
                    deleted = delete_subject(
                        delete_options[selected_delete],
                        student_id
                    )

                    if deleted:
                        st.success("Subject deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Subject could not be found.")

                except Exception as error:
                    st.error(f"Delete failed: {error}")

    else:
        st.info("Add a subject to enable editing and deletion.")


# --------------------------------------------------
# 9. PERFORMANCE PREDICTION PAGE
# --------------------------------------------------

elif page == "AI Performance Prediction":

    st.subheader("🤖 AI Performance Prediction")

    st.write(
        "Enter your academic details to estimate your "
        "performance using the trained Machine Learning model."
    )

    st.info(
        "The current model uses study hours and previous marks "
        "to estimate your score. Attendance, difficulty, "
        "pending assignments and confidence are collected "
        "but are not yet used by this prediction model."
    )

    with st.form("prediction_form"):

        study = st.number_input(
            "Study Hours Per Day",
            min_value=0.5,
            max_value=16.0,
            value=3.0,
            step=0.5
        )

        attendance = st.number_input(
            "Attendance (%)",
            min_value=0.0,
            max_value=100.0,
            value=82.0,
            step=1.0
        )

        marks = st.number_input(
            "Previous Marks (%)",
            min_value=0.0,
            max_value=100.0,
            value=68.0,
            step=1.0
        )

        difficulty = st.selectbox(
            "Subject Difficulty",
            ["Easy", "Medium", "Hard"]
        )

        pending = st.number_input(
            "Pending Assignments",
            min_value=0,
            max_value=100,
            value=4
        )

        confidence = st.slider(
            "Confidence Level",
            min_value=1,
            max_value=10,
            value=6
        )

        predict = st.form_submit_button(
            "🤖 Predict Performance",
            type="primary",
            use_container_width=True
        )

    if predict:

        try:
            with st.spinner("Analyzing your academic information..."):

                predicted_score = predict_performance(
                    study_hours_per_day=float(study),
                    previous_marks=float(marks),
                    previous_failures=0
                )

            st.divider()

            st.subheader("📊 Prediction Results")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Estimated Academic Score",
                    f"{predicted_score:.2f}%"
                )

            with col2:
                st.metric(
                    "Target Score",
                    "85.00%"
                )

            if predicted_score < 50:

                st.error(
                    "Performance Category: Needs Improvement"
                )

                st.write(
                    "Suggested action: Study consistently, "
                    "revise fundamentals and practice questions daily."
                )

            elif predicted_score < 75:

                st.warning(
                    "Performance Category: Moderate"
                )

                st.write(
                    "Suggested action: Focus on weaker topics, "
                    "revise regularly and solve practice questions."
                )

            else:

                st.success(
                    "Performance Category: Good"
                )

                st.write(
                    "Suggested action: Maintain your study routine "
                    "and practice mock tests."
                )

            st.caption(
                "This is a model-based estimate, not a guaranteed "
                "exam result. Actual performance may differ."
            )

            with st.expander("View the inputs you entered"):

                st.write(f"Study hours per day: {study}")
                st.write(f"Attendance: {attendance}%")
                st.write(f"Previous marks: {marks}%")
                st.write(f"Subject difficulty: {difficulty}")
                st.write(f"Pending assignments: {pending}")
                st.write(f"Confidence level: {confidence}/10")

        except Exception as error:

            st.error(
                f"Prediction failed: {error}"
            )

            st.info(
                "Check that the trained model exists and that "
                "the required Python packages are installed."
            )



# --------------------------------------------------
# 10. STUDY PLANNER PAGE
# --------------------------------------------------

elif page == "Smart Study Planner":

    st.subheader("📅 Smart Study Planner")

    st.write(
        "Generate a personalized timetable using "
        "your saved subjects and exam information."
    )

    profile = get_profile()

    if not profile:
        st.warning(
            "Please open Student Profile and save your profile first."
        )
        st.stop()

    student_id = profile["id"]

    try:
        subject_list = get_subjects(student_id)
    except Exception as error:
        st.error(f"Unable to load subjects: {error}")
        st.stop()

    if not subject_list:
        st.warning(
            "No subjects found. Open Subjects and add at least one subject."
        )
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        hours = st.number_input(
            "Daily Study Hours",
            min_value=0.5,
            max_value=16.0,
            value=float(profile.get("available_hours", 3.0)),
            step=0.5
        )

    with col2:
        start_time = st.time_input(
            "Study Start Time",
            value=datetime.strptime("18:00", "%H:%M").time()
        )

    with col3:
        break_minutes = st.number_input(
            "Break Between Sessions (minutes)",
            min_value=0,
            max_value=30,
            value=10,
            step=5
        )

    st.markdown("### 📚 Subjects for Your Timetable")

    selected_subject_names = st.multiselect(
        "Choose subjects",
        options=[s["subject_name"] for s in subject_list],
        default=[s["subject_name"] for s in subject_list]
    )

    selected_subjects = [
        s for s in subject_list
        if s["subject_name"] in selected_subject_names
    ]

    if st.button("🚀 Generate Study Timetable", type="primary"):

        if not selected_subjects:
            st.warning("Please select at least one subject.")

        else:
            try:
                timetable = generate_study_plan(
                    subjects=selected_subjects,
                    daily_hours=float(hours),
                    start_time=start_time.strftime("%H:%M"),
                    break_minutes=int(break_minutes)
                )

                st.session_state["generated_study_plan"] = timetable

                # Save timetable to SQLite
                today = date.today().isoformat()

                existing_tasks = get_study_tasks(student_id, today)

                if existing_tasks:
                    st.warning(
                        "Today's timetable is already saved. "
                        "Duplicate timetable was not created."
                    )

                else:
                    subject_lookup = {
                        subject["subject_name"]: subject
                        for subject in selected_subjects
                    }

                    for session in timetable:
                        subject = subject_lookup.get(session["subject"])

                        if subject is None:
                            continue

                        duration_hours = (
                            float(session["duration_minutes"]) / 60
                        )

                        save_study_task(
                            student_id=student_id,
                            subject_id=subject["id"],
                            task_title=session["task"],
                            task_date=today,
                            start_time=session["start"],
                            end_time=session["end"],
                            planned_hours=duration_hours
                        )

                    st.success("Today's timetable saved successfully!")

            except Exception as error:
                st.error(
                    f"Unable to generate or save timetable: {error}"
                )

    timetable = st.session_state.get("generated_study_plan", [])

    if timetable:
        st.markdown("### 🗓️ Your Personalized Timetable")

        st.success(
            f"Timetable generated with {len(timetable)} study sessions."
        )

        timetable_df = pd.DataFrame(timetable)

        timetable_df = timetable_df.rename(columns={
            "subject": "Subject",
            "start": "Start Time",
            "end": "End Time",
            "duration_minutes": "Study Duration (minutes)",
            "priority_score": "Priority Score",
            "task": "Suggested Task"
        })

        st.dataframe(
            timetable_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### ⏱️ Session Details")

        for session in timetable:
            with st.container(border=True):
                st.markdown(
                    f"**📘 {session['subject']}**  \n"
                    f"🕒 {session['start']} – {session['end']}  \n"
                    f"⏳ {session['duration_minutes']} minutes  \n"
                    f"🎯 {session['task']}"
                )

        st.info(
            "The timetable uses your saved subject details to prioritize "
            "study sessions. Treat the priority score as a planning "
            "heuristic, not a scientifically validated prediction."
        )


# --------------------------------------------------
# 11. PROGRESS TRACKING PAGE
# --------------------------------------------------

elif page == "Progress Tracking":

    st.subheader("📈 Progress Tracking")

    # Get actual student ID from saved profile
    profile = get_profile()

    if not profile:
        st.warning("Please save your Student Profile first.")

    else:
        student_id = profile["id"]

        # Get study tasks
        tasks = get_study_tasks(student_id)

        # Remove duplicate tasks while preserving Completed status
        unique_tasks = {}

        for task in tasks:
            key = (
                task["task_date"],
                task["start_time"],
                task["end_time"],
                task["subject_name"],
                task["task_title"]
            )

            if key not in unique_tasks:
                unique_tasks[key] = task

            elif task["status"] == "Completed":
                unique_tasks[key] = task

        tasks = list(unique_tasks.values())

        # Calculate progress
        total_planned = sum(
            float(t["planned_hours"] or 0) for t in tasks
        )

        total_completed = sum(
            float(t["completed_hours"] or 0) for t in tasks
        )

        pending = max(total_planned - total_completed, 0)

        progress = (
            total_completed / total_planned
            if total_planned > 0 else 0
        )

        # Display metrics
        st.metric(
            "Overall Study Progress",
            f"{progress * 100:.1f}%"
        )

        st.progress(progress)

        c1, c2, c3 = st.columns(3)

        c1.metric("Planned Hours", f"{total_planned:.1f}")
        c2.metric("Completed Hours", f"{total_completed:.1f}")
        c3.metric("Pending Hours", f"{pending:.1f}")

        st.divider()
        st.subheader("📚 Study Task History")

        if not tasks:
            st.info("No tasks found. Generate a timetable first.")

        for task in tasks:

            with st.container(border=True):

                st.write(f"**{task['task_title']}**")
                st.write(
                    f"Subject: {task.get('subject_name') or 'General'}"
                )
                st.write(f"Date: {task['task_date']}")
                st.write(
                    f"Time: {task['start_time']} - {task['end_time']}"
                )
                st.write(f"Status: {task['status']}")

                if task["status"] == "Pending":

                    if st.button(
                        "✅ Complete",
                        key=f"complete_{task['id']}"
                    ):
                        update_study_task_status(
                            task["id"], student_id, True
                        )
                        st.rerun()

                else:

                    st.success("Completed")

                    if st.button(
                        "↩ Mark Pending",
                        key=f"pending_{task['id']}"
                    ):
                        update_study_task_status(
                            task["id"], student_id, False
                        )
                        st.rerun()

# --------------------------------------------------
# 12. RECOMMENDATIONS PAGE
# --------------------------------------------------

elif page == "Recommendations":

    st.subheader("💡 Personalized Recommendations")

    profile = get_profile()

    if not profile:
        st.warning("Please save your Student Profile first.")

    else:
        student_id = profile["id"]

        subject_list = get_subjects(student_id)

        if not subject_list:
            st.info("Please add subjects to generate recommendations.")

        else:
            st.write(
                "Recommendations generated using your saved academic data."
            )

            for subject in subject_list:

                name = subject["subject_name"]

                maximum = float(subject["maximum_marks"] or 0)
                obtained = float(subject["obtained_marks"] or 0)

                marks = (
                    obtained / maximum * 100
                    if maximum > 0 else 0
                )

                total = int(subject["total_units"] or 0)
                completed = int(subject["completed_units"] or 0)

                completion = (
                    completed / total * 100
                    if total > 0 else 0
                )

                attendance = float(subject["attendance"] or 0)
                pending = int(subject["pending_assignments"] or 0)
                confidence = int(subject["confidence"] or 0)

                if marks < 50 or completion < 40:
                    color = "🔴"
                    title = "Needs Immediate Attention"
                    message = (
                        f"Your marks are {marks:.1f}% and syllabus "
                        f"completion is {completion:.1f}%. "
                        "Give this subject extra revision time."
                    )

                elif attendance < 75 or pending > 3 or confidence <= 4:
                    color = "🟡"
                    title = "Needs Improvement"
                    message = (
                        f"Attendance: {attendance:.1f}%, "
                        f"Pending assignments: {pending}, "
                        f"Confidence: {confidence}/10. "
                        "Attend classes regularly and complete pending work."
                    )

                else:
                    color = "🟢"
                    title = "Good Performance"
                    message = (
                        f"Your marks are {marks:.1f}% and syllabus "
                        f"completion is {completion:.1f}%. "
                        "Maintain your consistency and practice regularly."
                    )

                with st.container(border=True):

                    st.markdown(f"### {color} {name}")

                    st.caption(title)

                    st.write(message)

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Marks", f"{marks:.1f}%")
                    col2.metric("Syllabus", f"{completion:.1f}%")
                    col3.metric("Attendance", f"{attendance:.1f}%")

            st.caption(
                "Recommendations are rule-based suggestions generated "
                "from your saved academic information. They are not "
                "medical or guaranteed academic predictions."
            )

# --------------------------------------------------
# 13. ANALYTICS PAGE
# --------------------------------------------------

elif page == "Analytics":

    st.subheader("📊 Academic Analytics")

    profile = get_profile()

    if not profile:
        st.warning("Please save your Student Profile first.")

    else:
        student_id = profile["id"]

        subject_list = get_subjects(student_id)
        tasks = get_study_tasks(student_id)

        if not subject_list:
            st.info("Please add subjects to view academic analytics.")

        else:

            # Prepare actual subject data
            analytics_data = []

            for subject in subject_list:

                maximum = float(subject["maximum_marks"] or 0)
                obtained = float(subject["obtained_marks"] or 0)

                marks = (
                    obtained / maximum * 100
                    if maximum > 0 else 0
                )

                total = int(subject["total_units"] or 0)
                completed = int(subject["completed_units"] or 0)

                completion = (
                    completed / total * 100
                    if total > 0 else 0
                )

                analytics_data.append({
                    "Subject": subject["subject_name"],
                    "Marks": round(marks, 1),
                    "Attendance": float(subject["attendance"] or 0),
                    "Syllabus Completion": round(completion, 1)
                })

            analytics_df = pd.DataFrame(analytics_data)

            # Academic overview
            average_marks = analytics_df["Marks"].mean()
            average_completion = analytics_df["Syllabus Completion"].mean()
            average_attendance = analytics_df["Attendance"].mean()

            st.markdown("### 📈 Academic Overview")

            c1, c2, c3 = st.columns(3)

            c1.metric("Average Marks", f"{average_marks:.1f}%")
            c2.metric("Syllabus Completion", f"{average_completion:.1f}%")
            c3.metric("Average Attendance", f"{average_attendance:.1f}%")

            st.divider()

            # Subject performance chart
            st.markdown("### 📚 Subject Performance")

            fig = px.bar(
                analytics_df,
                x="Subject",
                y="Marks",
                color="Marks",
                text="Marks",
                range_y=[0, 100],
                color_continuous_scale="Blues",
                title="Subject-wise Academic Performance"
            )

            fig.update_traces(texttemplate="%{text:.1f}%")

            fig.update_layout(
                yaxis_title="Marks (%)",
                xaxis_title="Subject",
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Attendance and syllabus charts
            left, right = st.columns(2)

            with left:

                st.markdown("### 🎯 Syllabus Completion")

                fig = px.bar(
                    analytics_df,
                    x="Subject",
                    y="Syllabus Completion",
                    color="Syllabus Completion",
                    range_y=[0, 100],
                    color_continuous_scale="Greens"
                )

                st.plotly_chart(fig, use_container_width=True)

            with right:

                st.markdown("### 🏫 Attendance Analysis")

                fig = px.bar(
                    analytics_df,
                    x="Subject",
                    y="Attendance",
                    color="Attendance",
                    range_y=[0, 100],
                    color_continuous_scale="Teal"
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # Study task analytics
            st.markdown("### ⏱️ Study Activity Analytics")

            if tasks:

                task_data = []

                for task in tasks:

                    task_data.append({
                        "Date": task["task_date"],
                        "Status": task["status"],
                        "Planned Hours": float(task["planned_hours"] or 0),
                        "Completed Hours": float(task["completed_hours"] or 0)
                    })

                task_df = pd.DataFrame(task_data)

                total_planned = task_df["Planned Hours"].sum()
                total_completed = task_df["Completed Hours"].sum()

                completion_rate = (
                    total_completed / total_planned * 100
                    if total_planned > 0 else 0
                )

                c1, c2, c3 = st.columns(3)

                c1.metric("Planned Study Hours", f"{total_planned:.1f}")
                c2.metric("Completed Study Hours", f"{total_completed:.1f}")
                c3.metric("Study Completion Rate", f"{completion_rate:.1f}%")

                # Completed vs pending
                status_data = task_df.groupby("Status").size().reset_index(name="Tasks")

                fig = px.pie(
                    status_data,
                    names="Status",
                    values="Tasks",
                    hole=0.45,
                    title="Completed vs Pending Tasks"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Daily study hours for last 7 days
                task_df["Date"] = pd.to_datetime(
                    task_df["Date"], errors="coerce"
                )

                last_seven_days = date.today() - timedelta(days=6)

                recent_df = task_df[
                    task_df["Date"].dt.date >= last_seven_days
                ].copy()

                if not recent_df.empty:

                    daily_df = recent_df.groupby("Date", as_index=False)[
                        ["Planned Hours", "Completed Hours"]
                    ].sum()

                    fig = px.line(
                        daily_df,
                        x="Date",
                        y=["Planned Hours", "Completed Hours"],
                        markers=True,
                        title="Daily Study Hours - Last 7 Days"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                else:
                    st.info(
                        "No study activity recorded in the last 7 days."
                    )

            else:
                st.info(
                    "No study tasks found. Generate a timetable "
                    "to view study activity analytics."
                )

            # Subject information
            st.divider()

            st.markdown("### 📋 Subject Information")

            st.dataframe(
                analytics_df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Analytics are calculated using your saved SQLite "
                "subject and study task records."
            )

# --------------------------------------------------
# 14. SETTINGS AND ABOUT PAGE
# --------------------------------------------------

elif page == "Settings/About":

    st.subheader("⚙️ Settings & About Project")

    st.markdown("### Project Information")

    st.write("**Project:** AI-Powered Smart Study Planner and Student Performance Prediction System")
    st.write("**Student:** Manmeet Singh")
    st.write("**Roll Number:** 2025A1R018")
    st.write("**Course:** B.Tech CSE – 2nd Semester, A3")
    st.write("**Subject:** Artificial Intelligence and Machine Learning (MDC - AI - 301)")

    st.divider()

    st.markdown("### Problem Statement")
    st.write(
        "Students often struggle to organize their study time, "
        "identify weak subjects and monitor academic progress."
    )

    st.markdown("### Proposed Solution")
    st.write(
        "SmartStudy AI combines machine learning, subject "
        "priority calculation and personalized timetable "
        "generation to improve study management."
    )

    st.markdown("### Technologies Used")

    st.write(
        "Python, Streamlit, Pandas, NumPy, Scikit-learn, "
        "SQLite, Plotly and Joblib."
    )

    st.markdown("### Future Scope")

    st.write(
        "Adaptive learning, automated reminders, "
        "more advanced prediction models and cloud deployment."
    )

    st.success("Welcome to SmartStudy AI!")
