import { useParams, Link } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { Card, Badge, InlineLoading, EmptyState } from '../components/ui';
import { useCompany, useCompanyInitiatives } from '../hooks';

export default function Timeline() {
  const { companyId } = useParams<{ companyId: string }>();
  
  const { data: company } = useCompany(companyId!);
  const { data: initiatives, isLoading } = useCompanyInitiatives(companyId!);

  if (isLoading) {
    return <InlineLoading message="Loading timeline..." />;
  }

  // Group initiatives by first mention date
  const timelineData = initiatives
    ?.filter((i) => i.first_mentioned_date)
    .sort((a, b) => 
      new Date(b.first_mentioned_date!).getTime() - new Date(a.first_mentioned_date!).getTime()
    ) || [];

  // Group by quarter/year
  const groupedByPeriod: Record<string, typeof timelineData> = {};
  timelineData.forEach((initiative) => {
    const date = new Date(initiative.first_mentioned_date!);
    const quarter = Math.ceil((date.getMonth() + 1) / 3);
    const key = `Q${quarter} ${date.getFullYear()}`;
    
    if (!groupedByPeriod[key]) {
      groupedByPeriod[key] = [];
    }
    groupedByPeriod[key].push(initiative);
  });

  const categoryColors: Record<string, string> = {
    strategy: 'bg-blue-500',
    product: 'bg-green-500',
    market: 'bg-yellow-500',
    operational: 'bg-purple-500',
    financial: 'bg-red-500',
    technology: 'bg-indigo-500',
  };

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        to={`/companies/${companyId}`}
        className="flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeftIcon className="h-4 w-4 mr-1" />
        Back to {company?.name || 'company'}
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Initiative Timeline</h1>
        <p className="text-gray-500 mt-1">
          Track strategic initiatives over time
        </p>
      </div>

      {/* Category legend */}
      <Card padding="sm">
        <div className="flex flex-wrap gap-4">
          {Object.entries(categoryColors).map(([category, color]) => (
            <div key={category} className="flex items-center">
              <div className={`w-3 h-3 rounded-full ${color} mr-2`} />
              <span className="text-sm text-gray-600 capitalize">{category}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Timeline */}
      {Object.keys(groupedByPeriod).length > 0 ? (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

          {Object.entries(groupedByPeriod).map(([period, periodInitiatives]) => (
            <div key={period} className="relative pl-12 pb-8">
              {/* Period marker */}
              <div className="absolute left-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">
                  {period.split(' ')[0]}
                </span>
              </div>

              {/* Period header */}
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{period}</h3>
                <p className="text-sm text-gray-500">
                  {periodInitiatives.length} initiative{periodInitiatives.length !== 1 ? 's' : ''}
                </p>
              </div>

              {/* Initiatives for this period */}
              <div className="space-y-3">
                {periodInitiatives.map((initiative) => (
                  <Card key={initiative.id} padding="sm" hover>
                    <div className="flex items-start">
                      <div
                        className={`w-3 h-3 rounded-full mt-1.5 mr-3 ${
                          categoryColors[initiative.category] || 'bg-gray-400'
                        }`}
                      />
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">
                              {initiative.name}
                            </h4>
                            {initiative.description && (
                              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                {initiative.description}
                              </p>
                            )}
                          </div>
                          <Badge
                            variant={initiative.status === 'active' ? 'success' : 'default'}
                            size="sm"
                          >
                            {initiative.status}
                          </Badge>
                        </div>

                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>{initiative.mention_count} mentions</span>
                          {initiative.timeline && (
                            <span>Timeline: {initiative.timeline}</span>
                          )}
                          {initiative.last_mentioned_date && (
                            <span>
                              Last: {new Date(initiative.last_mentioned_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No timeline data"
          description="Run analysis on documents to extract initiatives and build a timeline"
          action={
            <Link to={`/companies/${companyId}/analysis`}>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Run Analysis
              </button>
            </Link>
          }
        />
      )}
    </div>
  );
}
