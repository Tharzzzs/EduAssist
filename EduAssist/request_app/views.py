from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Case, When, Value, IntegerField # <-- ADDED Case, When, Value, IntegerField
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.template.loader import render_to_string

from .models import Request, Category, CategoryChoice, Tag
from .forms import SearchForm, RequestForm
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import RequestSerializer, TagSerializer
from eduassist_app.email_service import send_notification_email

# ------------------------
# Dashboard (Updated for Priority Sorting)
# ------------------------
@login_required(login_url='login')
def dashboard_view(request):
    form = SearchForm(request.GET or None)
    
    # 1. Initialize Base QuerySet based on user role
    if request.user.is_staff:
        # Staff sees all requests
        base_queryset = Request.objects.all()
    else:
        # Standard user sees only their own requests
        base_queryset = Request.objects.filter(user=request.user)
        
    # 2. Dynamic Count Calculation (reflecting the full base_queryset for summary cards)
    total_count = base_queryset.count()
    pending_count = base_queryset.filter(status='pending').count()
    approved_count = base_queryset.filter(status='approved').count()

    # 3. Apply custom ordering (Pending -> Approved -> Cancelled)
    requests = base_queryset.annotate(
        status_order=Case(
            When(status='pending', then=Value(1)),      # Highest Priority
            When(status='approved', then=Value(2)),     # Middle Priority
            When(status='cancelled', then=Value(3)),    # Lowest Priority
            default=Value(4),                           # Catch-all/Other
            output_field=IntegerField()
        )
    ).order_by('status_order', '-date') # Order by status priority, then by date (latest first)

    # 4. Apply search filter if present (filters the list of requests for the table)
    if form.is_valid():
        query = form.cleaned_data.get('search')
        if query:
            # Filters the requests list that gets displayed in the table
            requests = requests.filter(Q(title__icontains=query) | Q(status__icontains=query))

    context = {
        'requests': requests, 
        'form': form,
        'total_count': total_count,# Passed to template
        'pending_count': pending_count, # Passed to template
        'approved_count': approved_count, # Passed to template
    }

    return render(request, 'Home/dashboard.html', context)

# ------------------------
# Request Detail
# ------------------------
@login_required
def request_detail(request, id):
    req = get_object_or_404(Request, id=id)
    categories = Category.objects.all()
    return render(request, 'Home/request_detail.html', {
        'req': req,
        'request_obj': req, # required for modal pre-fill
        'categories': categories
    })

# ------------------------
# Add Request
# ------------------------
@login_required
def add_request(request):
    categories = Category.objects.all()
    category_choices = CategoryChoice.objects.all()

    if request.method == "POST":
        title = request.POST.get('title')
        status = request.POST.get('status', 'pending') 
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        category_choice_id = request.POST.get('category_choice')
        attachment = request.FILES.get('attachment')
        tags_input = request.POST.get('tags')

        category = Category.objects.get(id=category_id) if category_id else None
        category_choice = CategoryChoice.objects.get(id=category_choice_id) if category_choice_id else None

        new_request = Request.objects.create(
            user=request.user,
            title=title,
            status=status, 
            priority=priority,
            description=description,
            category=category,
            category_choice=category_choice,
            attachment=attachment
        )

        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                new_request.tags.add(tag)

        
        return redirect('dashboard')

    return render(request, 'Home/add_request.html', {
        'categories': categories,
        'category_choices': category_choices
    })

# ------------------------
# Edit Request
# ------------------------
@login_required
def edit_request(request, id):
    req = get_object_or_404(Request, id=id)
    
    # CRITICAL CHECK: Block staff from editing requests they did not create.
    if request.user.is_staff and request.user != req.user:
        messages.error(request, "Staff cannot directly edit request details submitted by other users. Use the 'Update Status / Comment' link for administrative actions.")
        return redirect('request_detail', id=req.id)
    
    # Only the creator of the request can proceed
    if not request.user == req.user:
        return HttpResponseForbidden() # Should only happen if the user isn't staff OR the creator

    categories = Category.objects.all()
    category_choices = CategoryChoice.objects.all()
    current_tags_str = ", ".join([t.name for t in req.tags.all()])

    if request.method == 'POST':
        # --- Start POST logic ---
        req.title = request.POST.get('title')
        req.status = request.POST.get('status') 
        req.priority = request.POST.get('priority')
        req.category_id = request.POST.get('category')
        req.category_choice_id = request.POST.get('category_choice')
        req.description = request.POST.get('description')

        if 'attachment' in request.FILES:
            req.attachment = request.FILES['attachment']
        
        # Handle Tags update
        req.tags.clear() 
        tags_input = request.POST.get('tags')
        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                req.tags.add(tag)
        
        req.save()
        # --- End POST logic ---

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, "Request updated successfully.")
        return redirect('request_detail', id=req.id)

    context = {
        'request_obj': req,
        'categories': categories,
        'category_choices': category_choices,
        'current_tags_str': current_tags_str
    }

    # Added necessary JSON response handling for potential AJAX/modal use
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('Home/edit_request.html', context, request=request)
        return JsonResponse({'form_html': html})

    return render(request, 'Home/edit_request.html', context)
# ------------------------
# Delete Request
# ------------------------
@login_required
def delete_request(request, id):
    if request.user.is_staff:
        req = get_object_or_404(Request, id=id)
    else:
        req = get_object_or_404(Request, id=id, user=request.user)

    if request.method == 'POST':
        req.delete()
        
        return redirect('dashboard')

    return render(request, 'Home/confirm_delete.html', {'req': req})

# ------------------------
# Landing Page
# ------------------------
def landing_page(request):
    return render(request, 'Home/landing.html')

# ------------------------
# Class-Based Views (Updated for Priority Sorting)
# ------------------------
class RequestListView(LoginRequiredMixin, ListView):
    model = Request
    template_name = 'request/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        queryset = Request.objects.prefetch_related('tags').all()
        category_value = self.request.GET.get('category')
        tag_slug = self.request.GET.get('tag')
        status = self.request.GET.get('status')
        search = self.request.GET.get('q')

        if category_value:
            queryset = queryset.filter(category_id=category_value)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            
        # Apply Custom Priority Sorting: Pending (1) -> Approved (2) -> Cancelled (3)
        queryset = queryset.annotate(
            status_order=Case(
                When(status='pending', then=Value(1)),
                When(status='approved', then=Value(2)),
                When(status='cancelled', then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        ).order_by('status_order', '-date') # Order by priority, then by latest date

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.annotate(request_count=Count('requests')).filter(request_count__gt=0).order_by('name')
        context['current_category'] = self.request.GET.get('category')
        context['current_tag'] = self.request.GET.get('tag')
        context['current_status'] = self.request.GET.get('status')
        context['current_search'] = self.request.GET.get('q')
        return context

# Only admin/staff can create categories
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def create_category(request):
    if request.method == "POST":
        if 'category_name' in request.POST:
            name = request.POST.get('category_name')
            if name:
                Category.objects.get_or_create(name=name)

        elif 'query_name' in request.POST:
            query_name = request.POST.get('query_name')
            category_id = request.POST.get('category_for_query')
            if query_name and category_id:
                category = Category.objects.get(id=category_id)
                CategoryChoice.objects.get_or_create(value=query_name, category=category)

        return redirect('create_category')

    categories = Category.objects.all()
    choices = CategoryChoice.objects.all()
    return render(request, "Home/create_category.html", {"categories": categories, "choices": choices})

# ------------------------
# Approve/Update Request Status (Admin Action)
# ------------------------
@login_required
# @user_passes_test(lambda u: u.is_staff) # Note: Admin check should be implemented here, but is commented out in original snippet
def approve_request(request, id):
    req = get_object_or_404(Request, id=id)

    if request.method == "POST":
        
        # 1. Grab new status and admin message from the POST data
        new_status = request.POST.get('new_status', req.status) # Grab new status, default to current status
        admin_message = request.POST.get("admin_message", "")
        
        # 2. Update Request Status
        is_status_changed = (req.status != new_status)
        req.status = new_status
        req.save()

        # 3. Handle Notification (Only send email if status actually changed)
        if is_status_changed:
            # Assuming 'pending', 'approved', 'rejected', etc. match email templates
            # Note: The original example only handled 'approved' in this block.
            # I will use the new status for dynamic email type if templates exist.
            email_type = f"request_{new_status}" 

            send_notification_email(
                to_email=req.user.email,
                type=email_type,
                template_name=email_type,
                context_data={
                    "name": req.user.first_name,
                    "title": req.title,
                    "admin_message": admin_message,
                    "new_status": req.get_status_display()
                }
            )
        
        # 4. Success message and redirect
        messages.success(request, f"Request status changed to '{req.get_status_display()}' and user notified.")
        
        return redirect('request_detail', id=id)

    # GET Request: Renders the Admin Status/Comment Form
    return render(request, 'Home/approve_request.html', {
        'req': req,
        'current_status': req.status,
        # Pass all possible status choices (assuming STATUS_CHOICES is defined in Request model)
        # You will need to ensure Request.STATUS_CHOICES is correctly imported/available.
        'status_choices': Request.STATUS_CHOICES 
    })