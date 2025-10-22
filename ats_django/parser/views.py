from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate
from .gemini_parser import process_resume
from django.http import JsonResponse
from django.db.models import Q

@login_required
def parser_home(request):
    """
    Renders the main page of the parser app and displays candidates.
    """
    candidates = Candidate.objects.all()

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

    # Date of Birth range filtering
    min_dob = request.GET.get('min_dob')
    max_dob = request.GET.get('max_dob')
    if min_dob:
        candidates = candidates.filter(date_of_birth__gte=min_dob)
    if max_dob:
        candidates = candidates.filter(date_of_birth__lte=max_dob)

    # Sorting
    sort_by = request.GET.get('sort_by', 'id')
    order = request.GET.get('order', 'asc')
    if order == 'desc':
        sort_by = f'-{sort_by}'
    candidates = candidates.order_by(sort_by)

    return render(request, 'parser/parser_home.html', {'candidates': candidates})

@login_required
def upload_resume(request):
    """
    Handles the resume upload, sends it to the Gemini API for parsing,
    and saves the extracted data.
    """
    csv_output = None
    if request.method == 'POST':
        resume_files = request.FILES.getlist('resumes')
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
                        resume_file_name=resume_file.name
                    )
        if raw_csv_outputs:
            csv_output = "\n\n".join(raw_csv_outputs)

        return JsonResponse({'csv_output': csv_output, 'parsed_data': all_parsed_data})

    candidates = Candidate.objects.all()
    return render(request, 'parser/parser_home.html', {'candidates': candidates, 'csv_output': csv_output})

def autocomplete(request):
    if 'term' in request.GET and 'field' in request.GET:
        field = request.GET.get('field')
        term = request.GET.get('term')

        # Ensure the field is a valid field on the Candidate model to prevent security issues
        valid_fields = [f.name for f in Candidate._meta.get_fields()]
        if field not in valid_fields:
            return JsonResponse([], safe=False)

        qs = Candidate.objects.filter(**{f'{field}__icontains': term})
        values = list(qs.values_list(field, flat=True).distinct())
        return JsonResponse(values, safe=False)
    return JsonResponse([], safe=False)