from .models import UserSettings

def theme_settings(request):
    if request.user.is_authenticated:
        settings = UserSettings.objects.filter(user=request.user).first()
        return {"global_dark_mode": settings.dark_mode if settings else False}
    return {"global_dark_mode": False}
