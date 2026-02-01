import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  DocumentTextIcon,
  ArrowUpTrayIcon,
  ChartBarIcon,
  ClockIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';
import { Card, CardHeader, Button, Badge, InlineLoading, Alert, EmptyState } from '../components/ui';
import { useCompany, useCompanyStats, useCompanyDocuments, useCompanyInitiatives } from '../hooks';

export default function CompanyDetail() {
  const { companyId } = useParams<{ companyId: string }>();
  const navigate = useNavigate();

  const { data: company, isLoading: companyLoading } = useCompany(companyId!);
  const { data: stats } = useCompanyStats(companyId!);
  const { data: documents } = useCompanyDocuments(companyId!);
  const { data: initiatives } = useCompanyInitiatives(companyId!);

  if (companyLoading) {
    return <InlineLoading message="Loading company details..." />;
  }

  if (!company) {
    return (
      <Alert type="error" title="Company not found">
        The requested company could not be found.
      </Alert>
    );
  }

  const documentTypeLabels: Record<string, string> = {
    earnings_call: 'Earnings Call',
    annual_report: 'Annual Report',
    quarterly_report: 'Quarterly Report',
    investor_presentation: 'Investor Presentation',
    press_release: 'Press Release',
    sec_filing: 'SEC Filing',
    other: 'Other',
  };

  const statusColors: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
    pending: 'default',
  };

  return (
    <div className="space-y-6">
      {/* Back button and header */}
      <div>
        <button
          onClick={() => navigate('/companies')}
          className="flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to companies
        </button>
        
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{company.name}</h1>
              {company.ticker && (
                <Badge variant="primary">{company.ticker}</Badge>
              )}
            </div>
            {company.industry && (
              <p className="text-gray-500 mt-1">{company.industry}</p>
            )}
            {company.description && (
              <p className="text-gray-600 mt-2 max-w-2xl">{company.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Link to={`/companies/${companyId}/upload`}>
              <Button leftIcon={<ArrowUpTrayIcon className="h-5 w-5" />}>
                Upload Document
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Documents</p>
              <p className="text-2xl font-semibold">{stats?.document_count || 0}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Initiatives</p>
              <p className="text-2xl font-semibold">{stats?.initiative_count || 0}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Insights</p>
              <p className="text-2xl font-semibold">{stats?.insight_count || 0}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="text-sm font-medium">
                {stats?.last_updated
                  ? new Date(stats.last_updated).toLocaleDateString()
                  : 'Never'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to={`/companies/${companyId}/analysis`}>
          <Card hover className="text-center py-8">
            <ChartBarIcon className="h-10 w-10 mx-auto text-blue-600" />
            <h3 className="mt-3 font-semibold text-gray-900">Run Analysis</h3>
            <p className="text-sm text-gray-500">Extract insights from documents</p>
          </Card>
        </Link>
        <Link to={`/companies/${companyId}/timeline`}>
          <Card hover className="text-center py-8">
            <ClockIcon className="h-10 w-10 mx-auto text-purple-600" />
            <h3 className="mt-3 font-semibold text-gray-900">View Timeline</h3>
            <p className="text-sm text-gray-500">Track initiatives over time</p>
          </Card>
        </Link>
        <Link to={`/search?company=${companyId}`}>
          <Card hover className="text-center py-8">
            <DocumentTextIcon className="h-10 w-10 mx-auto text-green-600" />
            <h3 className="mt-3 font-semibold text-gray-900">Search Documents</h3>
            <p className="text-sm text-gray-500">Find specific information</p>
          </Card>
        </Link>
      </div>

      {/* Documents */}
      <Card>
        <CardHeader
          title="Documents"
          subtitle={`${documents?.length || 0} documents`}
          action={
            <Link to={`/companies/${companyId}/upload`}>
              <Button variant="outline" size="sm">
                Upload
              </Button>
            </Link>
          }
        />
        {documents && documents.length > 0 ? (
          <div className="divide-y divide-gray-200 -mx-6">
            {documents.map((doc) => (
              <div key={doc.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{doc.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="default" size="sm">
                        {documentTypeLabels[doc.document_type] || doc.document_type}
                      </Badge>
                      <Badge variant={statusColors[doc.processing_status]} size="sm">
                        {doc.processing_status}
                      </Badge>
                      {doc.fiscal_period && doc.fiscal_year && (
                        <span className="text-sm text-gray-500">
                          {doc.fiscal_period} {doc.fiscal_year}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-sm text-gray-400">
                    {doc.publish_date
                      ? new Date(doc.publish_date).toLocaleDateString()
                      : new Date(doc.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No documents yet"
            description="Upload your first document to start analyzing"
            action={
              <Link to={`/companies/${companyId}/upload`}>
                <Button>Upload Document</Button>
              </Link>
            }
          />
        )}
      </Card>

      {/* Initiatives */}
      <Card>
        <CardHeader
          title="Strategic Initiatives"
          subtitle={`${initiatives?.length || 0} initiatives identified`}
          action={
            <Link to={`/companies/${companyId}/timeline`}>
              <Button variant="outline" size="sm">
                View Timeline
              </Button>
            </Link>
          }
        />
        {initiatives && initiatives.length > 0 ? (
          <div className="space-y-3">
            {initiatives.slice(0, 5).map((initiative) => (
              <div
                key={initiative.id}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{initiative.name}</h4>
                    {initiative.description && (
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {initiative.description}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="info" size="sm">
                        {initiative.category}
                      </Badge>
                      <Badge
                        variant={initiative.status === 'active' ? 'success' : 'default'}
                        size="sm"
                      >
                        {initiative.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <p>{initiative.mention_count} mentions</p>
                    {initiative.first_mentioned_date && (
                      <p className="text-xs">
                        First: {new Date(initiative.first_mentioned_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No initiatives yet"
            description="Run analysis on documents to extract strategic initiatives"
            action={
              <Link to={`/companies/${companyId}/analysis`}>
                <Button>Run Analysis</Button>
              </Link>
            }
          />
        )}
      </Card>
    </div>
  );
}
