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
    # Initialize an empty dictionary for context
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        required_domain = "@cit.edu"
        
        if not email.endswith(required_domain):
            context['email_error'] = f"Please use your educational email ending in {required_domain}."
        elif password != password2:
            context['password2_error'] = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            context['username_error'] = "Username already exists."
        else:
            # If all checks pass, create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            # Since the user is redirected, we can still use the messages framework here
            # or rely on a successful redirect to 'login' which the user can see.
            # We'll stick to redirecting for success.
            return redirect('login')

    # Render the template with the context (which may contain specific error messages)
    return render(request, 'accounts/register.html', context)


@login_required(login_url='login')
def home_view(request):
    return render(request, 'Home/home.html')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})



@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Bind POST data but restrict to specific editable fields
        form = ProfileForm(request.POST, instance=profile)

        # ✅ Only allow these fields to be saved
        allowed_fields = {"contact_number", "program", "year_level"}

        if form.is_valid():
            # Manually update only allowed fields
            for field_name in allowed_fields:
                if field_name in form.cleaned_data:
                    setattr(profile, field_name, form.cleaned_data[field_name])

            profile.save()
            
            return redirect('profile')
        else:
            # Handle common validation issues
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
    users = Profile.objects.select_related('user').all()
    return render(request, 'Home/admin_dashboard.html', {'users': users})