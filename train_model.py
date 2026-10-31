
from pathlib import Path
import sys

# Allow Python to find the modules folder.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.ml_model import train_model


def main():
    print("\n====================================")
    print(" SMARTSTUDY AI - MODEL TRAINING")
    print("====================================\n")

    try:
        print("Downloading and preparing UCI dataset...")

        results = train_model()

        print("\nModel training completed!")

        print("\nEvaluation Results")
        print("------------------------------")

        for metric, value in results.items():
            print(f"{metric}: {value}")

        print("\nSaved model:")
        print(BASE_DIR / "models" / "performance_model.pkl")

        print("\nTraining finished successfully!")

    except Exception as error:
        print("\nModel training failed.")
        print(f"Reason: {error}")


if __name__ == "__main__":
    main()
