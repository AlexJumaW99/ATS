from django.urls import path
from . import views

urlpatterns = [
    path('', views.parser_home, name='parser_home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('create_job/', views.create_job, name='create_job'),
    path('create_job_posting/', views.create_job_posting, name='create_job_posting'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('job/<int:job_id>/', views.job_posting_details, name='job_posting_details'),
]