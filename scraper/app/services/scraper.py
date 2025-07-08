import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse

from ..api.models import JobData

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def scrape_jobs(self, keywords: List[str], location: str = "", max_pages: int = 3) -> List[JobData]:
        """Main scraping method to be implemented by subclasses"""
        raise NotImplementedError
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page"""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_salary(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """Extract salary range from text"""
        if not text:
            return None, None
        
        # Common salary patterns
        patterns = [
            r'\$(\d+(?:,\d+)?(?:k|K)?)\s*-\s*\$(\d+(?:,\d+)?(?:k|K)?)',
            r'\$(\d+(?:,\d+)?(?:k|K)?)',
            r'(\d+(?:,\d+)?(?:k|K)?)\s*-\s*(\d+(?:,\d+)?(?:k|K)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 2:
                        min_sal = self._parse_salary(match.group(1))
                        max_sal = self._parse_salary(match.group(2))
                        return min_sal, max_sal
                    else:
                        salary = self._parse_salary(match.group(1))
                        return salary, salary
                except:
                    continue
        
        return None, None
    
    def _parse_salary(self, salary_str: str) -> Optional[int]:
        """Parse salary string to integer"""
        if not salary_str:
            return None
        
        # Remove commas and convert k/K to thousands
        salary_str = salary_str.replace(',', '')
        if salary_str.lower().endswith('k'):
            return int(salary_str[:-1]) * 1000
        
        return int(salary_str)

class RemoteOKScraper(BaseScraper):
    def __init__(self):
        super().__init__("RemoteOK", "https://remoteok.io")
    
    async def scrape_jobs(self, keywords: List[str], location: str = "", max_pages: int = 3) -> List[JobData]:
        jobs = []
        
        async with self:
            # RemoteOK API endpoint
            api_url = f"{self.base_url}/api"
            
            try:
                response = await self.session.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                # Skip the first item (it's metadata)
                job_listings = data[1:] if len(data) > 1 else []
                
                for job_data in job_listings:
                    # Filter by keywords
                    if keywords and not any(
                        keyword.lower() in (job_data.get('position', '') + ' ' + job_data.get('description', '')).lower()
                        for keyword in keywords
                    ):
                        continue
                    
                    # Extract job information
                    job = JobData(
                        title=job_data.get('position', ''),
                        company=job_data.get('company', ''),
                        location=job_data.get('location', 'Remote'),
                        location_type='remote',
                        job_type='full-time',
                        description=job_data.get('description', ''),
                        requirements='',
                        salary_min=None,
                        salary_max=None,
                        currency='USD',
                        external_id=f"remoteok_{job_data.get('id', '')}",
                        external_url=f"{self.base_url}/job/{job_data.get('id', '')}",
                        tags=job_data.get('tags', []),
                        posted_date=datetime.fromtimestamp(job_data.get('date', 0)) if job_data.get('date') else datetime.now()
                    )
                    
                    jobs.append(job)
                    
                    # Limit results
                    if len(jobs) >= max_pages * 25:  # Approximate pagination
                        break
                
                logger.info(f"RemoteOK: Scraped {len(jobs)} jobs")
                
            except Exception as e:
                logger.error(f"RemoteOK scraping error: {str(e)}")
        
        return jobs

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed", "https://indeed.com")
    
    async def scrape_jobs(self, keywords: List[str], location: str = "", max_pages: int = 3) -> List[JobData]:
        jobs = []
        
        async with self:
            query = " ".join(keywords) if keywords else "developer"
            
            for page in range(max_pages):
                start = page * 10
                search_url = f"{self.base_url}/jobs?q={query}&l={location}&start={start}"
                
                html = await self.fetch_page(search_url)
                if not html:
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        # Extract job details
                        title_elem = card.find('h2', class_='jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        company_elem = card.find('span', class_='companyName')
                        company = company_elem.get_text(strip=True) if company_elem else ''
                        
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else ''
                        
                        # Get job link
                        link_elem = title_elem.find('a') if title_elem else None
                        job_link = urljoin(self.base_url, link_elem.get('href')) if link_elem else ''
                        
                        # Extract salary if available
                        salary_elem = card.find('span', class_='salaryText')
                        salary_text = salary_elem.get_text(strip=True) if salary_elem else ''
                        salary_min, salary_max = self.extract_salary(salary_text)
                        
                        # Get job description snippet
                        desc_elem = card.find('div', class_='summary')
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        job = JobData(
                            title=title,
                            company=company,
                            location=job_location,
                            location_type='onsite',  # Indeed doesn't clearly specify
                            job_type='full-time',
                            description=description,
                            requirements='',
                            salary_min=salary_min,
                            salary_max=salary_max,
                            currency='USD',
                            external_id=f"indeed_{hash(job_link)}",
                            external_url=job_link,
                            tags=[],
                            posted_date=datetime.now()
                        )
                        
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing Indeed job card: {str(e)}")
                        continue
                
                # Add delay between requests
                await asyncio.sleep(1)
        
        logger.info(f"Indeed: Scraped {len(jobs)} jobs")
        return jobs

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn", "https://linkedin.com")
    
    async def scrape_jobs(self, keywords: List[str], location: str = "", max_pages: int = 3) -> List[JobData]:
        jobs = []
        
        async with self:
            # LinkedIn requires more sophisticated handling
            # This is a simplified version
            query = " ".join(keywords) if keywords else "developer"
            
            for page in range(max_pages):
                start = page * 25
                search_url = f"{self.base_url}/jobs/search?keywords={query}&location={location}&start={start}"
                
                html = await self.fetch_page(search_url)
                if not html:
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # LinkedIn has different selectors and may require authentication
                # This is a placeholder implementation
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        company_elem = card.find('a', class_='hidden-nested-link')
                        company = company_elem.get_text(strip=True) if company_elem else ''
                        
                        location_elem = card.find('span', class_='job-search-card__location')
                        job_location = location_elem.get_text(strip=True) if location_elem else ''
                        
                        # Get job link
                        link_elem = card.find('a', class_='base-card__full-link')
                        job_link = link_elem.get('href') if link_elem else ''
                        
                        job = JobData(
                            title=title,
                            company=company,
                            location=job_location,
                            location_type='onsite',
                            job_type='full-time',
                            description='',
                            requirements='',
                            salary_min=None,
                            salary_max=None,
                            currency='USD',
                            external_id=f"linkedin_{hash(job_link)}",
                            external_url=job_link,
                            tags=[],
                            posted_date=datetime.now()
                        )
                        
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing LinkedIn job card: {str(e)}")
                        continue
                
                # Add delay between requests
                await asyncio.sleep(2)
        
        logger.info(f"LinkedIn: Scraped {len(jobs)} jobs")
        return jobs