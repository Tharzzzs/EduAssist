document.addEventListener("DOMContentLoaded", function () {

    const newPassword = document.getElementById("id_new_password1");
    const confirmPassword = document.getElementById("id_new_password2");
    const requirementsBox = document.getElementById("requirements");
    const requirementItems = requirementsBox.querySelectorAll("li");
    const matchError = document.getElementById("match-error");
    const submitBtn = document.querySelector('button[type="submit"]');

    /* === SAME RULES AS REGISTER PAGE === */
    const rules = {
        length: /.{8,}/,
    lower: /[a-z]/,
        upper: /[A-Z]/,
        special: /[!@#$%^&*()_+=-]/
    };

    /* === Strength Meter (same scoring logic as register) === */

    function calculateStrength(password) {
        let score = 0;
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/\d/.test(password)) score += 1;
        if (/[!@#$%^&*()_+=-]/.test(password)) score += 2;
        if (/(123|abc|password|qwerty|qwert)/i.test(password)) score -= 2;

        return Math.max(0, Math.min(6, score));
    }

    function updateRequirements(password) {
        requirementItems.forEach(item => {
            const type = item.dataset.check;
            if (rules[type].test(password)) {
                item.classList.remove("invalid");
                item.classList.add("valid");
            } else {
                item.classList.remove("valid");
                item.classList.add("invalid");
            }
        });
    }

    function updateMatch() {
        if (confirmPassword.value.length === 0) {
            matchError.textContent = "";
            return false;
        }
        if (newPassword.value !== confirmPassword.value) {
            matchError.textContent = "Passwords do not match.";
            return false;
        } else {
            matchError.textContent = "";
            return true;
        }
    }

    /* === Determine if Submit is Allowed === */
    function canSubmit() {
        const pw = newPassword.value;

        const mandatoryRulesMet = Object.keys(rules).every(rule => rules[rule].test(pw));
        const matches = pw === confirmPassword.value && pw.length > 0;

        return mandatoryRulesMet && matches;
    }

    function updateSubmitState() {
        submitBtn.disabled = !canSubmit();
    }

    newPassword.addEventListener("focus", function () {
        if (this.value.length > 0) requirementsBox.style.display = "block";
    });

    newPassword.addEventListener("blur", function () {
        requirementsBox.style.display = "none";
    });

    /* === Password Input Events === */
    newPassword.addEventListener("input", function () {
        const pw = this.value;

        if (pw.length > 0) {
            requirementsBox.style.display = "block";
        } else {
            requirementsBox.style.display = "none";
        }

        updateRequirements(pw);
        updateSubmitState();
    });

    /* === Confirm Password Input === */
    confirmPassword.addEventListener("input", function () {
        updateMatch();
        updateSubmitState();
    });

    /* Prevent submission unless valid */
    document.getElementById("password-form").addEventListener("submit", function (e) {
        if (!canSubmit()) {
            e.preventDefault();
            alert("Please fix the password errors before submitting.");
        }
    });

    /* Initialize */
    requirementsBox.style.display = "none";
    updateSubmitState();
});
