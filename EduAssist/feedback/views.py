from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test # Added user_passes_test
from .models import Feedback
from .forms import FeedbackForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# --- Helper Function for Staff Check ---
def is_staff_check(user):
    """Checks if the user is active and has staff status."""
    return user.is_active and user.is_staff

# --- User Views (Submit, List, Edit, Delete) ---

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
    # Ensure only the owner can edit their feedback
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
    # Ensure only the owner can delete their feedback
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, "Feedback deleted.")
        return redirect('my_feedback')
    return render(request, 'feedback/confirm_delete.html', {'feedback': feedback})

# --- AJAX View ---

@login_required
@csrf_exempt # Use this carefully, or ensure you send the CSRF token in your AJAX request
def submit_feedback_ajax(request):
    if request.method == "POST":
        try:
            # Handle JSON data from the request body
            data = json.loads(request.body)
            rating = int(data.get('rating', 0))
            comment = data.get('comment', '').strip()

            # Server-side validation
            if rating < 1 or rating > 5:
                return JsonResponse({"success": False, "error": "Invalid rating."}, status=400)

            # Example custom validation logic: require comment for 1-star
            if rating == 1 and not comment:
                return JsonResponse({"success": False, "error": "Comment required for 1-star rating."}, status=400)

            # Create the feedback object
            Feedback.objects.create(user=request.user, rating=rating, comment=comment)
            return JsonResponse({"success": True, "message": "Feedback submitted successfully."})
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)
        except Exception as e:
            print(f"Error submitting AJAX feedback: {e}")
            return JsonResponse({"success": False, "error": "Unable to submit feedback at this time."}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


# --- Admin View (Staff Only) ---

@user_passes_test(is_staff_check, login_url='/admin/login/') 
def all_feedback(request):
    """Admin view to see all feedback submissions."""
    feedbacks = Feedback.objects.all().order_by('-created_at') 
    
    # --- FIX: Pass a range iterable for the star icons ---
    STAR_RANGE = range(1, 6) # Creates the iterable [1, 2, 3, 4, 5]
    
    return render(request, 'feedback/all_feedback.html', {
        'feedbacks': feedbacks,
        'star_range': STAR_RANGE, # Pass the new variable to the template
    })