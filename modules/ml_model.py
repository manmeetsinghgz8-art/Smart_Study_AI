
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

DATA_PATH = DATA_DIR / "student_performance.csv"
MODEL_PATH = MODEL_DIR / "performance_model.pkl"

FEATURES = [
    "studytime",
    "failures",
    "G1",
    "G2"
]

TARGET = "G3"


def load_dataset():
    """
    Download the UCI Student Performance dataset
    and save the Mathematics records locally.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from ucimlrepo import fetch_ucirepo

        dataset = fetch_ucirepo(id=320)

        features = dataset.data.features
        targets = dataset.data.targets

        # The repository may return target columns
        # separately from the feature columns.
        data = pd.concat(
            [features, targets],
            axis=1
        )

        if "G3" not in data.columns:
            raise ValueError(
                "The downloaded dataset does not contain G3."
            )

        data = data.loc[:, ~data.columns.duplicated()]

        required_columns = FEATURES + [TARGET]

        missing = [
            col for col in required_columns
            if col not in data.columns
        ]

        if missing:
            raise ValueError(
                f"Dataset is missing columns: {missing}"
            )

        data = data[required_columns].copy()

        # Convert columns to numeric values.
        for column in required_columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 30:
            raise ValueError(
                "Not enough valid records to train."
            )

        data.to_csv(DATA_PATH, index=False)

        return data

    except Exception as error:

        # Use a previously downloaded real dataset
        # if internet access is unavailable.
        if DATA_PATH.exists():

            data = pd.read_csv(DATA_PATH)

            if all(
                col in data.columns
                for col in FEATURES + [TARGET]
            ):
                return data.dropna(
                    subset=FEATURES + [TARGET]
                )

        raise RuntimeError(
            "Unable to download the UCI dataset. "
            "Check your internet connection and try again. "
            f"Details: {error}"
        )


def train_model():
    """
    Train and evaluate a Random Forest Regressor.
    Save the trained model to a pickle file.
    """

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    data = load_dataset()

    X = data[FEATURES]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_split=4,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test, predictions
    )

    mse = mean_squared_error(
        y_test, predictions
    )

    rmse = np.sqrt(mse)

    r2 = r2_score(
        y_test, predictions
    )

    results = {
        "MAE": float(mae),
        "MSE": float(mse),
        "RMSE": float(rmse),
        "R2": float(r2),
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test))
    }

    # Save model, feature names and evaluation results.
    model_data = {
        "model": model,
        "features": FEATURES,
        "metrics": results,
        "dataset": "UCI Student Performance",
        "target_scale": "0-20"
    }

    joblib.dump(model_data, MODEL_PATH)

    return results


def load_model():
    """Load the saved model or train it if missing."""

    if not MODEL_PATH.exists():
        train_model()

    try:
        model_data = joblib.load(MODEL_PATH)

        if "model" not in model_data:
            raise ValueError("Invalid model file.")

        return model_data

    except Exception:
        # Attempt to rebuild a corrupt model file.
        train_model()
        return joblib.load(MODEL_PATH)


def predict_performance(
    study_hours_per_day,
    previous_marks,
    previous_failures=0
):
    """
    Predict an estimated academic percentage.

    Study hours are converted to the UCI weekly
    study-time categories.

    Previous percentage is converted to 0-20 grades.
    """

    if not 0 <= previous_marks <= 100:
        raise ValueError(
            "Previous marks must be between 0 and 100."
        )

    if not 0.5 <= study_hours_per_day <= 16:
        raise ValueError(
            "Study hours must be between 0.5 and 16."
        )

    if not 0 <= previous_failures <= 3:
        raise ValueError(
            "Previous failures must be between 0 and 3."
        )

    # UCI studytime categories:
    # 1 = less than 2 hours/week
    # 2 = 2 to 5 hours/week
    # 3 = 5 to 10 hours/week
    # 4 = more than 10 hours/week

    weekly_hours = study_hours_per_day * 7

    if weekly_hours < 2:
        studytime = 1
    elif weekly_hours <= 5:
        studytime = 2
    elif weekly_hours <= 10:
        studytime = 3
    else:
        studytime = 4

    previous_grade = previous_marks / 5

    input_data = pd.DataFrame([{
        "studytime": studytime,
        "failures": previous_failures,
        "G1": previous_grade,
        "G2": previous_grade
    }])

    model_data = load_model()

    model = model_data["model"]

    prediction = float(
        model.predict(input_data)[0]
    )

    # Convert the 0-20 result into a percentage.
    percentage = (prediction / 20) * 100

    percentage = max(
        0.0,
        min(100.0, percentage)
    )

    return round(percentage, 2)


def get_feature_importance():
    """Return the model's feature importance."""

    model_data = load_model()

    model = model_data["model"]

    return {
        feature: round(float(importance), 4)
        for feature, importance in zip(
            FEATURES,
            model.feature_importances_
        )
    }


def get_model_metrics():
    """Return the saved model evaluation metrics."""

    model_data = load_model()

    return model_data["metrics"]

def predict_student_performance(
    study_hours_per_day,
    attendance,
    previous_marks,
    subject_difficulty,
    pending_assignments,
    confidence_level
):
    """
    Generate a student score estimate using the trained model.

    The existing UCI model uses studytime, failures, G1 and G2.
    Other form inputs are accepted for future recommendations,
    but are not used by this particular model.
    """

    if not 0.5 <= study_hours_per_day <= 16:
        raise ValueError("Study hours must be between 0.5 and 16.")

    if not 0 <= attendance <= 100:
        raise ValueError("Attendance must be between 0 and 100.")

    if not 0 <= previous_marks <= 100:
        raise ValueError("Previous marks must be between 0 and 100.")

    if not 0 <= pending_assignments <= 100:
        raise ValueError("Pending assignments must be between 0 and 100.")

    if not 1 <= confidence_level <= 10:
        raise ValueError("Confidence level must be between 1 and 10.")

    difficulty_values = ["Easy", "Medium", "Hard"]

    if subject_difficulty not in difficulty_values:
        raise ValueError("Select Easy, Medium, or Hard.")

    # Use the existing model's expected input format.
    estimated_score = predict_performance(
        study_hours_per_day=study_hours_per_day,
        previous_marks=previous_marks,
        previous_failures=0
    )

    return estimated_score
