# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from .models import Request, Profile
from .forms import ProfileForm, SearchForm
from django.http import HttpResponseForbidden


def login_view(request):
    
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')



def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('landing')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful. You can log in now.")
            return redirect('login')

    return render(request, 'accounts/register.html')


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


@login_required(login_url='login')
def dashboard_view(request):
    form = SearchForm(request.GET)
    if request.user.is_staff:
        requests = Request.objects.all()  # Admin sees all requests
    else:
        requests = Request.objects.filter(user=request.user)  # Regular user sees only their requests

    if form.is_valid() and form.cleaned_data['search']:
        query = form.cleaned_data['search']
        requests = requests.filter(
            Q(title__icontains=query) | Q(status__icontains=query)
        )

    return render(request, 'Home/dashboard.html', {'requests': requests, 'form': form})


@login_required(login_url='login')
def request_detail(request, id):

    req = get_object_or_404(Request, id=id)
    # Only allow the owner or admin to view
    if not (request.user == req.user or request.user.is_staff):
        return HttpResponseForbidden("You do not have permission to view this request.")
    return render(request, 'Home/request_detail.html', {'req': req})


@login_required(login_url='login')
def edit_request(request, id):
    req = get_object_or_404(Request, id=id)

    if not (request.user == req.user or request.user.is_staff):
        return HttpResponseForbidden("You do not have permission to edit this request.")

    if request.method == 'POST':
        req.title = request.POST.get('title')
        req.status = request.POST.get('status')
        req.date = request.POST.get('date')
        req.description = request.POST.get('description')
        req.save()
        return redirect('request_detail', id=req.id)

    return render(request, 'Home/edit_request.html', {'request_obj': req})


@login_required(login_url='login')
def delete_request(request, id):
    if request.user.is_staff or request.user.is_superuser:
        req = get_object_or_404(Request, id=id)
    else:
        req = get_object_or_404(Request, id=id, user=request.user)

    if request.method == 'POST':
        req.delete()
        return redirect('dashboard')

    return render(request, 'Home/confirm_delete.html', {'req': req})

@login_required(login_url='login')
def add_request(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        status = request.POST.get('status')
        date = request.POST.get('date')
        description = request.POST.get('description')

        Request.objects.create(
            user=request.user,
            title=title,
            status=status,
            date=date,
            description=description
        )
        return redirect('dashboard')

    return render(request, 'Home/add_request.html')


def landing_page(request):
    return render(request, 'Home/landing.html')

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