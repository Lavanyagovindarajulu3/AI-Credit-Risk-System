import os
import joblib
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "credit_model.pkl"
)


# ============================================================
# MODEL CACHE
# ============================================================

_model_package = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    global _model_package

    if _model_package is not None:
        return _model_package

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Trained credit risk model was not found. "
            "Please run: python models/train_model.py"
        )

    _model_package = joblib.load(
        MODEL_PATH
    )

    return _model_package


# ============================================================
# PREDICT CREDIT RISK
# ============================================================

def predict_credit_risk(input_data):

    package = load_model()

    model = package["model"]

    label_encoder = package["label_encoder"]

    feature_columns = package["features"]

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    row = {}

    for feature in feature_columns:

        if feature not in input_data:

            raise ValueError(
                f"Missing model feature: {feature}"
            )

        row[feature] = input_data[feature]

    input_df = pd.DataFrame(
        [row],
        columns=feature_columns
    )

    # --------------------------------------------------------
    # Ensure numerical values
    # --------------------------------------------------------

    for feature in feature_columns:

        input_df[feature] = pd.to_numeric(
            input_df[feature],
            errors="raise"
        )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        input_df
    )[0]

    # Convert encoded prediction back to text
    risk_level = label_encoder.inverse_transform(
        [prediction]
    )[0]

    # --------------------------------------------------------
    # Prediction probabilities
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        input_df
    )[0]

    classes = label_encoder.classes_

    probability_map = {
        classes[index]: float(probabilities[index])
        for index in range(len(classes))
    }

    probability = float(
        probabilities[prediction]
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "risk_level": risk_level,
        "probability": probability,
        "probabilities": probability_map
    }


# ============================================================
# TEST MODEL FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    sample_data = {
        "Applicant_Age": 30,
        "Annual_Income": 600000,
        "Employment_Years": 5,
        "Loan_Amount": 200000,
        "Loan_Term": 36,
        "Existing_Loans": 1,
        "Monthly_Debt": 10000,
        "Savings": 150000,
        "Assets": 500000,
        "Dependents": 2,
        "Credit_History": 5,
        "Previous_Defaults": 0,
        "Credit_Score": 750
    }

    try:

        result = predict_credit_risk(
            sample_data
        )

        print("\nPrediction Result")
        print("-----------------")

        print(
            "Risk Level:",
            result["risk_level"]
        )

        print(
            "Probability:",
            f"{result['probability'] * 100:.2f}%"
        )

        print(
            "\nProbabilities:"
        )

        for risk, probability in result[
            "probabilities"
        ].items():

            print(
                f"{risk}: "
                f"{probability * 100:.2f}%"
            )

    except Exception as error:

        print(
            f"\nPrediction failed: {error}"
        )