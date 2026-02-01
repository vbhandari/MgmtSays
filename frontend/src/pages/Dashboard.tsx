import { Link } from 'react-router-dom';
import {
  BuildingOfficeIcon,
  DocumentTextIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { Card, CardHeader, InlineLoading, Alert } from '../components/ui';
import { useCompanies } from '../hooks';

export default function Dashboard() {
  const { data: companies, isLoading, error } = useCompanies();

  if (isLoading) {
    return <InlineLoading message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <Alert type="error" title="Error loading dashboard">
        Failed to load dashboard data. Please try again.
      </Alert>
    );
  }

  const stats = [
    {
      name: 'Companies',
      value: companies?.length || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-blue-500',
      href: '/companies',
    },
    {
      name: 'Documents',
      value: companies?.reduce((acc, c) => acc + (c.metadata?.document_count as number || 0), 0) || 0,
      icon: DocumentTextIcon,
      color: 'bg-green-500',
      href: '/companies',
    },
    {
      name: 'Initiatives',
      value: '-',
      icon: ArrowTrendingUpIcon,
      color: 'bg-purple-500',
      href: '/companies',
    },
    {
      name: 'Insights',
      value: '-',
      icon: LightBulbIcon,
      color: 'bg-orange-500',
      href: '/companies',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold">Welcome to MgmtSays</h2>
        <p className="mt-2 text-blue-100">
          Extract strategic insights from management disclosures using AI-powered analysis.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Link key={stat.name} to={stat.href}>
            <Card hover className="flex items-center">
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {/* Recent companies */}
      <Card>
        <CardHeader
          title="Recent Companies"
          subtitle="Companies you've been working with"
          action={
            <Link
              to="/companies"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View all
            </Link>
          }
        />
        {companies && companies.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {companies.slice(0, 5).map((company) => (
              <Link
                key={company.id}
                to={`/companies/${company.id}`}
                className="block py-3 hover:bg-gray-50 -mx-6 px-6 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{company.name}</p>
                    <p className="text-sm text-gray-500">
                      {company.ticker && <span className="mr-2">{company.ticker}</span>}
                      {company.industry}
                    </p>
                  </div>
                  <span className="text-sm text-gray-400">
                    {new Date(company.created_at).toLocaleDateString()}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No companies yet.</p>
            <Link to="/companies" className="text-blue-600 hover:underline mt-2 inline-block">
              Add your first company
            </Link>
          </div>
        )}
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/companies">
          <Card hover className="text-center">
            <BuildingOfficeIcon className="h-8 w-8 mx-auto text-blue-600" />
            <h3 className="mt-2 font-medium text-gray-900">Add Company</h3>
            <p className="text-sm text-gray-500">Track a new company's disclosures</p>
          </Card>
        </Link>
        <Link to="/search">
          <Card hover className="text-center">
            <DocumentTextIcon className="h-8 w-8 mx-auto text-green-600" />
            <h3 className="mt-2 font-medium text-gray-900">Search Disclosures</h3>
            <p className="text-sm text-gray-500">Find information across documents</p>
          </Card>
        </Link>
        <Link to="/search">
          <Card hover className="text-center">
            <LightBulbIcon className="h-8 w-8 mx-auto text-orange-600" />
            <h3 className="mt-2 font-medium text-gray-900">Ask Questions</h3>
            <p className="text-sm text-gray-500">Get AI-powered answers</p>
          </Card>
        </Link>
      </div>
    </div>
  );
}
