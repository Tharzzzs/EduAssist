from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Request, Tag
from .forms import SearchForm, RequestForm
from .serializers import RequestSerializer, TagSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import re

# ------------------------
# Static Categories
# ------------------------
CATEGORY_CHOICES = [
    ('Academic', 'Academic'),
    ('Course Material', 'Course Material'),
    ('Grades', 'Grades'),
    ('Assignments', 'Assignments'),
    ('Exam Schedule', 'Exam Schedule'),
    ('Finance', 'Finance'),
    ('Tuition Fee', 'Tuition Fee'),
    ('Scholarship', 'Scholarship'),
    ('Refund', 'Refund'),
    ('Technical', 'Technical'),
    ('Login Issue', 'Login Issue'),
    ('Software Installation', 'Software Installation'),
    ('Wi-Fi / Network Issue', 'Wi-Fi / Network Issue'),
    ('Administrative', 'Administrative'),
    ('ID Card', 'ID Card'),
    ('Room Allocation', 'Room Allocation'),
    ('Library Access', 'Library Access'),
]

# ------------------------
# Function-Based Views
# ------------------------

@login_required(login_url='login')
def dashboard_view(request):
    form = SearchForm(request.GET or None)
    if request.user.is_staff:
        requests = Request.objects.all()
    else:
        requests = Request.objects.filter(user=request.user)

    if form.is_valid():
        query = form.cleaned_data.get('search')
        if query:
            requests = requests.filter(Q(title__icontains=query) | Q(status__icontains=query))

    return render(request, 'Home/dashboard.html', {'requests': requests, 'form': form})


@login_required(login_url='login')
def request_detail(request, id):
    req = get_object_or_404(Request, id=id)
    return render(request, 'Home/request_detail.html', {'req': req})


@login_required
def edit_request(request, id):
    req = get_object_or_404(Request, id=id)
    if not (request.user == req.user or request.user.is_staff):
        return HttpResponseForbidden()

    categories = [{'value': c[0], 'label': c[1]} for c in CATEGORY_CHOICES]
    current_tags_str = ", ".join([t.name for t in req.tags.all()])

    if request.method == 'POST':
        req.title = request.POST.get('title')
        req.status = request.POST.get('status')
        req.priority = request.POST.get('priority')
        req.description = request.POST.get('description')
        req.category = request.POST.get('category')  # string assignment works now

        attachment = request.FILES.get('attachment')
        if attachment:
            req.attachment = attachment

        req.tags.clear()
        tags_str = request.POST.get('tags', '')
        tag_names = [name.strip().lower() for name in tags_str.split(',') if name.strip()]
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            req.tags.add(tag)

        req.save()
        return redirect('request_detail', id=req.id)

    return render(request, 'Home/edit_request.html', {
        'request_obj': req,
        'categories': categories,
        'current_tags_str': current_tags_str
    })



@login_required(login_url='login')
def delete_request(request, id):
    if request.user.is_staff:
        req = get_object_or_404(Request, id=id)
    else:
        req = get_object_or_404(Request, id=id, user=request.user)

    if request.method == 'POST':
        req.delete()
        return redirect('dashboard')

    return render(request, 'Home/confirm_delete.html', {'req': req})


@login_required
def add_request(request):
    categories = [{'value': c[0], 'label': c[1]} for c in CATEGORY_CHOICES]

    if request.method == "POST":
        title = request.POST.get('title')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        category_value = request.POST.get('category')  # string matches your choices
        attachment = request.FILES.get('attachment')
        tags_input = request.POST.get('tags')

        new_request = Request.objects.create(
            user=request.user,
            title=title,
            status=status,
            priority=priority,
            description=description,
            category=category_value,
            attachment=attachment
        )

        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',')]
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                new_request.tags.add(tag)

        messages.success(request, "Request submitted successfully!")
        return redirect('dashboard')

    return render(request, 'Home/add_request.html', {'categories': categories})


def landing_page(request):
    return render(request, 'Home/landing.html')


# ------------------------
# Class-Based Views
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
            queryset = queryset.filter(category=category_value)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.distinct().order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [{'value': c[0], 'label': c[1]} for c in CATEGORY_CHOICES]
        context['tags'] = Tag.objects.annotate(request_count=Count('requests')).filter(request_count__gt=0).order_by('name')
        context['current_category'] = self.request.GET.get('category')
        context['current_tag'] = self.request.GET.get('tag')
        context['current_status'] = self.request.GET.get('status')
        context['current_search'] = self.request.GET.get('q')
        return context


class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'request/category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [{'value': c[0], 'label': c[1]} for c in CATEGORY_CHOICES]
        return context

    def test_func(self):
        return self.request.user.is_staff


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'request/tag_list.html'
    context_object_name = 'tags'


class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    form_class = RequestForm
    template_name = 'request/request_form.html'
    success_url = reverse_lazy('request-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Request submitted successfully!")
        return super().form_valid(form)


class RequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Request
    template_name = 'request/request_detail.html'
    context_object_name = 'request_obj'

    def test_func(self):
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
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff


class RequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Request
    template_name = 'request/request_confirm_delete.html'
    success_url = reverse_lazy('request-list')
    context_object_name = 'request_obj'

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff


# ------------------------
# API Views
# ------------------------

class CategoryListAPI(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        data = [{'id': i, 'value': c[0], 'label': c[1]} for i, c in enumerate(CATEGORY_CHOICES, 1)]
        return Response(data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def autosuggest(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        tags = Tag.objects.filter(name__icontains=query).distinct()[:10]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Request.objects.prefetch_related('tags')
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
