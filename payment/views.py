from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from landing.models import SongSubmission
from .models import Package
import requests

def process_payment(request):
    if request.method == 'POST':
        try:
            song_id = request.POST.get('song_id')
            if not song_id:
                raise ValueError("Song ID is required")
                
            song = get_object_or_404(SongSubmission, pk=song_id)

            # Get the package from the song if it was selected during submission
            package = song.package

            # If no package was selected, get the default one
            if not package:
                package = Package.objects.filter(is_active=True).first()
                if not package:
                    raise ValueError("No active package available")
                # Update the song with the selected package
                song.package = package
                song.save()
                
            tx_ref = f"PTP-{song.id}-{package.id}-{int(timezone.now().timestamp())}"
            return render(request, 'payment/process.html', {
                'song': song,
                'package': package,
                'flutterwave_public_key': settings.FLUTTERWAVE_PUBLIC_KEY,
                'tx_ref': tx_ref,
                'callback_url': request.build_absolute_uri(reverse('payment:verify'))
            })
            
        except SongSubmission.DoesNotExist:
            return render(request, 'payment/error.html', {
                'message': 'Song submission not found',
                'redirect_url': reverse('landing:submit_song')
            })
        except Exception as e:
            return render(request, 'payment/error.html', {
                'message': str(e),
                'redirect_url': reverse('landing:submit_song')
            })

    return render(request, 'payment/error.html', {
        'message': 'Invalid request method',
        'redirect_url': reverse('landing:submit_song')
    })

def verify_payment(request):
    if request.method == 'GET':
        try:
            transaction_id = request.GET.get('transaction_id')
            tx_ref = request.GET.get('tx_ref')
            status = request.GET.get('status')

            if not transaction_id or not tx_ref:
                raise ValueError("Missing payment verification parameters")

            # Extract song_id from tx_ref (format: PTP-{song_id}-{package_id}-{timestamp})
            parts = tx_ref.split('-')
            if len(parts) < 3:
                raise ValueError("Invalid transaction reference format")

            song_id = parts[1]
            song = get_object_or_404(SongSubmission, pk=song_id)

            # Verify with Flutterwave
            if status == 'successful':
                verification_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
                headers = {
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
                }

                response = requests.get(verification_url, headers=headers)
                response.raise_for_status()
                verification_data = response.json()

                if verification_data['status'] == 'success' and verification_data['data']['status'] == 'successful':
                    # Update payment status
                    song.payment_status = 'completed'
                    song.transaction_reference = transaction_id
                    song.payment_date = timezone.now()
                    song.save()

                    return render(request, 'payment/success.html', {
                        'song': song,
                        'package': song.package
                    })

            # If we get here, payment verification failed
            song.payment_status = 'failed'
            song.save()
            raise ValueError("Payment verification failed")

        except Exception as e:
            return render(request, 'payment/error.html', {
                'message': str(e),
                'redirect_url': reverse('landing:submit_song')
            })

    return render(request, 'payment/error.html', {
        'message': 'Invalid request method',
        'redirect_url': reverse('landing:submit_song')
    })