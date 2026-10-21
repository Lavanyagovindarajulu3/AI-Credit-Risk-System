import os
import sys
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import LabelEncoder


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "credit_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "credit_model.pkl"
)


# ============================================================
# FEATURES USED BY THE MODEL
# ============================================================

FEATURE_COLUMNS = [
    "Applicant_Age",
    "Annual_Income",
    "Employment_Years",
    "Loan_Amount",
    "Loan_Term",
    "Existing_Loans",
    "Monthly_Debt",
    "Savings",
    "Assets",
    "Dependents",
    "Credit_History",
    "Previous_Defaults",
    "Credit_Score"
]

TARGET_COLUMN = "Risk_Level"


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    if not os.path.exists(DATASET_PATH):
        print("\nERROR: Dataset file not found.")
        print(f"Expected location: {DATASET_PATH}")
        sys.exit(1)

    print("\nLoading dataset...")

    data = pd.read_csv(DATASET_PATH)

    print(
        f"Dataset loaded successfully: "
        f"{data.shape[0]} rows, {data.shape[1]} columns"
    )

    return data


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_dataset(data):

    required_columns = FEATURE_COLUMNS + [
        TARGET_COLUMN
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        print("\nERROR: Missing columns in dataset:")

        for column in missing_columns:
            print(f" - {column}")

        sys.exit(1)

    print("Dataset columns validated successfully.")


# ============================================================
# CLEAN DATA
# ============================================================

def clean_dataset(data):

    data = data.copy()

    # Remove completely empty rows
    data.dropna(
        how="all",
        inplace=True
    )

    # Remove duplicate records
    data.drop_duplicates(
        inplace=True
    )

    # Convert numerical columns
    numerical_columns = [
        column
        for column in FEATURE_COLUMNS
        if column in data.columns
    ]

    for column in numerical_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Remove rows with missing numerical values
    data.dropna(
        subset=FEATURE_COLUMNS,
        inplace=True
    )

    # Clean target
    data[TARGET_COLUMN] = (
        data[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .str.title()
    )

    valid_targets = {
        "Low",
        "Medium",
        "High"
    }

    data = data[
        data[TARGET_COLUMN].isin(valid_targets)
    ]

    data.reset_index(
        drop=True,
        inplace=True
    )

    print(
        f"Clean dataset: "
        f"{len(data)} records"
    )

    return data


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    data = load_dataset()

    validate_dataset(data)

    data = clean_dataset(data)

    if len(data) < 20:

        print(
            "\nERROR: Dataset must contain at least "
            "20 valid records."
        )

        sys.exit(1)

    X = data[FEATURE_COLUMNS]

    y = data[TARGET_COLUMN]

    # --------------------------------------------------------
    # Encode target labels
    # --------------------------------------------------------

    label_encoder = LabelEncoder()

    y_encoded = label_encoder.fit_transform(y)

    print("\nRisk classes:")

    for encoded_value, class_name in enumerate(
        label_encoder.classes_
    ):
        print(
            f" {encoded_value} -> {class_name}"
        )

    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded
    )

    print(
        f"\nTraining records: {len(X_train)}"
    )

    print(
        f"Testing records: {len(X_test)}"
    )

    # --------------------------------------------------------
    # Random Forest Classifier
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=300,
        criterion="gini",
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining Random Forest model...")

    model.fit(
        X_train,
        y_train
    )

    print("Model training completed.")

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    y_prediction = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        y_prediction
    )

    print(
        f"\nModel Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_prediction,
            target_names=label_encoder.classes_,
            zero_division=0
        )
    )

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_prediction
        )
    )

    # --------------------------------------------------------
    # Feature Importance
    # --------------------------------------------------------

    importance = pd.DataFrame({
        "Feature": FEATURE_COLUMNS,
        "Importance": model.feature_importances_
    })

    importance.sort_values(
        by="Importance",
        ascending=False,
        inplace=True
    )

    print("\nFeature Importance:")

    for _, row in importance.iterrows():

        print(
            f"{row['Feature']}: "
            f"{row['Importance']:.4f}"
        )

    # --------------------------------------------------------
    # Create model directory
    # --------------------------------------------------------

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save complete model package
    # --------------------------------------------------------

    model_package = {
        "model": model,
        "label_encoder": label_encoder,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "version": "1.0"
    }

    joblib.dump(
        model_package,
        MODEL_PATH
    )

    print(
        f"\nModel saved successfully:"
        f"\n{MODEL_PATH}"
    )

    print(
        "\nTraining process completed successfully."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    train_model()