import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeftIcon, PlayIcon } from '@heroicons/react/24/outline';
import { Card, CardHeader, Button, Badge, Alert, EmptyState } from '../components/ui';
import { useCompany, useCompanyDocuments, useCompanyInitiatives, useRunAnalysis, useAnalysisJob } from '../hooks';
import toast from 'react-hot-toast';

export default function Analysis() {
  const { companyId } = useParams<{ companyId: string }>();
  
  const { data: company } = useCompany(companyId!);
  const { data: documents } = useCompanyDocuments(companyId!);
  const { data: initiatives, refetch: refetchInitiatives } = useCompanyInitiatives(companyId!);
  
  const runAnalysisMutation = useRunAnalysis();
  const [jobId, setJobId] = useState<string | null>(null);
  const { data: jobStatus } = useAnalysisJob(jobId || '', !!jobId);

  const completedDocs = documents?.filter((d) => d.processing_status === 'completed') || [];

  const handleRunAnalysis = async () => {
    try {
      const result = await runAnalysisMutation.mutateAsync({
        company_id: companyId!,
      });
      setJobId(result.job_id);
      toast.success('Analysis started');
    } catch (error) {
      toast.error('Failed to start analysis');
    }
  };

  // Check if job completed
  if (jobStatus?.status === 'completed' && jobId) {
    setJobId(null);
    refetchInitiatives();
    toast.success('Analysis completed!');
  }

  const categoryColors: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    strategy: 'primary',
    product: 'success',
    market: 'warning',
    operational: 'info',
    financial: 'danger',
    technology: 'primary',
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

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analysis</h1>
          <p className="text-gray-500 mt-1">
            Extract strategic initiatives and insights from documents
          </p>
        </div>
        <Button
          leftIcon={<PlayIcon className="h-5 w-5" />}
          onClick={handleRunAnalysis}
          isLoading={runAnalysisMutation.isPending || !!jobId}
          disabled={completedDocs.length === 0}
        >
          Run Analysis
        </Button>
      </div>

      {/* Analysis progress */}
      {jobId && jobStatus && (
        <Card>
          <CardHeader title="Analysis in Progress" />
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status: {jobStatus.status}</span>
              <span className="text-sm text-gray-600">{jobStatus.progress}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${jobStatus.progress}%` }}
              />
            </div>
          </div>
        </Card>
      )}

      {/* Document status */}
      <Card>
        <CardHeader
          title="Documents for Analysis"
          subtitle={`${completedDocs.length} of ${documents?.length || 0} documents ready`}
        />
        {documents && documents.length > 0 ? (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900">{doc.title}</p>
                  <p className="text-sm text-gray-500">
                    {doc.fiscal_period} {doc.fiscal_year}
                  </p>
                </div>
                <Badge
                  variant={
                    doc.processing_status === 'completed'
                      ? 'success'
                      : doc.processing_status === 'processing'
                      ? 'warning'
                      : doc.processing_status === 'failed'
                      ? 'danger'
                      : 'default'
                  }
                >
                  {doc.processing_status}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <Alert type="warning">
            No documents found. Upload documents first to run analysis.
          </Alert>
        )}
      </Card>

      {/* Initiatives */}
      <Card>
        <CardHeader
          title="Extracted Initiatives"
          subtitle={`${initiatives?.length || 0} initiatives found`}
        />
        {initiatives && initiatives.length > 0 ? (
          <div className="space-y-4">
            {initiatives.map((initiative) => (
              <div
                key={initiative.id}
                className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{initiative.name}</h4>
                    {initiative.description && (
                      <p className="text-sm text-gray-600 mt-1">{initiative.description}</p>
                    )}
                    <div className="flex items-center gap-2 mt-3">
                      <Badge variant={categoryColors[initiative.category] || 'default'}>
                        {initiative.category}
                      </Badge>
                      {initiative.timeline && (
                        <Badge variant="default">{initiative.timeline}</Badge>
                      )}
                      <span className="text-xs text-gray-400">
                        {initiative.mention_count} mention{initiative.mention_count !== 1 ? 's' : ''}
                      </span>
                    </div>
                    {initiative.metrics && initiative.metrics.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs text-gray-500">Metrics: </span>
                        <span className="text-xs text-gray-700">
                          {initiative.metrics.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-sm font-medium text-gray-900">
                      {Math.round(initiative.confidence_score * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">confidence</div>
                  </div>
                </div>

                {/* Evidence preview */}
                {initiative.evidence && initiative.evidence.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs font-medium text-gray-500 mb-2">Evidence</p>
                    <blockquote className="text-sm text-gray-600 italic border-l-2 border-gray-200 pl-3">
                      "{initiative.evidence[0].quote}"
                    </blockquote>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No initiatives extracted yet"
            description="Run analysis on your documents to extract strategic initiatives"
          />
        )}
      </Card>
    </div>
  );
}
