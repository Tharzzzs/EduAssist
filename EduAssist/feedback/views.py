from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Feedback
from .forms import FeedbackForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Feedback
import json

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you, your feedback has been submitted!")
            return redirect('my_feedback')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/submit_feedback.html', {'form': form})

@login_required
def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'feedback/my_feedback.html', {'feedbacks': feedbacks})

@login_required
def edit_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Feedback updated.")
            return redirect('my_feedback')
    else:
        form = FeedbackForm(instance=feedback)
    return render(request, 'feedback/edit_feedback.html', {'form': form})

@login_required
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, "Feedback deleted.")
        return redirect('my_feedback')
    return render(request, 'feedback/confirm_delete.html', {'feedback': feedback})

@login_required
@csrf_exempt  # optional if you send CSRF token
def submit_feedback_ajax(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rating = int(data.get('rating', 0))
            comment = data.get('comment', '').strip()

            if rating < 1 or rating > 5:
                return JsonResponse({"success": False, "error": "Invalid rating."})

            if rating == 1 and not comment:
                return JsonResponse({"success": False, "error": "Comment required for 1-star rating."})

            Feedback.objects.create(user=request.user, rating=rating, comment=comment)
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": "Unable to submit feedback at this time."})

    return JsonResponse({"success": False, "error": "Invalid request method."})