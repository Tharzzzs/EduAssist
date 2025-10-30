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
