from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Enquiry
from Clients.models import Client
import json
from datetime import date


@csrf_protect
def home_page(request, template_name='HomePage/home.html'):
    """Home page view with enquiry form handling"""

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()

            # Validate required fields
            if not all([name, email, mobile, subject, message]):
                messages.error(request, 'All fields are required. Please fill in all the information.')
                return render(request, template_name, {
                    'form_data': request.POST
                })

            # Validate email format (basic validation)
            if '@' not in email or '.' not in email:
                messages.error(request, 'Please enter a valid email address.')
                return render(request, template_name, {
                    'form_data': request.POST
                })

            # Create enquiry record
            enquiry = Enquiry.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                subject=subject,
                message=message
            )

            messages.success(request,
                f'Thank you {name}! Your enquiry has been submitted successfully. '
                'We will get back to you within 24 hours.'
            )

            # Redirect to prevent form resubmission
            return redirect('home')

        except Exception as e:
            messages.error(request, 'Sorry, there was an error submitting your enquiry. Please try again.')
            return render(request, template_name, {
                'form_data': request.POST
            })

    # GET request - show the home page
    return render(request, template_name)


@require_http_methods(["POST"])
@csrf_protect
def submit_enquiry_ajax(request):
    """AJAX endpoint for enquiry form submission"""
    try:
        # Parse JSON data if sent as JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        # Get form data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        # Validate required fields
        if not all([name, email, mobile, subject, message]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required. Please fill in all the information.'
            })

        # Validate email format
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address.'
            })

        # Create enquiry record
        enquiry = Enquiry.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            subject=subject,
            message=message
        )

        return JsonResponse({
            'success': True,
            'message': f'Thank you {name}! Your enquiry has been submitted successfully. We will get back to you within 24 hours.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Sorry, there was an error submitting your enquiry. Please try again.'
        })


@require_http_methods(["POST"])
@csrf_protect
def check_certificate(request):
    """AJAX endpoint for certificate verification"""
    try:
        # Parse JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        client_name = data.get('client_name', '').strip()
        certificate_number = data.get('certificate_number', '').strip()

        # Validate required fields
        if not client_name or not certificate_number:
            return JsonResponse({
                'success': False,
                'error': 'Both client name and certificate number are required.'
            })

        # Search for the certificate
        # Use Q objects for flexible searching
        client = Client.objects.filter(
            Q(name__icontains=client_name) &
            Q(certification_number__iexact=certificate_number)
        ).first()

        if not client:
            # Try alternative search patterns
            client = Client.objects.filter(
                Q(name__iexact=client_name) &
                Q(certification_number__icontains=certificate_number)
            ).first()

        if not client:
            return JsonResponse({
                'success': False,
                'error': f'No certificate found for client "{client_name}" with certificate number "{certificate_number}".'
            })

        # Check if certificate is active
        is_active = client.certification_status == 'active'

        # Check if certificate is expired based on expiry date
        if client.expiry_date and client.expiry_date < date.today():
            is_active = False

        # Format dates for display
        issue_date = client.issue_date.strftime('%B %d, %Y') if client.issue_date else 'Not specified'
        expiry_date = client.expiry_date.strftime('%B %d, %Y') if client.expiry_date else 'Not specified'

        # Prepare certificate data
        certificate_data = {
            'client_name': client.name,
            'certificate_number': client.certification_number,
            'standard': client.standard or 'Not specified',
            'issue_date': issue_date,
            'expiry_date': expiry_date,
            'scope': client.scope or None,
            'accreditation_body': client.accreditation_body or 'Not specified',
            'certification_status': client.get_certification_status_display(),
            'is_active': is_active,
            'country': client.country,
            'address': client.address
        }

        return JsonResponse({
            'success': True,
            'certificate': certificate_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while checking the certificate. Please try again.'
        })


@login_required
def enquiry_management(request):
    """View for managing customer enquiries"""

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Start with all enquiries
    enquiries = Enquiry.objects.all()

    # Apply status filter
    if status_filter:
        enquiries = enquiries.filter(status=status_filter)

    # Apply search filter
    if search_query:
        enquiries = enquiries.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    # Order by creation date (newest first)
    enquiries = enquiries.order_by('-created_at')

    # Pagination
    paginator = Paginator(enquiries, 10)  # Show 10 enquiries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get status choices for filter dropdown
    status_choices = Enquiry.ENQUIRY_STATUS_CHOICES

    context = {
        'page_obj': page_obj,
        'status_choices': status_choices,
        'current_status': status_filter,
        'search_query': search_query,
        'total_enquiries': enquiries.count(),
    }

    return render(request, 'HomePage/enquiry.html', context)


@login_required
@csrf_protect
def update_enquiry_status(request, enquiry_id):
    """AJAX endpoint to update enquiry status"""
    if request.method == 'POST':
        try:
            enquiry = get_object_or_404(Enquiry, id=enquiry_id)
            new_status = request.POST.get('status')

            if new_status in dict(Enquiry.ENQUIRY_STATUS_CHOICES):
                enquiry.status = new_status
                enquiry.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Enquiry status updated to {enquiry.get_status_display()}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid status'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error updating enquiry status'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@csrf_protect
def add_enquiry_response(request, enquiry_id):
    """AJAX endpoint to add response to enquiry"""
    if request.method == 'POST':
        try:
            enquiry = get_object_or_404(Enquiry, id=enquiry_id)
            response_text = request.POST.get('response', '').strip()

            if response_text:
                enquiry.response = response_text
                enquiry.responded_at = timezone.now()
                enquiry.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Response added successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Response cannot be empty'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error adding response'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def services_page(request):
    """Services page view"""
    return render(request, 'HomePage/services.html')


def about_us_page(request):
    """About Us page view"""
    return render(request, 'HomePage/about_us.html')

