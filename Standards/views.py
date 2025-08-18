from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Standards
import json
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def add_standards(request, template_name='Standards/add_standards.html'):
    # Get all standards and apply filters
    standards = Standards.objects.all()

    # Apply search filter if provided
    search_filter = request.GET.get('search_filter')

    if search_filter:
        standards = standards.filter(Standard_name__icontains=search_filter)

    standards = standards.order_by('-created_at')

    # Add pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(standards, 10)  # Show 10 standards per page

    try:
        standards = paginator.page(page)
    except PageNotAnInteger:
        standards = paginator.page(1)
    except EmptyPage:
        standards = paginator.page(paginator.num_pages)

    # Check if this is an edit request
    edit_standard_id = request.GET.get('edit')
    edit_standard = None
    if edit_standard_id:
        try:
            edit_standard = Standards.objects.get(id=edit_standard_id)
        except Standards.DoesNotExist:
            messages.error(request, 'Standard not found.')
            return redirect('standards')

    if request.method == 'POST':
        try:
            # Check if this is an edit or add operation
            edit_id = request.POST.get('edit_standard_id')
            if edit_id:
                try:
                    standard = Standards.objects.get(id=edit_id)
                    operation = 'updated'
                except Standards.DoesNotExist:
                    messages.error(request, 'Standard not found for editing.')
                    return redirect('standards')
            else:
                # Create new standard instance
                standard = Standards()
                operation = 'added'

            # Set form data
            standard.Standard_name = request.POST.get('standard_name', '').strip()

            # Set created_by if user is authenticated
            if request.user.is_authenticated and not edit_id:
                standard.created_by = request.user

            # Validate required fields
            if not standard.Standard_name:
                messages.error(request, 'Standard name is required.')
                return render(request, template_name, {
                    'standards': standards,
                    'form_data': request.POST
                })

            # Save the standard
            standard.save()
            messages.success(request, f'Standard "{standard.Standard_name}" has been {operation} successfully!')
            return redirect('standards')

        except Exception as e:
            messages.error(request, f'Error adding standard: {str(e)}')

    return render(request, template_name, {
        'standards': standards,
        'edit_standard': edit_standard,
    })


@login_required
def get_standard(request, standard_id):
    """Get standard data for editing"""
    try:
        standard = Standards.objects.get(id=standard_id)
        standard_data = {
            'id': standard.id,
            'Standard_name': standard.Standard_name,
        }
        return JsonResponse({'success': True, 'standard': standard_data})
    except Standards.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Standard not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_standard(request, standard_id):
    """Delete standard"""
    try:
        standard = Standards.objects.get(id=standard_id)
        standard_name = standard.Standard_name
        standard.delete()
        return JsonResponse({'success': True, 'message': f'Standard "{standard_name}" has been deleted successfully!'})
    except Standards.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Standard not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
