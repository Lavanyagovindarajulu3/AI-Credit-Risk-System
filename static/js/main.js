```javascript
/*
=========================================================
AI-POWERED CREDIT RISK ASSESSMENT SYSTEM
Main JavaScript
=========================================================
*/


"use strict";


/* =====================================================
   DOCUMENT READY
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    initializePasswordToggle();

    initializeFormValidation();

    initializeAutoDismissAlerts();

    initializeLoadingButtons();

    initializeTooltips();

    initializeConfirmActions();

    initializeNumberFormatting();

});


/* =====================================================
   PASSWORD VISIBILITY TOGGLE
   ===================================================== */

function initializePasswordToggle() {

    const toggleButtons =
        document.querySelectorAll(".toggle-password");

    toggleButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId =
                button.getAttribute("data-target");

            if (!targetId) {
                return;
            }

            const passwordInput =
                document.getElementById(targetId);

            if (!passwordInput) {
                return;
            }

            const icon =
                button.querySelector("i");

            if (passwordInput.type === "password") {

                passwordInput.type = "text";

                if (icon) {
                    icon.classList.remove("bi-eye");
                    icon.classList.add("bi-eye-slash");
                }

            } else {

                passwordInput.type = "password";

                if (icon) {
                    icon.classList.remove("bi-eye-slash");
                    icon.classList.add("bi-eye");
                }

            }

        });

    });

}


/* =====================================================
   FORM VALIDATION
   ===================================================== */

function initializeFormValidation() {

    const forms =
        document.querySelectorAll(".needs-validation");

    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                if (!form.checkValidity()) {

                    event.preventDefault();
                    event.stopPropagation();

                }

                form.classList.add("was-validated");

            },
            false
        );

    });

}


/* =====================================================
   AUTO DISMISS BOOTSTRAP ALERTS
   ===================================================== */

function initializeAutoDismissAlerts() {

    const alerts =
        document.querySelectorAll(
            ".alert[data-auto-dismiss]"
        );

    alerts.forEach(function (alert) {

        const duration =
            parseInt(
                alert.getAttribute("data-auto-dismiss"),
                10
            ) || 5000;

        setTimeout(function () {

            if (typeof bootstrap !== "undefined") {

                const alertInstance =
                    bootstrap.Alert.getOrCreateInstance(alert);

                alertInstance.close();

            } else {

                alert.remove();

            }

        }, duration);

    });

}


/* =====================================================
   LOADING BUTTONS
   ===================================================== */

function initializeLoadingButtons() {

    const forms =
        document.querySelectorAll(
            "form[data-loading]"
        );

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            if (!button) {
                return;
            }

            const originalHTML =
                button.innerHTML;

            button.dataset.originalText =
                originalHTML;

            button.disabled = true;

            button.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true">
                </span>
                Processing...
            `;

        });

    });

}


/* =====================================================
   BOOTSTRAP TOOLTIPS
   ===================================================== */

function initializeTooltips() {

    if (typeof bootstrap === "undefined") {
        return;
    }

    const tooltipElements =
        document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        );

    tooltipElements.forEach(function (element) {

        new bootstrap.Tooltip(element);

    });

}


/* =====================================================
   CONFIRM ACTIONS
   ===================================================== */

function initializeConfirmActions() {

    const confirmElements =
        document.querySelectorAll(
            "[data-confirm]"
        );

    confirmElements.forEach(function (element) {

        element.addEventListener(
            "click",
            function (event) {

                const message =
                    element.getAttribute("data-confirm");

                if (
                    message &&
                    !window.confirm(message)
                ) {

                    event.preventDefault();

                }

            }
        );

    });

}


/* =====================================================
   NUMBER FORMATTING
   ===================================================== */

function initializeNumberFormatting() {

    const numberInputs =
        document.querySelectorAll(
            "input[data-number-format]"
        );

    numberInputs.forEach(function (input) {

        input.addEventListener(
            "input",
            function () {

                let value =
                    input.value.replace(
                        /[^0-9.]/g,
                        ""
                    );

                const parts =
                    value.split(".");

                if (parts.length > 2) {

                    value =
                        parts[0] +
                        "." +
                        parts.slice(1).join("");

                }

                input.value = value;

            }
        );

    });

}


/* =====================================================
   PASSWORD STRENGTH
   ===================================================== */

function checkPasswordStrength(password) {

    let score = 0;

    if (!password) {
        return score;
    }

    if (password.length >= 8) {
        score++;
    }

    if (/[A-Z]/.test(password)) {
        score++;
    }

    if (/[a-z]/.test(password)) {
        score++;
    }

    if (/[0-9]/.test(password)) {
        score++;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
        score++;
    }

    return score;

}


/* =====================================================
   PASSWORD STRENGTH INDICATOR
   ===================================================== */

function initializePasswordStrength() {

    const passwordInput =
        document.getElementById("password");

    const strengthBar =
        document.getElementById("passwordStrength");

    const strengthText =
        document.getElementById("passwordStrengthText");

    if (!passwordInput) {
        return;
    }

    passwordInput.addEventListener(
        "input",
        function () {

            const score =
                checkPasswordStrength(
                    passwordInput.value
                );

            if (strengthBar) {

                strengthBar.style.width =
                    `${(score / 5) * 100}%`;

            }

            if (!strengthText) {
                return;
            }

            if (score <= 1) {

                strengthText.textContent =
                    "Very Weak";

            } else if (score === 2) {

                strengthText.textContent =
                    "Weak";

            } else if (score === 3) {

                strengthText.textContent =
                    "Medium";

            } else if (score === 4) {

                strengthText.textContent =
                    "Strong";

            } else {

                strengthText.textContent =
                    "Very Strong";

            }

        }
    );

}


/* =====================================================
   CONFIRM PASSWORD
   ===================================================== */

function initializePasswordConfirmation() {

    const password =
        document.getElementById("password");

    const confirmPassword =
        document.getElementById("confirm_password");

    if (!password || !confirmPassword) {
        return;
    }

    confirmPassword.addEventListener(
        "input",
        function () {

            if (
                confirmPassword.value &&
                confirmPassword.value !== password.value
            ) {

                confirmPassword.setCustomValidity(
                    "Passwords do not match."
                );

            } else {

                confirmPassword.setCustomValidity("");

            }

        }
    );

}


/* =====================================================
   CREDIT SCORE COLOR
   ===================================================== */

function getCreditScoreCategory(score) {

    score = Number(score);

    if (Number.isNaN(score)) {
        return "unknown";
    }

    if (score >= 750) {
        return "excellent";
    }

    if (score >= 650) {
        return "good";
    }

    if (score >= 550) {
        return "fair";
    }

    return "poor";

}


/* =====================================================
   LOAN AMOUNT VALIDATION
   ===================================================== */

function validateLoanAmount(input) {

    if (!input) {
        return false;
    }

    const value =
        Number(input.value);

    if (
        Number.isNaN(value) ||
        value <= 0
    ) {

        input.setCustomValidity(
            "Enter a valid loan amount."
        );

        return false;

    }

    input.setCustomValidity("");

    return true;

}


/* =====================================================
   EMAIL VALIDATION
   ===================================================== */

function isValidEmail(email) {

    const pattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return pattern.test(
        String(email).toLowerCase()
    );

}


/* =====================================================
   PHONE VALIDATION
   ===================================================== */

function isValidPhone(phone) {

    const cleaned =
        String(phone)
            .replace(/\s+/g, "")
            .replace(/[-()]/g, "");

    return /^\+?[0-9]{10,15}$/.test(
        cleaned
    );

}


/* =====================================================
   SHOW TOAST
   ===================================================== */

function showToast(
    message,
    type = "info"
) {

    const container =
        document.getElementById(
            "toastContainer"
        );

    if (!container) {
        return;
    }

    const toast =
        document.createElement("div");

    toast.className =
        `toast align-items-center text-bg-${type} border-0`;

    toast.setAttribute(
        "role",
        "alert"
    );

    toast.setAttribute(
        "aria-live",
        "assertive"
    );

    toast.setAttribute(
        "aria-atomic",
        "true"
    );

    toast.innerHTML = `

        <div class="d-flex">

            <div class="toast-body">

                ${escapeHTML(message)}

            </div>

            <button
                type="button"
                class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast">
            </button>

        </div>

    `;

    container.appendChild(toast);

    if (typeof bootstrap !== "undefined") {

        const bootstrapToast =
            new bootstrap.Toast(toast, {
                delay: 4000
            });

        bootstrapToast.show();

    }

    toast.addEventListener(
        "hidden.bs.toast",
        function () {

            toast.remove();

        }
    );

}


/* =====================================================
   ESCAPE HTML
   ===================================================== */

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value);

    return div.innerHTML;

}


/* =====================================================
   LOADING OVERLAY
   ===================================================== */

function showLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.classList.add("active");

    }

}


function hideLoading() {

    const overlay =
        document.getElementById(
            "loadingOverlay"
        );

    if (overlay) {

        overlay.classList.remove("active");

    }

}


/* =====================================================
   SCROLL TO ELEMENT
   ===================================================== */

function scrollToElement(
    elementId
) {

    const element =
        document.getElementById(
            elementId
        );

    if (!element) {
        return;
    }

    element.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =====================================================
   DEBOUNCE
   ===================================================== */

function debounce(
    callback,
    delay = 300
) {

    let timeout;

    return function (...args) {

        clearTimeout(timeout);

        timeout =
            setTimeout(
                () => callback.apply(this, args),
                delay
            );

    };

}


/* =====================================================
   INITIALIZE EXTRA FUNCTIONS
   ===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializePasswordStrength();

        initializePasswordConfirmation();

    }
);
```
