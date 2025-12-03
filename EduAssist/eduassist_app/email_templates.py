import os
from django.conf import settings

def load_template(template_name):
    path = os.path.join(settings.BASE_DIR, "email_templates", f"{template_name}.html")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
