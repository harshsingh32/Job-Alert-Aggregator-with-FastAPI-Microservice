import React, { useState, useEffect } from 'react';
import { jobsAPI } from '../services/api';
import { DashboardStats } from '../types';
import { 
  TrendingUp, 
  Briefcase, 
  BookmarkIcon, 
  CheckCircle, 
  Activity,
  Database
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await jobsAPI.getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Matches',
      value: stats?.total_matches || 0,
      icon: Briefcase,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      title: 'New This Week',
      value: stats?.new_matches || 0,
      icon: TrendingUp,
      color: 'bg-green-500',
      change: '+23%',
    },
    {
      title: 'Bookmarked',
      value: stats?.bookmarked_jobs || 0,
      icon: BookmarkIcon,
      color: 'bg-yellow-500',
      change: '+5%',
    },
    {
      title: 'Applied',
      value: stats?.applied_jobs || 0,
      icon: CheckCircle,
      color: 'bg-purple-500',
      change: '+8%',
    },
    {
      title: 'Recent Scrapes',
      value: stats?.recent_scrapes || 0,
      icon: Activity,
      color: 'bg-indigo-500',
      change: '+15%',
    },
    {
      title: 'Total Jobs',
      value: stats?.total_jobs || 0,
      icon: Database,
      color: 'bg-gray-500',
      change: '+45%',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's your job search overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-1">{stat.change} from last week</p>
                </div>
                <div className={`${stat.color} p-3 rounded-full`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">New job matches found for "Python Developer"</span>
              <span className="text-xs text-gray-400">2 hours ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Scraping completed for RemoteOK</span>
              <span className="text-xs text-gray-400">4 hours ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Job preference updated</span>
              <span className="text-xs text-gray-400">1 day ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Email notification sent</span>
              <span className="text-xs text-gray-400">2 days ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center px-4 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
              <Search className="h-4 w-4 mr-2" />
              Browse Jobs
            </button>
            <button className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
              <Settings className="h-4 w-4 mr-2" />
              Update Preferences
            </button>
            <button className="flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
              <Briefcase className="h-4 w-4 mr-2" />
              View Matches
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;