# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from .models import Profile
from .forms import ProfileForm, SearchForm
from django.http import HttpResponseForbidden
from feedback.models import Feedback
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def login_view(request):
    # Initialize an empty dictionary for context
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Assuming 'dashboard' is a defined URL name for your next page
            return redirect('dashboard') 
        else:
            # FIX: Use 'login_error' to match the variable name used in the HTML template.
            context['login_error'] = 'Invalid username or password.'

    # NOTE: The template expects 'login_error' to render the message.
    # The template path is assumed to be 'accounts/login.html' based on the view.
    return render(request, 'accounts/login.html', context)



def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('landing')


def register_view(request):
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        required_domain = "@cit.edu"
        
        # Combined regex pattern for mandatory complexity requirements
        complexity_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+=-]).{8,}$')

        # --- VALIDATION CHAIN ---
        if not re.match(r'^[a-zA-Z\s]+$', username):
            context['username_error'] = "Full Name can only contain letters and spaces."
        
        elif not email.endswith(required_domain):
            context['email_error'] = f"Please use your educational email ending in {required_domain}."
            
        elif password != password2:
            context['password2_error'] = "Passwords do not match."
            
        # --- NEW PASSWORD VALIDATION INTEGRATION ---
        elif not complexity_pattern.match(password):
            context['password_error'] = "Password must be at least 8 characters and include an uppercase letter, a lowercase letter, and a special character (!@#$%^&*()_+=-)."
            
        else:
            try:
                # 1. Run all password validators from settings.py
                # We create a temporary user object because some validators check user attributes (like username similarity)
                validate_password(password, user=User(username=username))
                
                # 2. If validation passes, check if username exists
                if User.objects.filter(username=username).exists():
                    context['username_error'] = "Username already exists."
                else:
                    # If all checks pass, create the user
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    return redirect('login')
                    
            except ValidationError as e:
                # Catch errors from the common password check and other validators
                context['password_error'] = e.messages[0]
        # --- END NEW PASSWORD VALIDATION INTEGRATION ---

    return render(request, 'accounts/register.html', context)

@login_required(login_url='login')
def home_view(request):
    return render(request, 'Home/home.html')


@login_required(login_url='login')
def change_password(request):
    next_page = request.GET.get("next", "profile")

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            if next_page == "settings":
                return redirect('settings')
            else:
                return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form, 'next': next_page,})



@login_required
def profile(request):
    # Define a default role for new profiles (e.g., 'STUDENT' or 'DEFAULT')
    DEFAULT_ROLE = 'STUDENT' 

    # FIX: Use 'defaults' to provide a non-null value for the 'role' field 
    # when the profile object has to be created.
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'role': DEFAULT_ROLE} # <--- THIS is the necessary change
    )

    if request.method == 'POST':
        # ... (rest of your POST logic)
        form = ProfileForm(request.POST, instance=profile)

        allowed_fields = {"contact_number", "program", "year_level"}

        if form.is_valid():
            for field_name in allowed_fields:
                if field_name in form.cleaned_data:
                    setattr(profile, field_name, form.cleaned_data[field_name])
            
            # Note: Assuming year_level is a CharField based on your previous code ('1' to '5'). 
            # If it's an IntegerField, you should cast profile.year_level to int for comparison.
            if profile.year_level < '1' or profile.year_level > '5':
                messages.error(request, "Year level must be between 1 and 5.")
                return redirect('profile')
            else:
                profile.save()
                return redirect('profile')
        else:
            contact = request.POST.get('contact_number', '').strip()
            if not contact:
                messages.error(request, "Contact field cannot be empty.")
            elif not contact.isdigit() or len(contact) < 10:
                messages.error(request, "Incorrect format of contact number.")
            else:
                messages.error(request, "Profile update failed, please try again later.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'Home/profile.html', {
        'form': form,
        'user_info': request.user,
    })



@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    # Only SUPERADMIN or ADMIN may view dashboard
    if profile.role not in ["SUPERADMIN", "ADMIN"]:
        return HttpResponseForbidden("Unauthorized access")

    users = Profile.objects.select_related('user').all()
    return render(request, 'Home/admin_dashboard.html', {'users': users})


@login_required
def change_role_view(request, user_id):

    current = Profile.objects.get(user=request.user)

    if current.role != "SUPERADMIN":
        return HttpResponseForbidden("Only Superadmins can change roles.")

    target = get_object_or_404(Profile, id=user_id)
    target_user = target.user

    if request.method == "POST":
        new_role = request.POST.get("role")
        target.role = new_role
        target.save()

        # IMPORTANT: Match Django permissions
        if new_role in ["ADMIN", "SUPERADMIN"]:
            target_user.is_staff = True
        else:
            target_user.is_staff = False
        
        target_user.save()

        messages.success(request, "Role updated successfully.")
        return redirect("admin_dashboard")

    return redirect("admin_dashboard")
