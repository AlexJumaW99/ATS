from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate
from .gemini_parser import process_resume
from django.http import JsonResponse

@login_required
def parser_home(request):
    """
    Renders the main page of the parser app and displays candidates.
    """
    candidates = Candidate.objects.all()
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
                        degree=item.get('degree'),
                        resume_file_name=resume_file.name
                    )
        if raw_csv_outputs:
            csv_output = "\n\n".join(raw_csv_outputs)

        return JsonResponse({'csv_output': csv_output})

    candidates = Candidate.objects.all()
    return render(request, 'parser/parser_home.html', {'candidates': candidates, 'csv_output': csv_output})