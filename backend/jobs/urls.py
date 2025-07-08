from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('matches/', views.JobMatchListView.as_view(), name='job_matches'),
    path('matches/<int:pk>/', views.JobMatchDetailView.as_view(), name='job_match_detail'),
    path('<int:job_id>/bookmark/', views.bookmark_job, name='bookmark_job'),
    path('<int:job_id>/apply/', views.mark_applied, name='mark_applied'),
    path('boards/', views.JobBoardListView.as_view(), name='job_boards'),
    path('scrape-logs/', views.ScrapeLogListView.as_view(), name='scrape_logs'),
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
]