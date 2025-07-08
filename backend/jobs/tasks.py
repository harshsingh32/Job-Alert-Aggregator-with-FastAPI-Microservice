from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import requests
import logging

from .models import Job, JobBoard, JobMatch, ScrapeLog, EmailNotification
from users.models import User, JobPreference

logger = logging.getLogger(__name__)

@shared_task
def scrape_all_jobs():
    """Scrape jobs from all active job boards"""
    job_boards = JobBoard.objects.filter(is_active=True)
    
    for job_board in job_boards:
        scrape_job_board.delay(job_board.id)
    
    logger.info(f"Initiated scraping for {job_boards.count()} job boards")

@shared_task
def scrape_job_board(job_board_id):
    """Scrape jobs from a specific job board"""
    try:
        job_board = JobBoard.objects.get(id=job_board_id)
        
        # Create scrape log
        scrape_log = ScrapeLog.objects.create(
            job_board=job_board,
            status='started'
        )
        
        # Call FastAPI scraper service
        response = requests.post(
            f"{settings.SCRAPER_SERVICE_URL}/scrape/{job_board.name.lower()}",
            json=job_board.scraper_config,
            timeout=300
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Update scrape log
            scrape_log.status = 'completed'
            scrape_log.jobs_scraped = data.get('jobs_scraped', 0)
            scrape_log.jobs_created = data.get('jobs_created', 0)
            scrape_log.jobs_updated = data.get('jobs_updated', 0)
            scrape_log.completed_at = timezone.now()
            scrape_log.duration = scrape_log.completed_at - scrape_log.started_at
            scrape_log.save()
            
            # Trigger job matching for new jobs
            match_new_jobs.delay(job_board_id)
            
            logger.info(f"Successfully scraped {data.get('jobs_scraped', 0)} jobs from {job_board.name}")
        else:
            scrape_log.status = 'failed'
            scrape_log.error_message = f"HTTP {response.status_code}: {response.text}"
            scrape_log.completed_at = timezone.now()
            scrape_log.duration = scrape_log.completed_at - scrape_log.started_at
            scrape_log.save()
            
            logger.error(f"Failed to scrape {job_board.name}: {response.text}")
            
    except JobBoard.DoesNotExist:
        logger.error(f"Job board with id {job_board_id} not found")
    except Exception as e:
        logger.error(f"Error scraping job board {job_board_id}: {str(e)}")
        
        # Update scrape log if it exists
        try:
            scrape_log.status = 'failed'
            scrape_log.error_message = str(e)
            scrape_log.completed_at = timezone.now()
            scrape_log.duration = scrape_log.completed_at - scrape_log.started_at
            scrape_log.save()
        except:
            pass

@shared_task
def match_new_jobs(job_board_id):
    """Match new jobs with user preferences"""
    try:
        job_board = JobBoard.objects.get(id=job_board_id)
        
        # Get jobs from the last scrape
        recent_jobs = Job.objects.filter(
            job_board=job_board,
            scraped_at__gte=timezone.now() - timedelta(hours=2),
            is_active=True
        )
        
        # Get all active job preferences
        preferences = JobPreference.objects.filter(is_active=True)
        
        matches_created = 0
        
        for preference in preferences:
            keywords = preference.get_keywords_list()
            
            for job in recent_jobs:
                # Check if match already exists
                if JobMatch.objects.filter(user=preference.user, job=job).exists():
                    continue
                
                # Calculate match score
                match_score = calculate_match_score(job, preference, keywords)
                
                if match_score > 0.3:  # Minimum threshold for matching
                    JobMatch.objects.create(
                        user=preference.user,
                        job=job,
                        job_preference=preference,
                        match_score=match_score
                    )
                    matches_created += 1
        
        logger.info(f"Created {matches_created} new job matches for {job_board.name}")
        
    except JobBoard.DoesNotExist:
        logger.error(f"Job board with id {job_board_id} not found")
    except Exception as e:
        logger.error(f"Error matching jobs for job board {job_board_id}: {str(e)}")

def calculate_match_score(job, preference, keywords):
    """Calculate match score between job and user preference"""
    score = 0.0
    
    # Check keywords in title (weight: 0.4)
    title_matches = sum(1 for keyword in keywords 
                       if keyword.lower() in job.title.lower())
    score += (title_matches / len(keywords)) * 0.4
    
    # Check keywords in description (weight: 0.3)
    description_matches = sum(1 for keyword in keywords 
                            if keyword.lower() in job.description.lower())
    score += (description_matches / len(keywords)) * 0.3
    
    # Check location type match (weight: 0.2)
    if job.location_type == preference.location_type:
        score += 0.2
    
    # Check job type match (weight: 0.1)
    if job.job_type == preference.job_type:
        score += 0.1
    
    return min(score, 1.0)

@shared_task
def send_job_alerts():
    """Send email alerts for new job matches"""
    preferences = JobPreference.objects.filter(
        is_active=True,
        email_notifications=True
    )
    
    for preference in preferences:
        # Get unviewed matches from the last 24 hours
        new_matches = JobMatch.objects.filter(
            user=preference.user,
            is_viewed=False,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).select_related('job')
        
        if new_matches.exists():
            send_job_alert_email.delay(preference.user.id, list(new_matches.values_list('id', flat=True)))

@shared_task
def send_job_alert_email(user_id, match_ids):
    """Send job alert email to user"""
    try:
        user = User.objects.get(id=user_id)
        matches = JobMatch.objects.filter(id__in=match_ids).select_related('job')
        
        if not matches.exists():
            return
        
        subject = f"🚨 {matches.count()} New Job Alert{'s' if matches.count() > 1 else ''}"
        
        # Create email notification record
        email_notification = EmailNotification.objects.create(
            user=user,
            subject=subject
        )
        email_notification.job_matches.set(matches)
        
        try:
            # Send email
            send_mail(
                subject=subject,
                message=f"You have {matches.count()} new job matches. Check your dashboard for details.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            email_notification.is_sent = True
            email_notification.save()
            
            logger.info(f"Sent job alert email to {user.email} for {matches.count()} matches")
            
        except Exception as e:
            email_notification.error_message = str(e)
            email_notification.save()
            logger.error(f"Failed to send job alert email to {user.email}: {str(e)}")
            
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
    except Exception as e:
        logger.error(f"Error sending job alert email: {str(e)}")