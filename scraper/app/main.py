from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import logging
from datetime import datetime
import asyncio

from .services.scraper import RemoteOKScraper, IndeedScraper, LinkedInScraper
from .api.models import JobData, ScrapeResult, ScrapeRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Scraper API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scrapers
scrapers = {
    'remoteok': RemoteOKScraper(),
    'indeed': IndeedScraper(),
    'linkedin': LinkedInScraper(),
}

@app.get("/")
async def root():
    return {"message": "Job Scraper API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/scrapers")
async def get_available_scrapers():
    return {
        "scrapers": list(scrapers.keys()),
        "count": len(scrapers)
    }

@app.post("/scrape/{scraper_name}")
async def scrape_jobs(
    scraper_name: str,
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    if scraper_name not in scrapers:
        raise HTTPException(
            status_code=404,
            detail=f"Scraper '{scraper_name}' not found. Available scrapers: {list(scrapers.keys())}"
        )
    
    scraper = scrapers[scraper_name]
    
    try:
        # Run scraping in background
        background_tasks.add_task(
            run_scraper,
            scraper,
            request.keywords,
            request.location,
            request.max_pages
        )
        
        return {
            "message": f"Scraping started for {scraper_name}",
            "scraper": scraper_name,
            "keywords": request.keywords,
            "location": request.location,
            "max_pages": request.max_pages
        }
    
    except Exception as e:
        logger.error(f"Error initiating scraping for {scraper_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_scraper(scraper, keywords: List[str], location: str, max_pages: int):
    """Run scraper in background"""
    try:
        jobs = await scraper.scrape_jobs(keywords, location, max_pages)
        
        # Here you would typically save to database
        # For now, we'll just log the results
        logger.info(f"Scraped {len(jobs)} jobs successfully")
        
        return {
            "jobs_scraped": len(jobs),
            "jobs_created": len(jobs),  # Placeholder
            "jobs_updated": 0,  # Placeholder
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error in scraper: {str(e)}")
        return {
            "jobs_scraped": 0,
            "jobs_created": 0,
            "jobs_updated": 0,
            "status": "failed",
            "error": str(e)
        }

@app.post("/scrape/batch")
async def scrape_multiple_sources(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """Scrape jobs from multiple sources"""
    results = {}
    
    for scraper_name, scraper in scrapers.items():
        try:
            background_tasks.add_task(
                run_scraper,
                scraper,
                request.keywords,
                request.location,
                request.max_pages
            )
            results[scraper_name] = "started"
        except Exception as e:
            results[scraper_name] = f"failed: {str(e)}"
    
    return {
        "message": "Batch scraping initiated",
        "results": results,
        "keywords": request.keywords,
        "location": request.location
    }

@app.get("/jobs/test")
async def test_scraper():
    """Test endpoint to verify scraper functionality"""
    try:
        scraper = scrapers['remoteok']
        jobs = await scraper.scrape_jobs(['python', 'developer'], 'remote', 1)
        
        return {
            "status": "success",
            "jobs_found": len(jobs),
            "sample_job": jobs[0] if jobs else None
        }
    except Exception as e:
        logger.error(f"Test scraper error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)