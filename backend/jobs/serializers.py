from rest_framework import serializers
from .models import Job, JobMatch, JobBoard, ScrapeLog

class JobBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobBoard
        fields = ['id', 'name', 'base_url', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class JobSerializer(serializers.ModelSerializer):
    job_board_name = serializers.CharField(source='job_board.name', read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'location_type', 'job_type',
            'description', 'requirements', 'salary_min', 'salary_max', 'currency',
            'external_url', 'job_board_name', 'tags', 'posted_date', 'scraped_at'
        ]
        read_only_fields = ['id', 'scraped_at', 'job_board_name']

class JobMatchSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_preference_keywords = serializers.CharField(source='job_preference.keywords', read_only=True)
    
    class Meta:
        model = JobMatch
        fields = [
            'id', 'job', 'job_preference_keywords', 'match_score',
            'is_viewed', 'is_bookmarked', 'is_applied', 'created_at'
        ]
        read_only_fields = ['id', 'job', 'job_preference_keywords', 'match_score', 'created_at']

class ScrapeLogSerializer(serializers.ModelSerializer):
    job_board_name = serializers.CharField(source='job_board.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = ScrapeLog
        fields = [
            'id', 'job_board_name', 'status', 'jobs_scraped', 'jobs_created',
            'jobs_updated', 'error_message', 'started_at', 'completed_at',
            'duration_seconds'
        ]
        read_only_fields = ['id']

    def get_duration_seconds(self, obj):
        if obj.duration:
            return obj.duration.total_seconds()
        return None