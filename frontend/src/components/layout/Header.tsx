import { useLocation } from 'react-router-dom';
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/companies': 'Companies',
  '/search': 'Search',
  '/settings': 'Settings',
};

export default function Header() {
  const location = useLocation();
  
  // Get title, handling dynamic routes
  const getTitle = () => {
    const path = location.pathname;
    
    if (pageTitles[path]) {
      return pageTitles[path];
    }
    
    if (path.includes('/companies/') && path.includes('/upload')) {
      return 'Upload Documents';
    }
    if (path.includes('/companies/') && path.includes('/analysis')) {
      return 'Analysis';
    }
    if (path.includes('/companies/') && path.includes('/timeline')) {
      return 'Initiative Timeline';
    }
    if (path.includes('/companies/')) {
      return 'Company Details';
    }
    
    return 'MgmtSays';
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <h1 className="text-xl font-semibold text-gray-900">{getTitle()}</h1>
      
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <BellIcon className="h-5 w-5" />
        </button>
        
        {/* User menu */}
        <button className="flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <UserCircleIcon className="h-6 w-6" />
          <span className="text-sm font-medium">User</span>
        </button>
      </div>
    </header>
  );
}
