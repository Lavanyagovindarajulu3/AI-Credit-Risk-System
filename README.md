# AI-Powered Credit Risk Assessment System Using Machine Learning

## 📌 Project Overview

The AI-Powered Credit Risk Assessment System is a web-based application developed using Python Flask and Machine Learning. It helps banks and financial institutions evaluate loan applicants by predicting credit risk based on customer information.

The system uses a Random Forest Machine Learning model to classify applicants into different risk categories and generate a credit score.

---

## 🎯 Objectives

- Predict loan approval risk using Machine Learning.
- Generate a credit score for each applicant.
- Reduce manual loan verification.
- Improve accuracy in credit risk assessment.
- Provide an easy-to-use web interface.

---

## 🛠 Technologies Used

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Machine Learning
- Pandas
- NumPy
- Scikit-learn
- Random Forest Algorithm
- Joblib

### Other Libraries
- Matplotlib
- Seaborn
- ReportLab

---

## 📂 Project Structure

```
AI-Credit-Risk-System/
│
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── database.sql
│
├── dataset/
│   └── credit_data.csv
│
├── model/
│   └── credit_model.pkl
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── loan_form.html
│   ├── result.html
│   └── admin.html
│
├── reports/
│
└── utils/
    └── predictor.py
```

---

## ⚙ Features

- User Registration
- User Login
- Admin Login
- Loan Application Form
- Credit Score Prediction
- Risk Classification
- Loan Approval Recommendation
- Dashboard
- PDF Report Generation
- MySQL Database Integration

---

## 🤖 Machine Learning Model

Algorithm Used:

- Random Forest Classifier

Input Features:

- Age
- Income
- Employment Status
- Loan Amount
- Credit History
- Existing Loans
- Loan Duration

Output:

- Credit Score
- Risk Level
  - Low Risk
  - Medium Risk
  - High Risk

---

## 🗄 Database

Database Name:

```
credit_risk_db
```

Main Tables:

- users
- loan_applications
- predictions

---

## 🚀 Installation

### Step 1

Clone the repository

```
git clone <repository-url>
```

### Step 2

Create Virtual Environment

```
python -m venv venv
```

### Step 3

Activate Virtual Environment

Windows

```
venv\Scripts\activate
```

### Step 4

Install Required Packages

```
pip install -r requirements.txt
```

### Step 5

Import Database

```
database.sql
```

into MySQL.

### Step 6

Train the Machine Learning Model

```
python train_model.py
```

### Step 7

Run Flask Application

```
python app.py
```

---

## 🌐 Open in Browser

```
http://127.0.0.1:5000
```

---

## 👩‍💻 Developer

Project Title:

AI-Powered Credit Risk Assessment System Using Machine Learning

Developed as a Final Year MCA Project.

---

## 📜 License

This project is developed for educational and academic purposes.