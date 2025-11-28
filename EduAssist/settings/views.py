from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserSettings

@login_required
def settings_view(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        errors = []

        # --- THEME VALIDATION ---
        theme = request.POST.get("theme")
        if theme not in ["light", "dark"]:
            errors.append("Selected theme is not available.")

        # --- EMAIL + NOTIFICATION VALIDATION ---
        email = request.POST.get("notification_email", "").strip()
        receive_email = request.POST.get("receive_email") == "on"

        if receive_email:
            if email == "":
                errors.append("Please enter an email address.")
            else:
                try:
                    validate_email(email)
                except ValidationError:
                    errors.append("Invalid email address.")

        # If there are errors → show messages and stop saving
        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect("settings")

        # --- SAVE VALID SETTINGS TO DATABASE ---
        settings.dark_mode = (theme == "dark")
        settings.notification_email = email
        settings.receive_email = receive_email
        settings.profile_visible = request.POST.get("profile_visible") == "on"
        settings.allow_data_sharing = request.POST.get("allow_data_sharing") == "on"

        try:
            settings.save()
            messages.success(request, "Settings updated successfully.")
        except:
            messages.error(request, "Unable to save settings, please try again later.")

        return redirect("settings")

    return render(request, "settings/settings.html", {
    "settings": settings,
    "user": request.user
})

