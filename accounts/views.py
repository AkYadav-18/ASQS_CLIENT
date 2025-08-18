from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CustomUser
from Clients.models import Client
from Clients.status_history import ClientStatusHistory
from Partners.models import Partner
from Standards.models import Standards


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember me
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'accounts/login.html',locals())




def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def anaytics(request):
    # Get current date and calculate date ranges
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # Basic counts
    total_clients = Client.objects.count()
    total_partners = Partner.objects.count()
    total_standards = Standards.objects.count()

    # Recent additions (last 30 days)
    recent_clients = Client.objects.filter(created_at__date__gte=thirty_days_ago).count()
    recent_partners = Partner.objects.filter(created_at__date__gte=thirty_days_ago).count()
    recent_standards = Standards.objects.filter(created_at__date__gte=thirty_days_ago).count()

    # Weekly additions (last 7 days)
    weekly_clients = Client.objects.filter(created_at__date__gte=seven_days_ago).count()
    weekly_partners = Partner.objects.filter(created_at__date__gte=seven_days_ago).count()
    weekly_standards = Standards.objects.filter(created_at__date__gte=seven_days_ago).count()

    # Client status distribution
    client_status_data = Client.objects.values('certification_status').annotate(
        count=Count('id')
    ).order_by('certification_status')

    # Top countries by client count
    top_countries = Client.objects.values('country').annotate(
        count=Count('id')
    ).exclude(country__isnull=True).exclude(country='').order_by('-count')[:5]

    # Partner countries distribution
    partner_countries = Partner.objects.values('country').annotate(
        count=Count('id')
    ).exclude(country__isnull=True).exclude(country='').order_by('-count')[:5]

    # Monthly data for charts (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):  # Start from 5 months ago to current month
        # Calculate the first day of the month
        if i == 0:
            month_start = today.replace(day=1)
        else:
            # Go back i months
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            month_start = today.replace(year=year, month=month, day=1)

        # Calculate the last day of the month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        clients_count = Client.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()

        partners_count = Partner.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()

        standards_count = Standards.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()

        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'clients': clients_count,
            'partners': partners_count,
            'standards': standards_count
        })

    # Certification expiry analysis
    upcoming_expiry = Client.objects.filter(
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gte=today
    ).count()

    expired_certs = Client.objects.filter(
        expiry_date__lt=today
    ).count()

    # Recent activity (last 5 items)
    recent_clients_list = Client.objects.order_by('-created_at')[:5]
    recent_partners_list = Partner.objects.order_by('-created_at')[:5]
    recent_standards_list = Standards.objects.order_by('-created_at')[:5]

    # Standards usage analysis
    standards_usage = Client.objects.values('standard').annotate(
        count=Count('id')
    ).exclude(standard__isnull=True).exclude(standard='').order_by('-count')[:5]

    # Get real status timeline data
    status_timeline_data = ClientStatusHistory.get_status_timeline_data(months=6)

    # Calculate expiring certifications (next 30 days)
    thirty_days_from_now = today + timedelta(days=30)
    expiring_soon = Client.objects.filter(
        expiry_date__lte=thirty_days_from_now,
        expiry_date__gte=today,
        certification_status='active'
    ).count()

    context = {
        # Basic counts
        'total_clients': total_clients,
        'total_partners': total_partners,
        'total_standards': total_standards,
        'expiring_soon': expiring_soon,

        # Recent additions
        'recent_clients': recent_clients,
        'recent_partners': recent_partners,
        'recent_standards': recent_standards,

        # Weekly additions
        'weekly_clients': weekly_clients,
        'weekly_partners': weekly_partners,
        'weekly_standards': weekly_standards,

        # Status and country data
        'client_status_data': list(client_status_data),
        'top_countries': list(top_countries),
        'partner_countries': list(partner_countries),

        # Monthly chart data
        'monthly_data': monthly_data,

        # Expiry data
        'upcoming_expiry': upcoming_expiry,
        'expired_certs': expired_certs,

        # Recent activity
        'recent_clients_list': recent_clients_list,
        'recent_partners_list': recent_partners_list,
        'recent_standards_list': recent_standards_list,

        # Standards usage
        'standards_usage': list(standards_usage),

        # Real status timeline data
        'status_timeline_data': status_timeline_data,
    }

    return render(request, 'accounts/analytics.html', context)
