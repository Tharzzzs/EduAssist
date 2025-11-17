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
from .forms import SearchForm, RequestForm # Import RequestForm
from datetime import datetime
# request/views.py - Add these imports at the top
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Request, Category, Tag
from .serializers import RequestSerializer, CategorySerializer, TagSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json

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
            messages.error(request, f"Failed to update the request. Please try again. ({e})")

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


# Add these class-based views after your existing function-based views
class RequestListView(LoginRequiredMixin, ListView):
    model = Request
    template_name = 'request/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        queryset = Request.objects.select_related('user', 'category').prefetch_related('tags').all()
        
        # Add your existing filtering logic here
        category_slug = self.request.GET.get('category')
        tag_slug = self.request.GET.get('tag')
        status = self.request.GET.get('status')
        search = self.request.GET.get('q')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.distinct().order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(request_count=Count('requests')).filter(request_count__gt=0)
        context['tags'] = Tag.objects.annotate(request_count=Count('requests')).filter(request_count__gt=0).order_by('name')
        context['current_category'] = self.request.GET.get('category')
        context['current_tag'] = self.request.GET.get('tag')
        context['current_status'] = self.request.GET.get('status')
        context['current_search'] = self.request.GET.get('q')
        return context


# New CBVs for Categories and Tags
class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'request/category_list.html'
    context_object_name = 'categories'

    def test_func(self):
        return self.request.user.is_staff # Only staff can manage categories

class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'request/tag_list.html'
    context_object_name = 'tags'


# New CBVs for Request CRUD
class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    form_class = RequestForm
    template_name = 'request/request_form.html'
    success_url = reverse_lazy('request-list')

    def form_valid(self, form):
        # Set the user to the logged-in user before saving
        form.instance.user = self.request.user
        messages.success(self.request, "Request submitted successfully!")
        return super().form_valid(form)

class RequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Request
    template_name = 'request/request_detail.html'
    context_object_name = 'request_obj'

    def test_func(self):
        # Users can see their own requests, staff can see all
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff

class RequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Request
    form_class = RequestForm
    template_name = 'request/request_form.html'
    context_object_name = 'request_obj'
    
    def get_success_url(self):
        messages.success(self.request, "Request updated successfully!")
        return reverse_lazy('request-detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Users can edit their own requests, staff can edit all
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff


class RequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Request
    template_name = 'request/request_confirm_delete.html'
    success_url = reverse_lazy('request-list')
    context_object_name = 'request_obj'

    def test_func(self):
        # Users can delete their own requests, staff can delete all
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff


# Add these API views at the bottom of the file
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def autosuggest(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        # Case-insensitive partial match
        tags = Tag.objects.filter(name__icontains=query).distinct()[:10]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)

class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Request.objects.select_related('user', 'category').prefetch_related('tags')
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)