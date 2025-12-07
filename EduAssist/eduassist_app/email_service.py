import re
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from supabase import create_client
from .email_templates import load_template

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def log_email(to_email, type, status, message=""):
    supabase.table("email_logs").insert({
        "to_email": to_email,
        "type": type,
        "status": status,
        "message": message
    }).execute()

def send_notification_email(subject, to_email, template_name, context_data):
    # 1. Validate email
    if not is_valid_email(to_email):
        log_email(to_email, template_name, "Failed - Invalid Email")
        return False

    # 2. Load template
    template_html = load_template(template_name)
    if template_html is None:
        log_email(to_email, template_name, "Failed - Template Missing")
        return False

    # 3. Render template
    try:
        template = Template(template_html)
        rendered_html = template.render(Context(context_data))
    except Exception as e:
        log_email(to_email, template_name, "Failed - Template Render Error", str(e))
        return False

    # 4. Send email
    try:
        email = EmailMultiAlternatives(
            subject,
            "",  # plain text
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        email.attach_alternative(rendered_html, "text/html")
        email.send()

        log_email(to_email, template_name, "Sent")
        return True

    except Exception as e:
        log_email(to_email, template_name, "Failed - Service Error", str(e))
        return False
