from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test

from landing.models import SongSubmission
from payment.models import Package
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay, TruncMonth
from .decorators import admin_required

import json
from datetime import timedelta

def is_admin(user):
    """Check if user is an admin (staff or superuser)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def admin_login(request):
    """Admin login view - only accessible to unauthenticated users"""
    # If user is already logged in and is admin, redirect to dashboard home
    if is_admin(request.user):
        return redirect('admin_dashboard:dashboard_home')

    # If user is logged in but not admin, show access denied
    if request.user.is_authenticated:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('landing:index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            # Check if user exists and is admin
            if user is not None and is_admin(user):
                login(request, user)
                messages.success(request, f"Welcome to the admin dashboard, {username}!")
                return redirect('admin_dashboard:home')
            else:
                messages.error(request, "Invalid username or password, or insufficient permissions.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'admin_dashboard/login.html', {'form': form})

@admin_required
def dashboard_home(request):
    # Dashboard statistics
    total_submissions = SongSubmission.objects.count()
    pending_submissions = SongSubmission.objects.filter(is_approved=False).count()
    approved_submissions = SongSubmission.objects.filter(is_approved=True).count()
    total_revenue = SongSubmission.objects.filter(
        payment_status='completed'
    ).aggregate(total=Sum('package__price'))['total'] or 0
    
    # Recent submissions
    recent_submissions = SongSubmission.objects.order_by('-submission_date')[:5]
    
    # Monthly revenue data for chart
    thirty_days_ago = timezone.now() - timedelta(days=30)
    revenue_by_day = SongSubmission.objects.filter(
        payment_status='completed',
        payment_date__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('payment_date')
    ).values('day').annotate(
        total=Sum('package__price')
    ).order_by('day')
    
    # Prepare chart data
    chart_labels = [entry['day'].strftime('%d %b') for entry in revenue_by_day]
    chart_data = [float(entry['total']) for entry in revenue_by_day]
    
    context = {
        'total_submissions': total_submissions,
        'pending_submissions': pending_submissions,
        'approved_submissions': approved_submissions,
        'total_revenue': total_revenue,
        'recent_submissions': recent_submissions,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'admin_dashboard/dashboard_home.html', context)

@admin_required
def song_list(request):
    # Filter parameters
    status = request.GET.get('status', '')
    genre = request.GET.get('genre', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    songs = SongSubmission.objects.all().order_by('-submission_date')
    
    # Apply filters
    if status:
        if status == 'approved':
            songs = songs.filter(is_approved=True)
        elif status == 'pending':
            songs = songs.filter(is_approved=False)
        elif status == 'paid':
            songs = songs.filter(payment_status='completed')
        elif status == 'unpaid':
            songs = songs.filter(payment_status='pending')
    
    if genre:
        songs = songs.filter(genre=genre)
    
    if search:
        songs = songs.filter(
            artist_name__icontains=search
        ) | songs.filter(
            song_title__icontains=search
        ) | songs.filter(
            email__icontains=search
        )
    
    context = {
        'songs': songs,
        'status': status,
        'genre': genre,
        'search': search,
        'genre_choices': SongSubmission.GENRE_CHOICES,
    }
    
    return render(request, 'admin_dashboard/song_list.html', context)

@admin_required
def song_detail(request, song_id):
    song = get_object_or_404(SongSubmission, pk=song_id)
    
    if request.method == 'POST':
        # Handle form submission for updating notes
        notes = request.POST.get('notes', '')
        song.notes = notes
        song.save()
        messages.success(request, 'Notes updated successfully')
        return redirect('admin_dashboard:song_detail', song_id=song.id)
    
    context = {
        'song': song,
    }
    
    return render(request, 'admin_dashboard/song_detail.html', context)

@admin_required
def song_approve(request, song_id):
    song = get_object_or_404(SongSubmission, pk=song_id)
    song.is_approved = True
    song.save()
    messages.success(request, f'Song "{song.song_title}" by {song.artist_name} has been approved')
    return redirect('admin_dashboard:song_list')

@admin_required
def song_reject(request, song_id):
    song = get_object_or_404(SongSubmission, pk=song_id)
    song.is_approved = False
    song.save()
    messages.success(request, f'Song "{song.song_title}" by {song.artist_name} has been rejected')
    return redirect('admin_dashboard:song_list')

@admin_required
def payment_list(request):
    # Filter parameters
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Base queryset - all songs with payments
    payments = SongSubmission.objects.exclude(payment_status='').order_by('-payment_date')
    
    # Apply filters
    if status:
        payments = payments.filter(payment_status=status)
    
    if search:
        payments = payments.filter(
            artist_name__icontains=search
        ) | payments.filter(
            song_title__icontains=search
        ) | payments.filter(
            email__icontains=search
        ) | payments.filter(
            transaction_reference__icontains=search
        )
    
    context = {
        'payments': payments,
        'status': status,
        'search': search,
        'payment_status_choices': SongSubmission.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'admin_dashboard/payment_list.html', context)

@admin_required
def payment_detail(request, payment_id):
    song = get_object_or_404(SongSubmission, pk=payment_id)
    
    context = {
        'payment': song,
    }
    
    return render(request, 'admin_dashboard/payment_detail.html', context)

@admin_required
def package_list(request):
    packages = Package.objects.all().order_by('price')
    
    context = {
        'packages': packages,
    }
    
    return render(request, 'admin_dashboard/package_list.html', context)

@admin_required
def package_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'
        
        if name and price:
            package = Package(
                name=name,
                description=description,
                price=price,
                is_active=is_active
            )
            package.save()
            messages.success(request, f'Package "{name}" has been added')
            return redirect('admin_dashboard:package_list')
        else:
            messages.error(request, 'Name and price are required')
    
    return render(request, 'admin_dashboard/package_form.html', {
        'action': 'Add',
    })

@admin_required
def package_edit(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'
        
        if name and price:
            package.name = name
            package.description = description
            package.price = price
            package.is_active = is_active
            package.save()
            messages.success(request, f'Package "{name}" has been updated')
            return redirect('admin_dashboard:package_list')
        else:
            messages.error(request, 'Name and price are required')
    
    return render(request, 'admin_dashboard/package_form.html', {
        'action': 'Edit',
        'package': package,
    })

@admin_required
def package_delete(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    
    if request.method == 'POST':
        package_name = package.name
        package.delete()
        messages.success(request, f'Package "{package_name}" has been deleted')
        return redirect('admin_dashboard:package_list')
    
    return render(request, 'admin_dashboard/package_confirm_delete.html', {
        'package': package,
    })

@admin_required
def analytics(request):
    # Submissions over time
    thirty_days_ago = timezone.now() - timedelta(days=30)
    submissions_by_day = SongSubmission.objects.filter(
        submission_date__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('submission_date')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Genre distribution
    genre_distribution = SongSubmission.objects.values('genre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Payment status distribution
    payment_status_distribution = SongSubmission.objects.values('payment_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Approval rate
    total_reviewed = SongSubmission.objects.count()
    approved_count = SongSubmission.objects.filter(is_approved=True).count()
    approval_rate = (approved_count / total_reviewed * 100) if total_reviewed > 0 else 0
    
    # Calculate pending rate (100 - approval_rate)
    pending_rate = 100 - approval_rate

    # Prepare chart data
    submission_labels = [entry['day'].strftime('%d %b') for entry in submissions_by_day]
    submission_data = [entry['count'] for entry in submissions_by_day]
    
    genre_labels = [dict(SongSubmission.GENRE_CHOICES).get(entry['genre'], entry['genre']) for entry in genre_distribution]
    genre_data = [entry['count'] for entry in genre_distribution]
    
    payment_status_labels = [dict(SongSubmission.PAYMENT_STATUS_CHOICES).get(entry['payment_status'], entry['payment_status']) for entry in payment_status_distribution]
    payment_status_data = [entry['count'] for entry in payment_status_distribution]
    
    context = {
        'submission_labels': json.dumps(submission_labels),
        'submission_data': json.dumps(submission_data),
        'genre_labels': json.dumps(genre_labels),
        'genre_data': json.dumps(genre_data),
        'payment_status_labels': json.dumps(payment_status_labels),
        'payment_status_data': json.dumps(payment_status_data),
        'approval_rate': approval_rate,
        'pending_rate': pending_rate,
    }
    
    return render(request, 'admin_dashboard/analytics.html', context)