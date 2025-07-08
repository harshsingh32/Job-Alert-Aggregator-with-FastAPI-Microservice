from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobPreference

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_email_verified', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_email_verified']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_email_verified', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(JobPreference)
class JobPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'keywords', 'location_type', 'experience_level', 'is_active', 'email_notifications', 'created_at']
    list_filter = ['location_type', 'experience_level', 'is_active', 'email_notifications']
    search_fields = ['user__email', 'keywords']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'keywords', 'is_active')
        }),
        ('Job Criteria', {
            'fields': ('location_type', 'desired_location', 'experience_level', 'job_type')
        }),
        ('Salary', {
            'fields': ('min_salary', 'max_salary')
        }),
        ('Notifications', {
            'fields': ('email_notifications',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']