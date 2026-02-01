import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  BuildingOfficeIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Companies', href: '/companies', icon: BuildingOfficeIcon },
  { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <DocumentTextIcon className="h-8 w-8 text-blue-600" />
        <span className="ml-2 text-xl font-bold text-gray-900">MgmtSays</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="h-5 w-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p>MgmtSays v1.0.0</p>
          <p className="mt-1">Management Disclosure Intelligence</p>
        </div>
      </div>
    </aside>
  );
}
