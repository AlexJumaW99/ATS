from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Candidate, Job, Profile
from .gemini_parser import process_resume
from django.http import JsonResponse
from django.db.models import Q
from datetime import date
from .forms import JobForm, ProfileUpdateForm
import json
import random

@login_required
def parser_home(request):
    """
    Renders the main page of the parser app and displays candidates.
    """
    jobs = Job.objects.select_related('created_by', 'created_by__profile').all().order_by('-opening_date')
    selected_job_id = request.GET.get('job_id')
    newly_created_job_id = request.GET.get('new_job_id')
    selected_job = None
    candidates = Candidate.objects.none()

    if newly_created_job_id:
        selected_job_id = newly_created_job_id

    if selected_job_id:
        try:
            selected_job = Job.objects.select_related('created_by').get(id=selected_job_id)
            candidates = Candidate.objects.filter(job=selected_job)
        except Job.DoesNotExist:
            pass
    elif jobs.exists():
        selected_job = jobs.first()
        candidates = Candidate.objects.filter(job=selected_job)

    # Filtering
    filters = {
        'first_name__icontains': request.GET.get('first_name'),
        'last_name__icontains': request.GET.get('last_name'),
        'address__icontains': request.GET.get('address'),
        'degree__icontains': request.GET.get('degree'),
        'degree_school__icontains': request.GET.get('degree_school'),
        'diploma__icontains': request.GET.get('diploma'),
        'diploma_school__icontains': request.GET.get('diploma_school'),
        'resume_file_name__icontains': request.GET.get('resume_file_name'),
    }
    for key, value in filters.items():
        if value:
            candidates = candidates.filter(**{key: value})

    min_dob = request.GET.get('min_dob')
    max_dob = request.GET.get('max_dob')
    if min_dob:
        candidates = candidates.filter(date_of_birth__gte=min_dob)
    if max_dob:
        candidates = candidates.filter(date_of_birth__lte=max_dob)

    sort_by = request.GET.get('sort_by', 'id')
    order = request.GET.get('order', 'asc')

    query_params = request.GET.copy()
    if 'sort_by' in query_params:
        del query_params['sort_by']
    if 'order' in query_params:
        del query_params['order']

    if order == 'desc':
        sort_by_param = f'-{sort_by}'
    else:
        sort_by_param = sort_by
    candidates = candidates.order_by(sort_by_param)

    job_form = JobForm()
    
    try:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)


    # Analytics data
    total_jobs = Job.objects.count()
    total_candidates = Candidate.objects.count()
    top_applicants = 0 # Placeholder for now

    context = {
        'jobs': jobs,
        'selected_job': selected_job,
        'candidates': candidates,
        'query_params': query_params.urlencode(),
        'job_form': job_form,
        'profile_form': profile_form,
        'total_jobs': total_jobs,
        'total_candidates': total_candidates,
        'top_applicants': top_applicants,
    }

    return render(request, 'parser/parser_home.html', context)

@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            return JsonResponse({'success': True, 'job': {'id': job.id, 'title': job.title}})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method.'})


@login_required
def create_job_posting(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            return redirect(f"{reverse('parser_home')}?new_job_id={job.id}")
    else:
        form = JobForm()
    return render(request, 'parser/create_job_posting.html', {'form': form})


@login_required
def upload_resume(request):
    """
    Handles the resume upload, sends it to the Gemini API for parsing,
    and saves the extracted data.
    """
    csv_output = None
    if request.method == 'POST':
        resume_files = request.FILES.getlist('resumes')
        job_id = request.POST.get('job_id')
        job = Job.objects.get(id=job_id)
        all_parsed_data = []
        raw_csv_outputs = []

        for resume_file in resume_files:
            parsed_data, raw_csv = process_resume(resume_file)
            if parsed_data:
                all_parsed_data.extend(parsed_data)
                if raw_csv:
                    raw_csv_outputs.append(raw_csv)
                for item in parsed_data:
                    Candidate.objects.create(
                        first_name=item.get('first_name'),
                        last_name=item.get('last_name'),
                        date_of_birth=item.get('date_of_birth') or None,
                        address=item.get('address'),
                        degree=item.get('degree'),
                        degree_school=item.get('degree_school'),
                        diploma=item.get('diploma'),
                        diploma_school=item.get('diploma_school'),
                        resume_file_name=resume_file.name,
                        job=job,
                        uploaded_by=request.user
                    )
        if raw_csv_outputs:
            csv_output = "\n\n".join(raw_csv_outputs)

        return JsonResponse({'csv_output': csv_output, 'parsed_data': all_parsed_data})

    jobs = Job.objects.all()
    candidates = Candidate.objects.all()
    return render(request, 'parser/parser_home.html', {'jobs': jobs, 'candidates': candidates, 'csv_output': csv_output})


def autocomplete(request):
    if 'term' in request.GET and 'field' in request.GET:
        field = request.GET.get('field')
        term = request.GET.get('term')

        valid_fields = [f.name for f in Candidate._meta.get_fields()]
        if field not in valid_fields:
            return JsonResponse([], safe=False)

        qs = Candidate.objects.filter(**{f'{field}__icontains': term})
        values = list(qs.values_list(field, flat=True).distinct())
        return JsonResponse(values, safe=False)
    return JsonResponse([], safe=False)

@login_required
def delete_job(request, job_id):
    """
    Deletes a job and all associated candidates.
    """
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('parser_home')
    return redirect('parser_home')

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('parser_home')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'parser/parser_home.html', {'profile_form': profile_form})