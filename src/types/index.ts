export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_email_verified: boolean;
  created_at: string;
}

export interface JobPreference {
  id: number;
  keywords: string;
  location_type: 'remote' | 'onsite' | 'hybrid';
  desired_location: string;
  experience_level: 'entry' | 'mid' | 'senior' | 'lead';
  min_salary?: number;
  max_salary?: number;
  job_type: string;
  is_active: boolean;
  email_notifications: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  location_type: 'remote' | 'onsite' | 'hybrid';
  job_type: string;
  description: string;
  requirements: string;
  salary_min?: number;
  salary_max?: number;
  currency: string;
  external_url: string;
  job_board_name: string;
  tags: string[];
  posted_date: string;
  scraped_at: string;
}

export interface JobMatch {
  id: number;
  job: Job;
  job_preference_keywords: string;
  match_score: number;
  is_viewed: boolean;
  is_bookmarked: boolean;
  is_applied: boolean;
  created_at: string;
}

export interface DashboardStats {
  total_matches: number;
  new_matches: number;
  bookmarked_jobs: number;
  applied_jobs: number;
  recent_scrapes: number;
  total_jobs: number;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: User;
}