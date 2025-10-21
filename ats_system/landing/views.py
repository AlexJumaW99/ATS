from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q

def landing_page(request):
    """
    Renders the main landing page.
    """
    return render(request, 'landing/landing_page.html')

def login_view(request):
    """
    Handles user login.
    - On GET request, it displays the login form.
    - On POST request, it authenticates the user using either username or email.
    """
    error_message = None
    if request.method == 'POST':
        # Get username and password from the form
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Try to find a user with the given username or email
        user = None
        try:
            # Q objects allow for complex queries, in this case OR
            user_q = User.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
            # We found a user by username or email, now authenticate with their actual username
            user = authenticate(request, username=user_q.username, password=password)
        except User.DoesNotExist:
            error_message = "Invalid credentials. Please try again."

        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            return redirect('parser_home') # Redirect to the parser app's home page
        else:
            # If authentication fails, set an error message
            if not error_message:
                error_message = "Invalid credentials. Please try again."

    # If it's a GET request or login failed, render the login page with an error message
    context = {'error': error_message}
    return render(request, 'landing/login.html', context)