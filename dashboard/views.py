from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from landing.models import SongSubmission
from .models import SupportRequest
from .forms import SupportRequestForm, ProfileUpdateForm

@login_required
def dashboard_home(request):
    # Get counts for summary stats
    songs_count = SongSubmission.objects.filter(user=request.user).count()
    pending_songs = SongSubmission.objects.filter(user=request.user, is_approved=False).count()
    approved_songs = SongSubmission.objects.filter(user=request.user, is_approved=True).count()
    
    # Get recent submissions
    recent_submissions = SongSubmission.objects.filter(
        user=request.user
    ).order_by('-submission_date')[:3]
    
    # Get recent support requests
    support_requests = SupportRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')[:3]
    
    context = {
        'user': request.user,
        'songs_count': songs_count,
        'pending_songs': pending_songs,
        'approved_songs': approved_songs,
        'recent_submissions': recent_submissions,
        'support_requests': support_requests,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def my_songs(request):
    songs = SongSubmission.objects.filter(user=request.user).order_by('-submission_date')
    
    context = {
        'songs': songs
    }
    
    return render(request, 'dashboard/my_songs.html', context)

@login_required
def my_payments(request):
    # Get all songs with payment information
    payments = SongSubmission.objects.filter(
        user=request.user
    ).exclude(
        payment_status=''
    ).order_by('-payment_date')
    
    context = {
        'payments': payments
    }
    
    return render(request, 'dashboard/my_payments.html', context)

@login_required
def support(request):
    support_requests = SupportRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'support_requests': support_requests
    }
    
    return render(request, 'dashboard/support.html', context)

@login_required
def create_support_request(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            
            # Send email notification to admins
            subject = f"New Support Request: {support_request.subject}"
            message = f"""
            A new support request has been submitted:
            
            From: {request.user.username} ({request.user.email})
            Subject: {support_request.subject}
            
            Message:
            {support_request.message}
            
            You can view this request in the admin dashboard.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            messages.success(request, "Your support request has been submitted. We'll get back to you soon.")
            return redirect('dashboard:support')
    else:
        form = SupportRequestForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'dashboard/create_support_request.html', context)

@login_required
def support_detail(request, request_id):
    support_request = get_object_or_404(SupportRequest, id=request_id, user=request.user)
    
    context = {
        'support_request': support_request
    }
    
    return render(request, 'dashboard/support_detail.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('dashboard:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form
    }
    
    return render(request, 'dashboard/profile.html', context)
