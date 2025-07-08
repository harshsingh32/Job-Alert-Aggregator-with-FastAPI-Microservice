from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from .models import JobData, ScrapeRequest, ScrapeResult
from ..services.scraper import RemoteOKScraper, IndeedScraper, LinkedInScraper

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize scrapers
scrapers = {
    'remoteok': RemoteOKScraper(),
    'indeed': IndeedScraper(),
    'linkedin': LinkedInScraper(),
}

@router.get("/scrapers")
async def get_scrapers():
    return {
        "scrapers": [
            {"name": name, "base_url": scraper.base_url}
            for name, scraper in scrapers.items()
        ]
    }

@router.post("/scrape/{scraper_name}")
async def scrape_jobs(
    scraper_name: str,
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
) -> dict:
    if scraper_name not in scrapers:
        raise HTTPException(
            status_code=404,
            detail=f"Scraper '{scraper_name}' not found"
        )
    
    scraper = scrapers[scraper_name]
    
    # Run scraping
    try:
        jobs = await scraper.scrape_jobs(
            keywords=request.keywords,
            location=request.location,
            max_pages=request.max_pages
        )
        
        return {
            "jobs_scraped": len(jobs),
            "jobs_created": len(jobs),
            "jobs_updated": 0,
            "status": "completed",
            "scraper_name": scraper_name,
            "jobs": [job.dict() for job in jobs]
        }
    
    except Exception as e:
        logger.error(f"Scraping error for {scraper_name}: {str(e)}")
        return {
            "jobs_scraped": 0,
            "jobs_created": 0,
            "jobs_updated": 0,
            "status": "failed",
            "error": str(e),
            "scraper_name": scraper_name
        }

@router.post("/scrape/batch")
async def scrape_batch(request: ScrapeRequest) -> dict:
    results = {}
    
    for scraper_name, scraper in scrapers.items():
        try:
            jobs = await scraper.scrape_jobs(
                keywords=request.keywords,
                location=request.location,
                max_pages=request.max_pages
            )
            
            results[scraper_name] = {
                "jobs_scraped": len(jobs),
                "jobs_created": len(jobs),
                "jobs_updated": 0,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Batch scraping error for {scraper_name}: {str(e)}")
            results[scraper_name] = {
                "jobs_scraped": 0,
                "jobs_created": 0,
                "jobs_updated": 0,
                "status": "failed",
                "error": str(e)
            }
    
    return {
        "message": "Batch scraping completed",
        "results": results
    }