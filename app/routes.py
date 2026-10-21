from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)
from io import BytesIO

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app.database import  fetch_one, fetch_all,execute_query
from models.predict import predict_credit_risk

import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


# ============================================================
# BLUEPRINT
# ============================================================

main = Blueprint("main", __name__)


# ============================================================
# LOGIN CHECK HELPERS
# ============================================================

def login_required():
    """
    Use inside routes that require a logged-in user.
    """
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return False
    return True


def admin_required():
    """
    Use inside routes that require an administrator.
    """
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return False

    if session.get("role") != "admin":
        flash("Access denied. Admin access required.", "danger")
        return False

    return True


# ============================================================
# CREDIT SCORE CALCULATION
# ============================================================

def calculate_credit_score(
    annual_income,
    monthly_debt,
    employment_years,
    savings,
    assets,
    credit_history,
    previous_defaults,
    existing_loans,
    loan_amount,
    dependents
):
    """
    Project-specific credit score.

    IMPORTANT:
    This is not an official bank or credit-bureau score.
    It is used only for this academic project.
    """

    score = 350.0

    # Credit history: 1 to 5
    credit_history = max(1, min(int(credit_history), 5))
    score += (credit_history - 1) * 50

    # Income compared with requested loan
    if loan_amount > 0:
        income_loan_ratio = annual_income / loan_amount

        if income_loan_ratio >= 2:
            score += 150
        elif income_loan_ratio >= 1.5:
            score += 120
        elif income_loan_ratio >= 1:
            score += 90
        elif income_loan_ratio >= 0.75:
            score += 50
        else:
            score += 20

    # Monthly debt ratio
    monthly_income = annual_income / 12 if annual_income > 0 else 0

    if monthly_income > 0:
        debt_ratio = monthly_debt / monthly_income

        if debt_ratio <= 0.20:
            score += 100
        elif debt_ratio <= 0.40:
            score += 70
        elif debt_ratio <= 0.60:
            score += 40
        else:
            score += 10

    # Employment stability
    score += min(employment_years * 8, 80)

    # Savings compared with loan
    if loan_amount > 0:
        savings_ratio = savings / loan_amount
        score += min(savings_ratio * 100, 100)

        # Assets compared with loan
        asset_ratio = assets / loan_amount
        score += min(asset_ratio * 50, 100)

    # Existing loans reduce score
    score -= existing_loans * 15

    # Previous defaults reduce score
    score -= previous_defaults * 60

    # Dependents
    score -= min(dependents * 5, 25)

    # Keep between 300 and 900
    score = max(300, min(round(score), 900))

    return int(score)


# ============================================================
# HOME
# ============================================================

@main.route("/")
def index():
    return render_template("index.html")


# ============================================================
# LOGIN
# ============================================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.", "danger")
            return render_template("login.html")

        user = fetch_one(
            """
            SELECT *
            FROM users
            WHERE email = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (email,)
        )

        password_valid = False

        if user:

            password_hash = user.get("password_hash")

            # Check hashed password
            if password_hash:

                try:
                    password_valid = check_password_hash(
                        password_hash,
                        password
                    )
                except Exception:
                    password_valid = False

            # Support old users whose password is stored plainly
            if not password_valid and user.get("password"):
                password_valid = (
                    user["password"] == password
                )

        if not user or not password_valid:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template("login.html")

        # Save login information
        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user.get("full_name", "")
        session["user_email"] = user.get("email", "")
        session["role"] = user.get("role", "user")

        flash(
            "Login successful!",
            "success"
        )

        # Admin -> Admin Dashboard
        if user.get("role") == "admin":
            return redirect(
                url_for("main.admin_dashboard")
            )

        # Normal user -> User Dashboard
        return redirect(
            url_for("main.dashboard")
        )

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@main.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("main.login")
    )


# ============================================================
# REGISTER
# ============================================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not name:
            flash("Name is required.", "danger")
            return render_template("register.html")

        if not email:
            flash("Email is required.", "danger")
            return render_template("register.html")

        if not password:
            flash("Password is required.", "danger")
            return render_template("register.html")

        existing_user = fetch_one(
            """
            SELECT id
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return render_template("register.html")

        password_hash = generate_password_hash(password)

        # This matches the users table used by the project.
        execute_query(
            """
            INSERT INTO users (
                full_name,
                name,
                email,
                password_hash,
                role
            )
            VALUES (
                %s, %s, %s, %s, %s
            )
            """,
            (
                full_name,
                full_name,
                email,
               generate_password_hash(password),
                "user"
            )
        )

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect(
            url_for("main.login")
        )

    return render_template("register.html")


# ============================================================
# USER DASHBOARD
# ============================================================

@main.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(
            url_for("main.login")
        )

    user_id = session["user_id"]

    applications = fetch_all(
        """
        SELECT *
        FROM loan_applications
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (user_id,)
    ) or []

    application_count = len(applications)

    latest_application = (
        applications[0]
        if applications
        else None
    )

    credit_score = None
    risk_level = None
    recommendation = None

    credit_score_percentage = 0
    score_category = "Not available"

    if latest_application:

        credit_score = latest_application.get(
            "credit_score"
        )

        risk_level = latest_application.get(
            "risk_level"
        )

        recommendation = latest_application.get(
            "recommendation"
        )

        if credit_score is not None:

            credit_score = int(
                credit_score
            )

            credit_score_percentage = min(
                round(
                    (credit_score / 900) * 100,
                    2
                ),
                100
            )

            if credit_score < 580:
                score_category = "Needs Improvement"

            elif credit_score < 670:
                score_category = "Fair"

            elif credit_score < 740:
                score_category = "Good"

            elif credit_score < 800:
                score_category = "Very Good"

            else:
                score_category = "Excellent"

    return render_template(
        "dashboard.html",
        applications=applications,
        application_count=application_count,
        latest_application=latest_application,
        credit_score=credit_score,
        risk_level=risk_level,
        recommendation=recommendation,
        credit_score_percentage=credit_score_percentage,
        score_category=score_category
    )
# ============================================================
# USER APPLICATION HISTORY
# ============================================================

@main.route("/application-history")
def application_history():

    if not login_required():
        return redirect(
            url_for("main.login")
        )

    try:

        applications = fetch_all(
            """
            SELECT *
            FROM loan_applications
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ) or []

        return render_template(
            "application_history.html",
            applications=applications
        )

    except Exception as error:

        print(
            "APPLICATION HISTORY ERROR:",
            error
        )

        return (
            "Application History Error: "
            + str(error)
        )

# ============================================================
# USER - VIEW SINGLE APPLICATION
# ============================================================

@main.route("/view-application/<int:application_id>")
def view_application(application_id):

    # --------------------------------------------------------
    # CHECK USER LOGIN
    # --------------------------------------------------------

    if not login_required():
        return redirect(url_for("main.login"))

    try:

        # ----------------------------------------------------
        # GET ONLY THE LOGGED-IN USER'S APPLICATION
        # ----------------------------------------------------

        application = fetch_one(
            """
            SELECT *
            FROM loan_applications
            WHERE id = %s
            AND user_id = %s
            """,
            (
                application_id,
                session["user_id"]
            )
        )

        # ----------------------------------------------------
        # APPLICATION NOT FOUND
        # ----------------------------------------------------

        if not application:
            return "Application not found", 404

        # ----------------------------------------------------
        # SHOW APPLICATION DETAILS
        # ----------------------------------------------------

        return render_template(
            "application_details.html",
            application=application
        )

    except Exception as error:

        print(
            "USER VIEW APPLICATION ERROR:",
            error
        )

        return (
            "User View Application Error: "
            + str(error)
        ), 500
    
# ============================================================
# LOAN APPLICATION
# ============================================================
@main.route(
    "/loan-application",
    methods=["GET", "POST"]
)
def loan_application():

    if not login_required():
        return redirect(
            url_for("main.login")
        )

    if request.method == "POST":

        try:

            user_id = session["user_id"]

            # ------------------------------------------------
            # PERSONAL DETAILS
            # ------------------------------------------------

            applicant_name = request.form.get(
                "applicant_name",
                ""
            ).strip()

            age = int(
                request.form.get(
                    "age",
                    0
                )
            )

            gender = request.form.get(
                "gender",
                ""
            )

            marital_status = request.form.get(
                "marital_status",
                ""
            )

            dependents = int(
                request.form.get(
                    "dependents",
                    0
                )
            )

            # ------------------------------------------------
            # EMPLOYMENT DETAILS
            # ------------------------------------------------

            employment_status = request.form.get(
                "employment_status",
                ""
            )

            occupation = request.form.get(
                "occupation",
                ""
            )

            education = request.form.get(
                "education",
                ""
            )

            employment_years = float(
                request.form.get(
                    "employment_years",
                    0
                )
            )

            # ------------------------------------------------
            # FINANCIAL DETAILS
            # ------------------------------------------------

            annual_income = float(
                request.form.get(
                    "annual_income",
                    0
                )
            )

            monthly_income = float(
                request.form.get(
                    "monthly_income",
                    0
                )
            )

            loan_amount = float(
                request.form.get(
                    "loan_amount",
                    0
                )
            )

            loan_term = int(
                request.form.get(
                    "loan_term",
                    0
                )
            )

            existing_loans = int(
                request.form.get(
                    "existing_loans",
                    0
                )
            )

            monthly_debt = float(
                request.form.get(
                    "monthly_debt",
                    0
                )
            )

            # ------------------------------------------------
            # CREDIT DETAILS
            # ------------------------------------------------

            credit_history = int(
                request.form.get(
                    "credit_history",
                    1
                )
            )

            previous_defaults = int(
                request.form.get(
                    "previous_defaults",
                    0
                )
            )

            # ------------------------------------------------
            # PROPERTY DETAILS
            # ------------------------------------------------

            property_area = request.form.get(
                "property_area",
                ""
            )

            property_value = float(
                request.form.get(
                    "property_value",
                    0
                )
            )

            # ------------------------------------------------
            # SAVINGS AND ASSETS
            # ------------------------------------------------

            savings = float(
                request.form.get(
                    "savings",
                    0
                )
            )

            assets = float(
                request.form.get(
                    "assets",
                    0
                )
            )

            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if not applicant_name:
                flash(
                    "Applicant name is required.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if age <= 0:
                flash(
                    "Please enter a valid age.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if annual_income <= 0:
                flash(
                    "Please enter a valid annual income.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if monthly_income <= 0:
                flash(
                    "Please enter a valid monthly income.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if loan_amount <= 0:
                flash(
                    "Please enter a valid loan amount.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if loan_term <= 0:
                flash(
                    "Please enter a valid loan term.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if employment_years < 0:
                flash(
                    "Employment years cannot be negative.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            if savings < 0 or assets < 0:
                flash(
                    "Savings and assets cannot be negative.",
                    "danger"
                )
                return render_template(
                    "loan_application.html"
                )

            # ------------------------------------------------
            # CREDIT SCORE
            # ------------------------------------------------

            credit_score = calculate_credit_score(
                annual_income=annual_income,
                monthly_debt=monthly_debt,
                employment_years=employment_years,
                savings=savings,
                assets=assets,
                credit_history=credit_history,
                previous_defaults=previous_defaults,
                existing_loans=existing_loans,
                loan_amount=loan_amount,
                dependents=dependents
            )

            # ------------------------------------------------
            # RANDOM FOREST INPUT
            # ------------------------------------------------

            model_input = {

                "Applicant_Age": age,

                "Annual_Income": annual_income,

                "Employment_Years":
                    employment_years,

                "Loan_Amount":
                    loan_amount,

                "Loan_Term":
                    loan_term,

                "Existing_Loans":
                    existing_loans,

                "Monthly_Debt":
                    monthly_debt,

                "Savings":
                    savings,

                "Assets":
                    assets,

                "Dependents":
                    dependents,

                "Credit_History":
                    credit_history,

                "Previous_Defaults":
                    previous_defaults,

                "Credit_Score":
                    credit_score
            }

            # ------------------------------------------------
            # AI PREDICTION
            # ------------------------------------------------

            prediction = predict_credit_risk(
                model_input
            )

            risk_level = prediction[
                "risk_level"
            ]

            risk_probability = prediction[
                "probability"
            ]

            # ------------------------------------------------
            # RECOMMENDATION
            # ------------------------------------------------

            if risk_level == "Low":

                recommendation = "Approve"

                prediction_reason = (
                    "The applicant has a low "
                    "predicted credit risk based "
                    "on income, credit score, debt, "
                    "savings, assets and repayment "
                    "history."
                )

                application_status = "Approved"

            elif risk_level == "Medium":

                recommendation = "Review"

                prediction_reason = (
                    "The applicant has a medium "
                    "predicted credit risk. The "
                    "application should be reviewed "
                    "carefully before approval."
                )

                application_status = "Pending"

            else:

                recommendation = "Reject"

                prediction_reason = (
                    "The applicant has a high "
                    "predicted credit risk based "
                    "on the financial and credit "
                    "information provided."
                )

                application_status = "Rejected"

            # ------------------------------------------------
            # SAVE APPLICATION
            # ------------------------------------------------

            application_id = execute_query(
                """
                INSERT INTO loan_applications (

                    user_id,
                    applicant_name,
                    age,
                    gender,
                    marital_status,
                    dependents,

                    employment_status,
                    occupation,
                    education,
                    employment_years,

                    annual_income,
                    monthly_income,
                    loan_amount,
                    loan_term,
                    existing_loans,
                    monthly_debt,

                    credit_history,
                    credit_score,

                    property_area,
                    property_value,

                    risk_level,
                    risk_probability,
                    recommendation,
                    prediction_reason,
                    application_status,

                    savings,
                    assets,
                    previous_defaults

                )

                VALUES (

                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s

                )
                """,

                (
                    user_id,
                    applicant_name,
                    age,
                    gender,
                    marital_status,
                    dependents,

                    employment_status,
                    occupation,
                    education,
                    employment_years,

                    annual_income,
                    monthly_income,
                    loan_amount,
                    loan_term,
                    existing_loans,
                    monthly_debt,

                    credit_history,
                    credit_score,

                    property_area,
                    property_value,

                    risk_level,
                    risk_probability,
                    recommendation,
                    prediction_reason,
                    application_status,

                    savings,
                    assets,
                    previous_defaults
                )
            )

            flash(
                "Application submitted successfully! "
                f"Credit Score: {credit_score} | "
                f"AI Risk: {risk_level} | "
                f"Recommendation: {recommendation}",
                "success"
            )

            return redirect(
                url_for("main.prediction_result", application_id=application_id))

        except Exception as error:

            print(
                "LOAN APPLICATION ERROR:",
                error
            )

            flash(
                f"Application failed: {error}",
                "danger"
            )

            return render_template(
                "loan_application.html"
            )

    return render_template(
        "loan_application.html"
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@main.route("/admin/dashboard")
def admin_dashboard():

    if not admin_required():
        return redirect(
            url_for("main.login")
        )
    search = request.args.get(
    "search",
    ""
    ).strip()

    risk = request.args.get(
        "risk",
        ""
    ).strip()

    status = request.args.get(
       "status",
       ""
    ).strip()

    recommendation = request.args.get(
      "recommendation",
    ""
    ).strip()

    try:

        # ------------------------------------------------
        # TOTAL USERS
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM users
            """
        )

        total_users = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # TOTAL APPLICATIONS
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            """
        )

        total_applications = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # APPROVED
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE recommendation = 'Approve'
            """
        )

        approved_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # HIGH RISK
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE risk_level = 'High'
            """
        )

        high_risk_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # MEDIUM RISK
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE risk_level = 'Medium'
            """
        )

        medium_risk_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # LOW RISK
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE risk_level = 'Low'
            """
        )

        low_risk_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # REVIEW
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE recommendation = 'Review'
            """
        )

        review_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # REJECTED
        # ------------------------------------------------

        result = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM loan_applications
            WHERE recommendation = 'Reject'
            """
        )

        rejected_count = (
            result["count"]
            if result
            else 0
        )

        # ------------------------------------------------
        # RECENT APPLICATIONS
        # ------------------------------------------------
        applications = fetch_all(
        """
        SELECT
            la.id,
            la.applicant_name,
            la.loan_amount,
            la.credit_score,
            la.risk_level,
            la.risk_probability,
            la.recommendation,
            la.application_status,
            la.created_at,
            la.user_id,
            u.full_name,
            u.email

        FROM loan_applications la

        LEFT JOIN users u
            ON la.user_id = u.id

        WHERE
            (%s = '' OR la.applicant_name LIKE %s)
             AND
            (%s = '' OR la.risk_level = %s)
            AND
            (%s = '' OR la.application_status = %s)
            AND
            (%s = '' OR la.recommendation = %s)

        ORDER BY la.id DESC
        """,
        (
            search,
            "%" + search + "%",

            risk,
            risk,

            status,
            status,

            recommendation,
            recommendation
        )
     
    ) or []

        # ------------------------------------------------
        # USERS
        # ------------------------------------------------

        users = fetch_all(
        """
        SELECT
            u.id,
            u.full_name,
            u.email,
            u.phone,
            u.role,
            u.created_at,
            COUNT(la.id) AS application_count

        FROM users u

        LEFT JOIN loan_applications la
            ON u.id = la.user_id

        GROUP BY
            u.id,
            u.full_name,
            u.email,
            u.phone,
            u.role,
            u.created_at

        ORDER BY u.id DESC
        """
    ) or []

        return render_template(
            "admin_dashboard.html",

            total_users=total_users,

            total_applications=
                total_applications,

            approved_count=
                approved_count,

            high_risk_count=
                high_risk_count,

            medium_risk_count=
                medium_risk_count,

            low_risk_count=
                low_risk_count,

            review_count=
                review_count,

            rejected_count=
                rejected_count,

            applications=
                applications,

            users=
                users,

            search=search,

            risk=risk,

            status=status,

            recommendation=recommendation
        )

    except Exception as error:

        print(
            "ADMIN DASHBOARD ERROR:",
            error
        )

        return (
            "Admin Dashboard Error: "
            + str(error)
        )


# ============================================================
# ADMIN APPLICATION DETAILS
#
# IMPORTANT:
# There is ONLY ONE view_application function in this file.
# This prevents:
# AssertionError:
# View function mapping is overwriting an existing endpoint
# function: main.view_application
# ============================================================
# ============================================================
# ADMIN APPLICATIONS
# ============================================================

@main.route("/admin/applications")
def admin_applications():

    # Admin access required
    if not admin_required():
        return redirect(
            url_for("main.login")
        )

    try:

        applications = fetch_all(
            """
            SELECT
                la.id,
                la.applicant_name,
                la.loan_amount,
                la.credit_score,
                la.risk_level,
                la.risk_probability,
                la.recommendation,
                la.application_status,
                la.created_at

            FROM loan_applications la

            ORDER BY la.id DESC
            """
        ) or []

        # ------------------------------------------------
        # STATISTICS
        # ------------------------------------------------

        total_applications = len(applications)

        approved = sum(
            1
            for application in applications
            if application.get("application_status") == "Approved"
        )

        under_review = sum(
            1
            for application in applications
            if application.get("application_status") in [
                "Pending",
                "Review"
            ]
        )

        rejected = sum(
            1
            for application in applications
            if application.get("application_status") == "Rejected"
        )

        return render_template(
            "admin_applications.html",

            applications=applications,

            total_applications=total_applications,

            approved=approved,

            under_review=under_review,

            rejected=rejected
        )

    except Exception as error:

        print(
            "ADMIN APPLICATIONS ERROR:",
            error
        )

        return (
            "Admin Applications Error: "
            + str(error)
        )

@main.route("/admin/application/<int:application_id>")
def admin_view_application(application_id):

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    try:

        application = fetch_one(
            """
            SELECT *
            FROM loan_applications
            WHERE id = %s
            """,
            (application_id,)
        )

        if not application:
            return "Application not found", 404

        return render_template(
            "application_details.html",
            application=application
        )

    except Exception as error:

        print(
            "ADMIN VIEW APPLICATION ERROR:",
            error
        )

        return (
            "Admin View Application Error: "
            + str(error)
        ), 500
# ============================================================
# ADMIN VIEW USER APPLICATIONS
# ============================================================

@main.route("/admin/user/<int:user_id>/applications")
def admin_user_applications(user_id):

    if not admin_required():
        return redirect(
            url_for("main.login")
        )

    try:

        # Get user details
        user_item = fetch_one(
            """
            SELECT
                id,
                full_name,
                email,
                phone,
                role,
                created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        if not user_item:
            flash(
                "User not found.",
                "danger"
            )

            return redirect(
                url_for("main.admin_dashboard")
            )

        # Get this user's applications
        applications = fetch_all(
            """
            SELECT *
            FROM loan_applications
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,)
        ) or []

        return render_template(
            "admin_user_applications.html",
            user_item=user_item,
            applications=applications
        )

    except Exception as error:

        print(
            "ADMIN USER APPLICATIONS ERROR:",
            error
        )

        return (
            "Admin User Applications Error: "
            + str(error)
        ), 500
         
# ============================================================
# ADMIN - UPDATE APPLICATION STATUS
# ============================================================

@main.route(
    "/admin/application/<int:application_id>/status",
    methods=["POST"]
)
def admin_update_application_status(application_id):

    # --------------------------------------------------------
    # CHECK ADMIN LOGIN
    # --------------------------------------------------------

    if not admin_required():
        return redirect(
            url_for("main.login")
        )

    try:

        # ----------------------------------------------------
        # GET STATUS FROM FORM
        # ----------------------------------------------------

        status = request.form.get(
            "status",
            "Pending"
        ).strip()

        # ----------------------------------------------------
        # ALLOWED STATUS VALUES
        # ----------------------------------------------------

        allowed_statuses = {
            "Pending",
            "Approved",
            "Rejected"
        }

        if status not in allowed_statuses:

            flash(
                "Invalid application status.",
                "danger"
            )

            return redirect(
                url_for(
                    "main.admin_view_application",
                    application_id=application_id
                )
            )

        # ----------------------------------------------------
        # CHECK APPLICATION EXISTS
        # ----------------------------------------------------

        application = fetch_one(
            """
            SELECT id
            FROM loan_applications
            WHERE id = %s
            """,
            (application_id,)
        )

        if not application:

            flash(
                "Application not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "main.admin_dashboard"
                )
            )

        # ----------------------------------------------------
        # UPDATE STATUS
        # ----------------------------------------------------

        execute_query(
            """
            UPDATE loan_applications

            SET application_status = %s

            WHERE id = %s
            """,
            (
                status,
                application_id
            )
        )

        # ----------------------------------------------------
        # SUCCESS MESSAGE
        # ----------------------------------------------------

        flash(
            "Application status updated successfully.",
            "success"
        )

        # ----------------------------------------------------
        # RETURN TO ADMIN APPLICATION DETAILS
        # ----------------------------------------------------

        return redirect(
            url_for(
                "main.admin_view_application",
                application_id=application_id
            )
        )

    except Exception as error:

        print(
            "UPDATE APPLICATION STATUS ERROR:",
            error
        )

        flash(
            f"Failed to update status: {error}",
            "danger"
        )

        return redirect(
            url_for(
                "main.admin_view_application",
                application_id=application_id
            )
        )
@main.route("/generate-report/<int:application_id>")
def generate_report(application_id):

    # Check admin login
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    try:

        # Get application
        application = fetch_one(
            """
            SELECT *
            FROM loan_applications
            WHERE id = %s
            """,
            (application_id,)
        )

        if not application:
            return "Application not found", 404


        # Create PDF in memory
        pdf_buffer = BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )


        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["Normal"]

        title_style.alignment = TA_CENTER


        elements = []


        # TITLE
        elements.append(
            Paragraph(
                "AI CREDIT RISK ASSESSMENT REPORT",
                title_style
            )
        )

        elements.append(Spacer(1, 20))


        # APPLICATION INFORMATION
        elements.append(
            Paragraph(
                "Application Information",
                heading_style
            )
        )

        elements.append(Spacer(1, 10))


        applicant_name = application.get(
            "applicant_name",
            "--"
        )

        application_id_value = application.get(
            "id",
            "--"
        )

        loan_amount = application.get(
            "loan_amount",
            "--"
        )

        credit_score = application.get(
            "credit_score",
            "--"
        )

        risk_level = application.get(
            "risk_level",
            "Pending"
        )

        recommendation = application.get(
            "recommendation",
            "Pending"
        )

        application_status = application.get(
            "application_status",
            "Pending"
        )


        data = [

            ["Application ID", str(application_id_value)],

            ["Applicant Name", str(applicant_name)],

            ["Loan Amount", "₹" + str(loan_amount)],

            ["Credit Score", str(credit_score)],

            ["Risk Level", str(risk_level)],

            ["Recommendation", str(recommendation)],

            ["Application Status", str(application_status)]

        ]


        table = Table(
            data,
            colWidths=[180, 300]
        )


        table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.black
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )

            ])
        )


        elements.append(table)

        elements.append(Spacer(1, 20))


        # ASSESSMENT SUMMARY
        elements.append(
            Paragraph(
                "Assessment Summary",
                heading_style
            )
        )

        elements.append(Spacer(1, 10))


        summary = (
            "The applicant has a "
            + str(risk_level)
            + " predicted credit risk based on "
            "income, credit score, debt, savings, "
            "assets and repayment history."
        )


        elements.append(
            Paragraph(
                summary,
                normal_style
            )
        )


        elements.append(Spacer(1, 30))


        elements.append(
            Paragraph(
                "Generated by AI Credit Risk Assessment System",
                normal_style
            )
        )


        # Build PDF
        doc.build(elements)


        # Move buffer to beginning
        pdf_buffer.seek(0)


        # Download PDF
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=
            f"credit_risk_report_{application_id}.pdf",
            mimetype="application/pdf"
        )


    except Exception as error:

        print(
            "PDF REPORT ERROR:",
            error
        )

        return (
            "PDF Report Error: "
            + str(error)
        ), 500
    
# ============================================================
# REPORTS PAGE
# ============================================================

@main.route("/reports")
def reports():

    if not login_required():
        return redirect(
            url_for("main.login")
        )

    # Admin sees all applications.
    # Normal user sees only their applications.

    if session.get("role") == "admin":

        applications = fetch_all(
            """
            SELECT
                la.*,
                u.full_name,
                u.email

            FROM loan_applications la

            LEFT JOIN users u
                ON la.user_id = u.id

            ORDER BY la.id DESC
            """
        ) or []

    else:

        applications = fetch_all(
            """
            SELECT *
            FROM loan_applications
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ) or []

    total_applications = len(
        applications
    )

    low_risk = sum(
        1
        for application in applications
        if application.get("risk_level") == "Low"
    )

    medium_risk = sum(
        1
        for application in applications
        if application.get("risk_level") == "Medium"
    )

    high_risk = sum(
        1
        for application in applications
        if application.get("risk_level") == "High"
    )

    approved_count = sum(
        1
        for application in applications
        if application.get("recommendation") == "Approve"
    )

    review_count = sum(
        1
        for application in applications
        if application.get("recommendation") == "Review"
    )

    rejected_count = sum(
        1
        for application in applications
        if application.get("recommendation") == "Reject"
    )

    if total_applications > 0:

        average_loan_amount = (
            sum(
                float(
                    application.get("loan_amount")
                    or 0
                )
                for application in applications
            )
            / total_applications
        )

        score_values = [
            float(
                application.get("credit_score")
                or 0
            )
            for application in applications
        ]

        average_credit_score = (
            sum(score_values)
            / total_applications
        )

    else:

        average_loan_amount = 0
        average_credit_score = 0

    return render_template(
        "reports.html",

        applications=applications,

        total_applications=
            total_applications,

        low_risk=
            low_risk,

        medium_risk=
            medium_risk,

        high_risk=
            high_risk,

        approved_count=
            approved_count,

        review_count=
            review_count,

        rejected_count=
            rejected_count,

        average_loan_amount=
            average_loan_amount,

        average_credit_score=
            average_credit_score
    )

# ============================================================
# PROFILE
# ============================================================

@main.route("/profile")
def profile():

    if not login_required():
        return redirect(
            url_for("main.login")
        )

    user = fetch_one(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    if not user:

        session.clear()

        flash(
            "User account not found.",
            "danger"
        )

        return redirect(
            url_for("main.login")
        )

    return render_template(
        "profile.html",
        user=user
    )


# ============================================================
# SIMPLE ERROR HANDLERS
# ============================================================

@main.app_errorhandler(404)
def page_not_found(error):

    return (
        "Page not found.",
        404
    )


@main.app_errorhandler(500)
def internal_server_error(error):

    return (
        "Internal server error.",
        500
    )
@main.route("/download_report/<int:application_id>")
def download_application_report(application_id):

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    try:

        # Get ONLY the selected application
        application = fetch_one(
            """
            SELECT *
            FROM loan_applications
            WHERE id = %s
              AND user_id = %s
            """,
            (
                application_id,
                session["user_id"]
            )
        )

        # Application doesn't exist
        if not application:
            flash(
                "Application not found.",
                "danger"
            )

            return redirect(
                url_for("main.application_history")
            )

        # Create PDF in memory
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        story = []

        # ------------------------------------------
        # TITLE
        # ------------------------------------------

        story.append(
            Paragraph(
                "AI Credit Risk Assessment Report",
                title_style
            )
        )

        story.append(
            Spacer(1, 20)
        )

        # ------------------------------------------
        # APPLICATION DETAILS
        # ------------------------------------------

        data = [
            [
                "Application ID",
                str(application.get("id", "N/A"))
            ],
            [
                "Applicant",
                str(
                    application.get(
                        "applicant_name",
                        "N/A"
                    )
                )
            ],
            [
                "Credit Score",
                str(
                    application.get(
                        "credit_score",
                        "N/A"
                    )
                )
            ],
            [
                "Risk Level",
                str(
                    application.get(
                        "risk_level",
                        "N/A"
                    )
                )
            ],
            [
                "Loan Amount",
                str(
                    application.get(
                        "loan_amount",
                        "N/A"
                    )
                )
            ],
            [
                "Recommendation",
                str(
                    application.get(
                        "recommendation",
                        "N/A"
                    )
                )
            ],
            [
                "Risk Probability",
                str(
                    application.get(
                        "risk_probability",
                        "N/A"
                    )
                )
            ],
            [
                "Application Status",
                str(
                    application.get(
                        "application_status",
                        "N/A"
                    )
                )
            ]
        ]

        table = Table(
            data,
            colWidths=[160, 290]
        )

        table.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(table)

        story.append(
            Spacer(1, 20)
        )

        # ------------------------------------------
        # PREDICTION REASON
        # ------------------------------------------

        story.append(
            Paragraph(
                "AI Prediction Reason",
                styles["Heading3"]
            )
        )

        prediction_reason = application.get(
            "prediction_reason",
            "No prediction reason available."
        )

        story.append(
            Paragraph(
                str(prediction_reason),
                styles["Normal"]
            )
        )

        # ------------------------------------------
        # BUILD PDF
        # ------------------------------------------

        doc.build(story)

        buffer.seek(0)

        # ------------------------------------------
        # DOWNLOAD
        # ------------------------------------------

        return send_file(
            buffer,
            as_attachment=True,
            download_name=(
                f"AI_Credit_Risk_Report_"
                f"{application_id}.pdf"
            ),
            mimetype="application/pdf"
        )

    except Exception as e:

        print(
            "PDF REPORT ERROR:",
            e
        )

        return (
            f"PDF Report Error: {str(e)}"
        )
    
# ============================================================
# AI PREDICTION RESULT
# ============================================================

@main.route("/prediction_result/<int:application_id>")
def prediction_result(application_id):

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    try:

        application = fetch_one(
            """
            SELECT *
            FROM loan_applications
            WHERE id = %s
              AND user_id = %s
            """,
            (
                application_id,
                session["user_id"]
            )
        )

        if not application:
            flash(
                "Application not found.",
                "danger"
            )

            return redirect(
                url_for("main.dashboard")
            )

        return render_template(
            "prediction_result.html",
            application=application
        )

    except Exception as error:

        print(
            "PREDICTION RESULT ERROR:",
            error
        )

        flash(
            f"Unable to load prediction result: {error}",
            "danger"
        )

        return redirect(
            url_for("main.dashboard")
        )