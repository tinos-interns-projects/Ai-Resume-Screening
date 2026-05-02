from django.contrib import admin
from .models import Job, Resume

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['candidate_name', 'job', 'match_score', 'uploaded_at']
    list_filter = ['job', 'uploaded_at']
    search_fields = ['candidate_name', 'extracted_text']