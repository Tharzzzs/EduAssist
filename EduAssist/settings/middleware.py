# EduAssist/settings/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import UserSettings

class ThemeMiddleware(MiddlewareMixin):
    """
    Set a cookie 'dark_mode'='1' or '0' on every response for authenticated users.
    This avoids relying on template context and works for all response types.
    """

    def process_response(self, request, response):
        try:
            user = getattr(request, "user", None)
            if user and user.is_authenticated and not isinstance(user, AnonymousUser):
                settings = UserSettings.objects.filter(user=user).first()
                dark = settings.dark_mode if settings else False
                # cookie value as string '1' or '0'
                response.set_cookie("dark_mode", "1" if dark else "0", max_age=30*24*3600, path="/")
            else:
                # For anonymous users, ensure cookie is removed or set to 0
                response.set_cookie("dark_mode", "0", max_age=30*24*3600, path="/")
        except Exception:
            # don't break responses if something goes wrong
            pass
        return response
