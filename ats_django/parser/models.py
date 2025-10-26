from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50)
    salary_range = models.CharField(max_length=100)
    closing_date = models.DateField()

    def __str__(self):
        return self.title

class Candidate(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    degree_school = models.CharField(max_length=255, null=True, blank=True)
    diploma = models.CharField(max_length=255, null=True, blank=True)
    diploma_school = models.CharField(max_length=255, null=True, blank=True)
    resume_file_name = models.CharField(max_length=255)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"