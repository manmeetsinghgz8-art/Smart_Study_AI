from datetime import datetime, timedelta


def generate_study_plan(
    subjects,
    daily_hours,
    start_time="18:00",
    break_minutes=10
):
    """
    Generate a daily study timetable from subject data.

    Each subject may contain:
    subject_name, difficulty, preparation_hours,
    pending_assignments, exam_date, confidence.
    """

    if daily_hours <= 0:
        raise ValueError("Daily study hours must be greater than zero.")

    if not subjects:
        return []

    start = datetime.strptime(start_time, "%H:%M")
    available_minutes = int(daily_hours * 60)

    # Reserve time for breaks between study sessions.
    session_count = min(len(subjects), max(1, available_minutes // 30))
    total_breaks = max(0, session_count - 1) * break_minutes
    study_minutes = available_minutes - total_breaks

    if study_minutes < session_count:
        raise ValueError("Increase daily study hours or reduce break duration.")

    # Prioritize subjects using difficulty, pending assignments,
    # confidence, preparation needs, and exam dates.
    today = datetime.now().date()

    def priority(subject):
        score = 0

        difficulty = subject.get("difficulty", "Medium")
        score += {"Easy": 1, "Medium": 2, "Hard": 3}.get(
            difficulty, 2
        ) * 2

        score += min(
            int(subject.get("pending_assignments", 0)), 10
        )

        confidence = int(subject.get("confidence", 5))
        score += max(0, 10 - confidence)

        preparation = float(subject.get("preparation_hours", 0))
        score += min(preparation, 20) * 0.2

        exam_date = subject.get("exam_date")

        if exam_date:
            try:
                exam = datetime.strptime(
                    str(exam_date), "%Y-%m-%d"
                ).date()

                days_left = (exam - today).days

                if days_left >= 0:
                    score += max(0, 14 - days_left) * 1.5
            except ValueError:
                pass

        return score

    ordered_subjects = sorted(
        subjects,
        key=priority,
        reverse=True
    )

    # Give every subject an initial study session.
    base_minutes = study_minutes // len(ordered_subjects)
    remainder = study_minutes % len(ordered_subjects)

    plan = []
    current_time = start

    for index, subject in enumerate(ordered_subjects):
        duration = base_minutes + (1 if index < remainder else 0)

        if duration <= 0:
            continue

        session_end = current_time + timedelta(minutes=duration)

        plan.append({
            "subject": subject.get("subject_name", "Subject"),
            "start": current_time.strftime("%I:%M %p"),
            "end": session_end.strftime("%I:%M %p"),
            "duration_minutes": duration,
            "priority_score": round(priority(subject), 2),
            "task": (
                "Complete pending assignments and revise weak topics"
                if int(subject.get("pending_assignments", 0)) > 0
                else "Revise concepts and solve practice questions"
            )
        })

        current_time = session_end

        if index < len(ordered_subjects) - 1:
            current_time += timedelta(minutes=break_minutes)

    return plan