import React, { useState, useEffect } from 'react';
import { jobsAPI } from '../services/api';
import { Job } from '../types';
import { 
  MapPin, 
  Clock, 
  DollarSign, 
  ExternalLink, 
  BookmarkIcon,
  Search,
  Filter
} from 'lucide-react';

const JobList: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    location_type: '',
    job_type: '',
    days_ago: '',
  });

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = {
        search: searchTerm,
        ...filters,
        days_ago: filters.days_ago ? parseInt(filters.days_ago) : undefined,
      };
      const data = await jobsAPI.getJobs(params);
      setJobs(data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs();
  };

  const handleBookmark = async (jobId: number) => {
    try {
      await jobsAPI.bookmarkJob(jobId);
      // Refresh jobs to update bookmark status
      fetchJobs();
    } catch (error) {
      console.error('Error bookmarking job:', error);
    }
  };

  const formatSalary = (min?: number, max?: number, currency = 'USD') => {
    if (!min && !max) return null;
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
    
    if (min && max) {
      return `${formatter.format(min)} - ${formatter.format(max)}`;
    }
    return formatter.format(min || max || 0);
  };

  const getLocationTypeColor = (type: string) => {
    switch (type) {
      case 'remote': return 'bg-green-100 text-green-800';
      case 'hybrid': return 'bg-yellow-100 text-yellow-800';
      case 'onsite': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">Browse Jobs</h1>
        <p className="text-gray-600 mt-1">Discover your next opportunity</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search jobs, companies, or keywords..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              Search
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <select
              value={filters.location_type}
              onChange={(e) => setFilters({ ...filters, location_type: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Locations</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
            </select>

            <select
              value={filters.job_type}
              onChange={(e) => setFilters({ ...filters, job_type: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Types</option>
              <option value="full-time">Full-time</option>
              <option value="part-time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="freelance">Freelance</option>
              <option value="internship">Internship</option>
            </select>

            <select
              value={filters.days_ago}
              onChange={(e) => setFilters({ ...filters, days_ago: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Any time</option>
              <option value="1">Last 24 hours</option>
              <option value="7">Last week</option>
              <option value="30">Last month</option>
            </select>
          </div>
        </form>
      </div>

      {/* Job Results */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <Search className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your search criteria</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLocationTypeColor(job.location_type)}`}>
                        {job.location_type}
                      </span>
                    </div>
                    
                    <p className="text-indigo-600 font-medium mb-2">{job.company}</p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {job.location}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {new Date(job.posted_date).toLocaleDateString()}
                      </div>
                      {formatSalary(job.salary_min, job.salary_max, job.currency) && (
                        <div className="flex items-center">
                          <DollarSign className="h-4 w-4 mr-1" />
                          {formatSalary(job.salary_min, job.salary_max, job.currency)}
                        </div>
                      )}
                    </div>
                    
                    <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                      {job.description.substring(0, 200)}...
                    </p>
                    
                    {job.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {job.tags.slice(0, 5).map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col space-y-2 ml-4">
                    <button
                      onClick={() => handleBookmark(job.id)}
                      className="p-2 text-gray-400 hover:text-yellow-500 hover:bg-gray-50 rounded-full transition-colors"
                    >
                      <BookmarkIcon className="h-5 w-5" />
                    </button>
                    
                    <a
                      href={job.external_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Apply
                    </a>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                  <span>Source: {job.job_board_name}</span>
                  <span>Scraped: {new Date(job.scraped_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default JobList;