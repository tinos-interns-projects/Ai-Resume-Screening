

# Create your models here.
from django.db import models
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Paste job requirements here")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Resume(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    candidate_name = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='resumes/%Y/%m/')
    extracted_text = models.TextField(blank=True)
    match_score = models.FloatField(default=0.0)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.candidate_name or 'Unknown'} - {self.match_score}%"