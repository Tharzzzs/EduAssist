# Place this in pos_app/utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_notification_email(subject, to_email, template_name, context_data):
    """
    Renders an email template and sends it to the specified recipient.
    
    Args:
        subject (str): The subject line of the email.
        to_email (str): The recipient's email address.
        template_name (str): The name of the HTML template file (e.g., 'request_approved.html').
        context_data (dict): Data to be passed to the template for rendering.
    """
    
    # 1. Render the HTML content using the provided template and context
    html_content = render_to_string(template_name, context_data)
    
    # 2. Create the plain text version of the email for older clients (good practice)
    text_content = strip_tags(html_content)
    
    # 3. Create the EmailMultiAlternatives object
    email = EmailMultiAlternatives(
        subject,
        text_content, # The plain text version
        settings.DEFAULT_FROM_EMAIL, # Sender's email address (defined in settings)
        [to_email] # Recipient list
    )
    
    # 4. Attach the HTML version
    email.attach_alternative(html_content, "text/html")
    
    # 5. Send the email
    email.send()