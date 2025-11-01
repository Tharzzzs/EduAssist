from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from .models import Request
from django.http import HttpResponseForbidden
from .forms import SearchForm
from datetime import datetime

@login_required(login_url='login')
def dashboard_view(request):
    form = SearchForm(request.GET or None)
    
    # Staff sees all requests, regular users see their own
    if request.user.is_staff:
        requests = Request.objects.all()
    else:
        requests = Request.objects.filter(user=request.user)
    
    # Apply search if form is valid and search exists
    if form.is_valid():
        query = form.cleaned_data.get('search')
        if query:
            requests = requests.filter(
                Q(title__icontains=query) | Q(status__icontains=query)
            )

    return render(request, 'Home/dashboard.html', {'requests': requests, 'form': form})


@login_required(login_url='login')
def request_detail(request, id):
    req = get_object_or_404(Request, id=id)
    if not (request.user == req.user or request.user.is_staff):
        return HttpResponseForbidden("You do not have permission to view this request.")
    return render(request, 'Home/request_detail.html', {'req': req})


@login_required(login_url='login')
def edit_request(request, id):
    req = get_object_or_404(Request, id=id)
    if not (request.user == req.user or request.user.is_staff):
        return HttpResponseForbidden("You do not have permission to edit this request.")

    if request.method == 'POST':
        title = request.POST.get('title')
        status = request.POST.get('status')
        date = request.POST.get('date')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        if not title or not status or not date:
            messages.error(request, "Please complete all required fields.")
            return redirect('edit_request', id=req.id)

        # Validation
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png',
                         'application/msword',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        max_size_mb = 5

        if attachment:
            if attachment.content_type not in allowed_types:
                messages.error(request, "File type not allowed. Please upload PDF, DOC, or image files.")
                return redirect('edit_request', id=req.id)
            if attachment.size > max_size_mb * 1024 * 1024:
                messages.error(request, "File exceeds 5MB size limit.")
                return redirect('edit_request', id=req.id)
            req.attachment = attachment  

        # Save changes
        try:
            req.title = title
            req.status = status
            req.description = description
            req.save()
            messages.success(request, "Request updated successfully!")
            return redirect('request_detail', id=req.id)
        
        except Exception as e:
            messages.error(request, "Failed to update the request. Please try again. ({e})")

        try:
            req.date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            

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
        attachment = request.FILES.get('attachment')

        if not title or not status or not date or not description:
            messages.error(request, "Please complete all required fields.")
            return redirect('add_request')
        
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png',
                         'application/msword',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        max_size_mb = 5

        if attachment:
            if attachment.content_type not in allowed_types:
                messages.error(request, "File type not allowed. Please upload PDF, DOC, or image files.")
                return redirect('add_request')
            if attachment.size > max_size_mb * 1024 * 1024:
                messages.error(request, "File exceeds 5MB size limit.")
                return redirect('add_request')

        try:
            # Check for duplicates
            if Request.objects.filter(user=request.user, title=title, date=date).exists():
                messages.warning(request, "This request has already been submitted.")
                return redirect('add_request')

            # Save to DB
            new_request = Request.objects.create(
                user=request.user,
                title=title,    
                status=status,
                date=date,
                description=description,
                attachment=attachment,
            )

            messages.success(request, f"Request submitted successfully! Reference ID: {new_request.id}")
            return redirect('dashboard')

        except Exception:
            messages.error(request, "Submission failed, please try again later.")

    return render(request, 'Home/add_request.html')


def landing_page(request):
    return render(request, 'Home/landing.html')
