from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def parser_home(request):
    """
    Renders the main page of the parser app.
    """
    return render(request, 'parser/parser_home.html')