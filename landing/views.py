from .api_utils import fetch_spotify_track_details, fetch_youtube_video_details
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
from .forms import SongSubmissionForm
from .models import SongSubmission
import logging
import json


def submit_song(request):
    if request.method == 'POST':
        # Check if this is an AJAX request (from JavaScript)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'multipart/form-data':
            form = SongSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    submission = form.save(commit=False)

                    # Get the package ID from the form data
                    package_id = request.POST.get('package')
                    if package_id:
                        try:
                            # Get the package from the database
                            from payment.models import Package
                            package = Package.objects.get(pk=package_id)
                            submission.package = package
                        except Package.DoesNotExist:
                            # If package doesn't exist, set to None
                            submission.package = None

                    if request.user.is_authenticated:
                        submission.user = request.user

                    submission.save()

                    # Return JSON response for AJAX requests
                    return JsonResponse({
                        'success': True,
                        'message': 'Your song has been submitted successfully! Redirecting to payment...',
                        'song_id': submission.id
                    })
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())  # Print detailed error for debugging
                    return JsonResponse({
                        'success': False,
                        'message': f'An error occurred while saving your submission: {str(e)}'
                    }, status=500)
            else:
                # Form validation failed - return errors
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': form.errors
                }, status=400)
        else:
            # Handle regular form submission (non-AJAX)
            form = SongSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                if request.user.is_authenticated:
                    submission.user = request.user
                submission.save()
                messages.success(request, 'Your song has been submitted successfully! Redirecting to payment...')
                return redirect('payment:process', song_id=submission.id)
    else:
        form = SongSubmissionForm()
    
    # Get all active packages to display in the template
    from payment.models import Package
    packages = Package.objects.filter(is_active=True)

    return render(request, 'landing/submit_song.html', {
        'form': form,
        'packages': packages
    })

@csrf_exempt
def fetch_song_details(request):
    if request.method == 'POST':
        try:
            # Parse JSON data for fetch request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                link = data.get('link', '')
                link_type = data.get('link_type', 'spotify')
            else:
                link = request.POST.get('link', '')
                link_type = request.POST.get('link_type', 'spotify')
            
            if link_type == 'spotify':
                track_details = fetch_spotify_track_details(link)
            else:
                track_details = fetch_youtube_video_details(link)
            
            if track_details:
                return JsonResponse({
                    'success': True,
                    'data': track_details
                })
            return JsonResponse({
                'success': False,
                'message': 'Could not fetch song details. Please check the link.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def landing_page(request):
    return render(request, 'landing/index.html')

def terms_page(request):
    return render(request, 'landing/terms.html')

def privacy_page(request):
    return render(request, 'landing/privacy.html')

def submitted_page(request):
    return render(request, 'landing/submitted_song.html')