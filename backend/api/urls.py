from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, ResumeViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'resumes', ResumeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]