from django.db import models

class Candidate(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    degree_school = models.CharField(max_length=255, null=True, blank=True)
    diploma = models.CharField(max_length=255, null=True, blank=True)
    diploma_school = models.CharField(max_length=255, null=True, blank=True)
    resume_file_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"