```javascript
/*
=========================================================
AI-POWERED CREDIT RISK ASSESSMENT SYSTEM
Frontend Validation
=========================================================
*/

"use strict";


/* =====================================================
   DOCUMENT READY
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    initializeRegistrationValidation();

    initializeLoanValidation();

    initializeLoginValidation();

    initializeProfileValidation();

});


/* =====================================================
   HELPER: SHOW INVALID MESSAGE
   ===================================================== */

function setInvalid(input, message) {

    if (!input) {
        return;
    }

    input.classList.add("is-invalid");
    input.classList.remove("is-valid");

    let feedback =
        input.parentElement.querySelector(
            ".custom-validation-message"
        );

    if (!feedback) {

        feedback =
            document.createElement("div");

        feedback.className =
            "invalid-feedback custom-validation-message";

        input.parentElement.appendChild(feedback);

    }

    feedback.textContent = message;

}


/* =====================================================
   HELPER: SHOW VALID
   ===================================================== */

function setValid(input) {

    if (!input) {
        return;
    }

    input.classList.remove("is-invalid");
    input.classList.add("is-valid");

    const feedback =
        input.parentElement.querySelector(
            ".custom-validation-message"
        );

    if (feedback) {
        feedback.remove();
    }

}


/* =====================================================
   HELPER: CLEAR VALIDATION
   ===================================================== */

function clearValidation(input) {

    if (!input) {
        return;
    }

    input.classList.remove("is-invalid");
    input.classList.remove("is-valid");

    const feedback =
        input.parentElement.querySelector(
            ".custom-validation-message"
        );

    if (feedback) {
        feedback.remove();
    }

}


/* =====================================================
   EMAIL VALIDATION
   ===================================================== */

function validateEmailField(input) {

    if (!input) {
        return false;
    }

    const email =
        input.value.trim();

    if (!email) {

        setInvalid(
            input,
            "Email address is required."
        );

        return false;

    }

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {

        setInvalid(
            input,
            "Enter a valid email address."
        );

        return false;

    }

    setValid(input);

    return true;

}


/* =====================================================
   PHONE VALIDATION
   ===================================================== */

function validatePhoneField(input) {

    if (!input) {
        return false;
    }

    const phone =
        input.value
            .trim()
            .replace(/[\s()-]/g, "");

    if (!phone) {

        setInvalid(
            input,
            "Phone number is required."
        );

        return false;

    }

    if (!/^\+?[0-9]{10,15}$/.test(phone)) {

        setInvalid(
            input,
            "Enter a valid phone number."
        );

        return false;

    }

    setValid(input);

    return true;

}


/* =====================================================
   REQUIRED TEXT FIELD
   ===================================================== */

function validateRequiredField(
    input,
    fieldName
) {

    if (!input) {
        return false;
    }

    const value =
        input.value.trim();

    if (!value) {

        setInvalid(
            input,
            `${fieldName} is required.`
        );

        return false;

    }

    setValid(input);

    return true;

}


/* =====================================================
   POSITIVE NUMBER
   ===================================================== */

function validatePositiveNumber(
    input,
    fieldName
) {

    if (!input) {
        return false;
    }

    const value =
        Number(input.value);

    if (
        Number.isNaN(value) ||
        value <= 0
    ) {

        setInvalid(
            input,
            `${fieldName} must be greater than zero.`
        );

        return false;

    }

    setValid(input);

    return true;

}


/* =====================================================
   NON-NEGATIVE NUMBER
   ===================================================== */

function validateNonNegativeNumber(
    input,
    fieldName
) {

    if (!input) {
        return false;
    }

    const value =
        Number(input.value);

    if (
        Number.isNaN(value) ||
        value < 0
    ) {

        setInvalid(
            input,
            `${fieldName} cannot be negative.`
        );

        return false;

    }

    setValid(input);

    return true;

}


/* =====================================================
   REGISTRATION VALIDATION
   ===================================================== */

function initializeRegistrationValidation() {

    const form =
        document.getElementById(
            "registrationForm"
        );

    if (!form) {
        return;
    }

    const fullName =
        document.getElementById(
            "full_name"
        );

    const email =
        document.getElementById(
            "email"
        );

    const phone =
        document.getElementById(
            "phone"
        );

    const password =
        document.getElementById(
            "password"
        );

    const confirmPassword =
        document.getElementById(
            "confirm_password"
        );


    /* ---------------------------------------------
       Full Name
       --------------------------------------------- */

    if (fullName) {

        fullName.addEventListener(
            "input",
            function () {

                const value =
                    fullName.value.trim();

                if (value.length < 3) {

                    setInvalid(
                        fullName,
                        "Name must contain at least 3 characters."
                    );

                } else {

                    setValid(fullName);

                }

            }
        );

    }


    /* ---------------------------------------------
       Email
       --------------------------------------------- */

    if (email) {

        email.addEventListener(
            "blur",
            function () {

                validateEmailField(email);

            }
        );

    }


    /* ---------------------------------------------
       Phone
       --------------------------------------------- */

    if (phone) {

        phone.addEventListener(
            "blur",
            function () {

                validatePhoneField(phone);

            }
        );

    }


    /* ---------------------------------------------
       Password
       --------------------------------------------- */

    if (password) {

        password.addEventListener(
            "input",
            function () {

                const value =
                    password.value;

                if (value.length < 8) {

                    setInvalid(
                        password,
                        "Password must contain at least 8 characters."
                    );

                } else {

                    setValid(password);

                }

            }
        );

    }


    /* ---------------------------------------------
       Confirm Password
       --------------------------------------------- */

    if (confirmPassword) {

        confirmPassword.addEventListener(
            "input",
            function () {

                if (
                    confirmPassword.value !==
                    password.value
                ) {

                    setInvalid(
                        confirmPassword,
                        "Passwords do not match."
                    );

                } else {

                    setValid(confirmPassword);

                }

            }
        );

    }


    /* ---------------------------------------------
       Submit
       --------------------------------------------- */

    form.addEventListener(
        "submit",
        function (event) {

            let valid = true;


            if (fullName) {

                if (
                    fullName.value.trim().length < 3
                ) {

                    setInvalid(
                        fullName,
                        "Enter your full name."
                    );

                    valid = false;

                }

            }


            if (
                email &&
                !validateEmailField(email)
            ) {

                valid = false;

            }


            if (
                phone &&
                !validatePhoneField(phone)
            ) {

                valid = false;

            }


            if (password) {

                if (password.value.length < 8) {

                    setInvalid(
                        password,
                        "Password must contain at least 8 characters."
                    );

                    valid = false;

                }

            }


            if (
                confirmPassword &&
                password &&
                confirmPassword.value !== password.value
            ) {

                setInvalid(
                    confirmPassword,
                    "Passwords do not match."
                );

                valid = false;

            }


            if (!valid) {

                event.preventDefault();

                const firstInvalid =
                    form.querySelector(
                        ".is-invalid"
                    );

                if (firstInvalid) {
                    firstInvalid.focus();
                }

            }

        }
    );

}


/* =====================================================
   LOGIN VALIDATION
   ===================================================== */

function initializeLoginValidation() {

    const form =
        document.getElementById(
            "loginForm"
        );

    if (!form) {
        return;
    }

    const email =
        document.getElementById(
            "email"
        );

    const password =
        document.getElementById(
            "password"
        );


    form.addEventListener(
        "submit",
        function (event) {

            let valid = true;


            if (
                email &&
                !validateEmailField(email)
            ) {

                valid = false;

            }


            if (password) {

                if (!password.value.trim()) {

                    setInvalid(
                        password,
                        "Password is required."
                    );

                    valid = false;

                } else {

                    setValid(password);

                }

            }


            if (!valid) {

                event.preventDefault();

            }

        }
    );

}


/* =====================================================
   LOAN APPLICATION VALIDATION
   ===================================================== */

function initializeLoanValidation() {

    const form =
        document.getElementById(
            "loanApplicationForm"
        );

    if (!form) {
        return;
    }


    const annualIncome =
        document.getElementById(
            "annual_income"
        );

    const loanAmount =
        document.getElementById(
            "loan_amount"
        );

    const loanTerm =
        document.getElementById(
            "loan_term"
        );

    const existingDebt =
        document.getElementById(
            "existing_debt"
        );

    const creditHistory =
        document.getElementById(
            "credit_history"
        );

    const previousDefaults =
        document.getElementById(
            "previous_defaults"
        );


    /* ---------------------------------------------
       Annual Income
       --------------------------------------------- */

    if (annualIncome) {

        annualIncome.addEventListener(
            "input",
            function () {

                validatePositiveNumber(
                    annualIncome,
                    "Annual income"
                );

            }
        );

    }


    /* ---------------------------------------------
       Loan Amount
       --------------------------------------------- */

    if (loanAmount) {

        loanAmount.addEventListener(
            "input",
            function () {

                validatePositiveNumber(
                    loanAmount,
                    "Loan amount"
                );

            }
        );

    }


    /* ---------------------------------------------
       Loan Term
       --------------------------------------------- */

    if (loanTerm) {

        loanTerm.addEventListener(
            "input",
            function () {

                const value =
                    Number(loanTerm.value);

                if (
                    Number.isNaN(value) ||
                    value <= 0 ||
                    value > 480
                ) {

                    setInvalid(
                        loanTerm,
                        "Loan term must be between 1 and 480 months."
                    );

                } else {

                    setValid(loanTerm);

                }

            }
        );

    }


    /* ---------------------------------------------
       Existing Debt
       --------------------------------------------- */

    if (existingDebt) {

        existingDebt.addEventListener(
            "input",
            function () {

                validateNonNegativeNumber(
                    existingDebt,
                    "Existing debt"
                );

            }
        );

    }


    /* ---------------------------------------------
       Previous Defaults
       --------------------------------------------- */

    if (previousDefaults) {

        previousDefaults.addEventListener(
            "input",
            function () {

                const value =
                    Number(
                        previousDefaults.value
                    );

                if (
                    Number.isNaN(value) ||
                    value < 0 ||
                    !Number.isInteger(value)
                ) {

                    setInvalid(
                        previousDefaults,
                        "Enter a valid number of previous defaults."
                    );

                } else {

                    setValid(previousDefaults);

                }

            }
        );

    }


    /* ---------------------------------------------
       Submit
       --------------------------------------------- */

    form.addEventListener(
        "submit",
        function (event) {

            let valid = true;


            if (
                annualIncome &&
                !validatePositiveNumber(
                    annualIncome,
                    "Annual income"
                )
            ) {

                valid = false;

            }


            if (
                loanAmount &&
                !validatePositiveNumber(
                    loanAmount,
                    "Loan amount"
                )
            ) {

                valid = false;

            }


            if (loanTerm) {

                const term =
                    Number(
                        loanTerm.value
                    );

                if (
                    Number.isNaN(term) ||
                    term <= 0 ||
                    term > 480
                ) {

                    setInvalid(
                        loanTerm,
                        "Loan term must be between 1 and 480 months."
                    );

                    valid = false;

                }

            }


            if (
                existingDebt &&
                !validateNonNegativeNumber(
                    existingDebt,
                    "Existing debt"
                )
            ) {

                valid = false;

            }


            if (previousDefaults) {

                const defaults =
                    Number(
                        previousDefaults.value
                    );

                if (
                    Number.isNaN(defaults) ||
                    defaults < 0 ||
                    !Number.isInteger(defaults)
                ) {

                    setInvalid(
                        previousDefaults,
                        "Enter a valid number of previous defaults."
                    );

                    valid = false;

                }

            }


            if (!valid) {

                event.preventDefault();

                const firstInvalid =
                    form.querySelector(
                        ".is-invalid"
                    );

                if (firstInvalid) {
                    firstInvalid.focus();
                }

            }

        }
    );

}


/* =====================================================
   PROFILE VALIDATION
   ===================================================== */

function initializeProfileValidation() {

    const form =
        document.getElementById(
            "profileForm"
        );

    if (!form) {
        return;
    }


    const fullName =
        document.getElementById(
            "full_name"
        );

    const email =
        document.getElementById(
            "email"
        );

    const phone =
        document.getElementById(
            "phone"
        );


    form.addEventListener(
        "submit",
        function (event) {

            let valid = true;


            if (fullName) {

                if (
                    fullName.value.trim().length < 3
                ) {

                    setInvalid(
                        fullName,
                        "Name must contain at least 3 characters."
                    );

                    valid = false;

                }

            }


            if (
                email &&
                !validateEmailField(email)
            ) {

                valid = false;

            }


            if (
                phone &&
                !validatePhoneField(phone)
            ) {

                valid = false;

            }


            if (!valid) {

                event.preventDefault();

                const firstInvalid =
                    form.querySelector(
                        ".is-invalid"
                    );

                if (firstInvalid) {
                    firstInvalid.focus();
                }

            }

        }
    );

}

