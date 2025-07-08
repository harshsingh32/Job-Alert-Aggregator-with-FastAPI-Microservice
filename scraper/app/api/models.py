from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobData(BaseModel):
    title: str
    company: str
    location: str
    location_type: str = Field(default="remote", description="remote, onsite, or hybrid")
    job_type: str = Field(default="full-time", description="full-time, part-time, contract, etc.")
    description: str
    requirements: str = ""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    external_id: str
    external_url: str
    tags: List[str] = []
    posted_date: datetime = Field(default_factory=datetime.now)

class ScrapeRequest(BaseModel):
    keywords: List[str] = Field(default=[], description="Keywords to search for")
    location: str = Field(default="", description="Location to search in")
    max_pages: int = Field(default=3, description="Maximum number of pages to scrape")
    job_board_config: Dict[str, Any] = Field(default={}, description="Job board specific configuration")

class ScrapeResult(BaseModel):
    jobs_scraped: int
    jobs_created: int
    jobs_updated: int
    status: str
    error: Optional[str] = None
    duration: Optional[float] = None
    scraper_name: str
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"