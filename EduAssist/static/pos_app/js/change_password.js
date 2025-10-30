document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("password-form");
  const newPassword = document.getElementById("id_new_password1");
  const confirmPassword = document.getElementById("id_new_password2");
  const requirements = document.querySelectorAll("#requirements li");
  const matchError = document.getElementById("match-error");
  const submitBtn = form.querySelector('button[type="submit"]');


  const checks = {
    length: (pw) => pw.length >= 8,
    lower: (pw) => /[a-z]/.test(pw),
    upper: (pw) => /[A-Z]/.test(pw),
    special: (pw) => /[!@#$%^&*(),.?":{}|<>]/.test(pw),
  };

  function updateRequirements(pw) {
    requirements.forEach((req) => {
      const checkType = req.dataset.check;
      if (checks[checkType](pw)) {
        req.classList.remove("invalid");
        req.classList.add("valid");
        req.style.display = "none"; 
      } else {
        req.classList.remove("valid");
        req.classList.add("invalid");
        req.style.display = "block"; 
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

  function canSubmit() {
    const pw = newPassword.value;
    const allValid = Object.keys(checks).every((key) => checks[key](pw));
    const match = pw === confirmPassword.value && pw.length > 0;
    return allValid && match;
  }

  function updateSubmitState() {
    submitBtn.disabled = !canSubmit();
  }

  newPassword.addEventListener("input", () => {
    updateRequirements(newPassword.value);
    updateSubmitState();
  });

  confirmPassword.addEventListener("input", () => {
    updateMatch();
    updateSubmitState();
  });

  form.addEventListener("submit", function (event) {
    if (!canSubmit()) {
      event.preventDefault();
      alert("Please fix the errors before submitting.");
    }
  });

  updateRequirements("");
  updateSubmitState();
});

temp

