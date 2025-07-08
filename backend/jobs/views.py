from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Job, JobMatch, JobBoard, ScrapeLog
from .serializers import JobSerializer, JobMatchSerializer, JobBoardSerializer, ScrapeLogSerializer

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(company__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by location type
        location_type = self.request.query_params.get('location_type', None)
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        
        # Filter by job type
        job_type = self.request.query_params.get('job_type', None)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary', None)
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)
        
        max_salary = self.request.query_params.get('max_salary', None)
        if max_salary:
            queryset = queryset.filter(salary_max__lte=max_salary)
        
        # Filter by posted date
        days_ago = self.request.query_params.get('days_ago', None)
        if days_ago:
            date_threshold = timezone.now() - timedelta(days=int(days_ago))
            queryset = queryset.filter(posted_date__gte=date_threshold)
        
        return queryset

class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

class JobMatchListView(generics.ListAPIView):
    serializer_class = JobMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user)

class JobMatchDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = JobMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bookmark_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id, is_active=True)
        job_match, created = JobMatch.objects.get_or_create(
            user=request.user,
            job=job,
            defaults={'job_preference': request.user.job_preferences.first()}
        )
        job_match.is_bookmarked = not job_match.is_bookmarked
        job_match.save()
        
        return Response({
            'bookmarked': job_match.is_bookmarked,
            'message': 'Job bookmarked successfully' if job_match.is_bookmarked else 'Job unbookmarked successfully'
        })
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_applied(request, job_id):
    try:
        job = Job.objects.get(id=job_id, is_active=True)
        job_match, created = JobMatch.objects.get_or_create(
            user=request.user,
            job=job,
            defaults={'job_preference': request.user.job_preferences.first()}
        )
        job_match.is_applied = True
        job_match.save()
        
        return Response({'message': 'Job marked as applied successfully'})
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class JobBoardListView(generics.ListAPIView):
    queryset = JobBoard.objects.filter(is_active=True)
    serializer_class = JobBoardSerializer
    permission_classes = [permissions.IsAuthenticated]

class ScrapeLogListView(generics.ListAPIView):
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    user = request.user
    
    # Get user's job matches
    total_matches = JobMatch.objects.filter(user=user).count()
    new_matches = JobMatch.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    bookmarked_jobs = JobMatch.objects.filter(user=user, is_bookmarked=True).count()
    applied_jobs = JobMatch.objects.filter(user=user, is_applied=True).count()
    
    # Get recent scrape activity
    recent_scrapes = ScrapeLog.objects.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Get total jobs in system
    total_jobs = Job.objects.filter(is_active=True).count()
    
    return Response({
        'total_matches': total_matches,
        'new_matches': new_matches,
        'bookmarked_jobs': bookmarked_jobs,
        'applied_jobs': applied_jobs,
        'recent_scrapes': recent_scrapes,
        'total_jobs': total_jobs,
    })