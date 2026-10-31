
def validate_profile(profile):
    """
    Validate student profile information.
    Returns (is_valid, error_message).
    """

    if not profile["name"].strip():
        return False, "Student name cannot be empty."

    if not profile["roll_number"].strip():
        return False, "Roll number cannot be empty."

    if not profile["branch"].strip():
        return False, "Branch cannot be empty."

    if not 1 <= profile["semester"] <= 8:
        return False, "Semester must be between 1 and 8."

    if not 0.5 <= profile["available_hours"] <= 16:
        return False, "Study hours must be between 0.5 and 16."

    if not 0 <= profile["target_percentage"] <= 100:
        return False, "Target percentage must be between 0 and 100."

    if not 0 <= profile["current_percentage"] <= 100:
        return False, "Current percentage must be between 0 and 100."

    if not 0 <= profile["attendance"] <= 100:
        return False, "Attendance must be between 0 and 100."

    if profile["preferred_time"] not in [
        "Morning", "Afternoon", "Evening", "Night"
    ]:
        return False, "Select a valid preferred study time."

    return True, "Profile information is valid."

def validate_subject(subject):
    """Validate subject information before saving."""

    if not subject["subject_name"].strip():
        return False, "Subject name cannot be empty."

    if subject["maximum_marks"] <= 0:
        return False, "Maximum marks must be greater than zero."

    if subject["obtained_marks"] < 0:
        return False, "Obtained marks cannot be negative."

    if subject["obtained_marks"] > subject["maximum_marks"]:
        return False, "Obtained marks cannot exceed maximum marks."

    if not 0 <= subject["attendance"] <= 100:
        return False, "Attendance must be between 0 and 100."

    if subject["difficulty"] not in ["Easy", "Medium", "Hard"]:
        return False, "Select a valid difficulty level."

    if subject["total_units"] < 1:
        return False, "Total units must be at least 1."

    if not 0 <= subject["completed_units"] <= subject["total_units"]:
        return False, "Completed units cannot exceed total units."

    if subject["pending_assignments"] < 0:
        return False, "Pending assignments cannot be negative."

    if subject["preparation_hours"] < 0:
        return False, "Preparation hours cannot be negative."

    if not 1 <= subject["confidence"] <= 10:
        return False, "Confidence must be between 1 and 10."

    return True, "Subject information is valid."

def validate_subject(subject):
    """Validate subject information before saving."""

    if not subject["subject_name"].strip():
        return False, "Subject name cannot be empty."

    if subject["maximum_marks"] <= 0:
        return False, "Maximum marks must be greater than zero."

    if subject["obtained_marks"] < 0:
        return False, "Obtained marks cannot be negative."

    if subject["obtained_marks"] > subject["maximum_marks"]:
        return False, "Obtained marks cannot exceed maximum marks."

    if not 0 <= subject["attendance"] <= 100:
        return False, "Attendance must be between 0 and 100."

    if subject["difficulty"] not in ["Easy", "Medium", "Hard"]:
        return False, "Select a valid difficulty level."

    if subject["total_units"] < 1:
        return False, "Total units must be at least 1."

    if not 0 <= subject["completed_units"] <= subject["total_units"]:
        return False, "Completed units cannot exceed total units."

    if subject["pending_assignments"] < 0:
        return False, "Pending assignments cannot be negative."

    if subject["preparation_hours"] < 0:
        return False, "Preparation hours cannot be negative."

    if not 1 <= subject["confidence"] <= 10:
        return False, "Confidence must be between 1 and 10."

    return True, "Subject information is valid."
