from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job, Resume
from .serializers import JobSerializer, ResumeSerializer
from .ai_processor import extract_text, calculate_match_score, extract_candidate_name

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    @action(detail=False, methods=['post'])
    def upload_and_screen(self, request):
        job_id = request.data.get('job_id')
        file = request.FILES.get('resume')
        
        if not job_id or not file:
            return Response({"error": "job_id and resume file required"}, status=400)
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)
        
        # Create resume object
        resume = Resume.objects.create(
            job=job,
            file=file,
            candidate_name="Processing..."
        )
        
        # Extract text from resume
        try:
            resume.extracted_text = extract_text(resume.file.path)
            # Extract and update candidate name
            resume.candidate_name = extract_candidate_name(resume.extracted_text)
        except Exception as e:
            resume.delete()
            return Response(
                {"error": f"Failed to extract text: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Calculate match score
        resume.match_score = calculate_match_score(job.description, resume.extracted_text)
        
        # Save results
        resume.save()
        
        return Response({
            "id": resume.id,
            "candidate_name": resume.candidate_name,
            "match_score": resume.match_score,
            "message": "Resume screened successfully!"
        }, status=201)

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Delete all resumes for a specific job"""
        job_id = request.query_params.get('job')
        
        if not job_id:
            return Response({"error": "Job ID required"}, status=400)
        
        count, _ = Resume.objects.filter(job_id=job_id).delete()
        
        return Response({
            "message": f"Deleted {count} candidates",
            "count": count
        })