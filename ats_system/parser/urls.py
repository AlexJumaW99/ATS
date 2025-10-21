from django.urls import path
from . import views

urlpatterns = [
    path('', views.parser_home, name='parser_home'),
    path('upload/', views.upload_resume, name='upload_resume'), # New URL for uploading
]