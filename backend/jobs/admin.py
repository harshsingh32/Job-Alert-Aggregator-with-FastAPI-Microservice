from django.contrib import admin
from .models import Job, JobBoard, JobMatch, ScrapeLog, EmailNotification

@admin.register(JobBoard)
class JobBoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'base_url']
    ordering = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location_type', 'job_type', 'job_board', 'posted_date', 'is_active']
    list_filter = ['location_type', 'job_type', 'job_board', 'is_active', 'posted_date']
    search_fields = ['title', 'company', 'location']
    ordering = ['-posted_date']
    readonly_fields = ['external_id', 'scraped_at']

@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'match_score', 'is_viewed', 'is_bookmarked', 'is_applied', 'created_at']
    list_filter = ['is_viewed', 'is_bookmarked', 'is_applied', 'created_at']
    search_fields = ['user__email', 'job__title', 'job__company']
    ordering = ['-created_at']

@admin.register(ScrapeLog)
class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = ['job_board', 'status', 'jobs_scraped', 'jobs_created', 'jobs_updated', 'started_at', 'completed_at']
    list_filter = ['status', 'job_board', 'started_at']
    search_fields = ['job_board__name']
    ordering = ['-started_at']
    readonly_fields = ['duration']

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'sent_at', 'is_sent']
    list_filter = ['is_sent', 'sent_at']
    search_fields = ['user__email', 'subject']
    ordering = ['-sent_at']