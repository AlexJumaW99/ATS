from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Route for the main landing page
    path('', views.landing_page, name='landing_page'),

    # Route for the login page
    path('login/', views.login_view, name='login'),

    # Route for logging out
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'),
]
