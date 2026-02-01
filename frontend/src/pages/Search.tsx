import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MagnifyingGlassIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { Card, CardHeader, Button, Input, Badge, InlineLoading, EmptyState, Alert } from '../components/ui';
import { useCompanies, useSearch, useAskQuestion } from '../hooks';

export default function Search() {
  const [searchParams] = useSearchParams();
  const preselectedCompany = searchParams.get('company');

  const [query, setQuery] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(preselectedCompany || '');
  const [mode, setMode] = useState<'search' | 'ask'>('search');
  const [question, setQuestion] = useState('');

  const { data: companies } = useCompanies();
  
  const { data: searchResults, isLoading: searchLoading } = useSearch({
    query,
    company_id: selectedCompany || undefined,
    top_k: 10,
  });

  const askMutation = useAskQuestion();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Search is automatic via the hook
  };

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question || !selectedCompany) return;

    await askMutation.mutateAsync({
      question,
      company_id: selectedCompany,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search & Ask</h1>
        <p className="text-gray-500 mt-1">
          Search through documents or ask questions about company disclosures
        </p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-2">
        <Button
          variant={mode === 'search' ? 'primary' : 'outline'}
          onClick={() => setMode('search')}
          leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
        >
          Search
        </Button>
        <Button
          variant={mode === 'ask' ? 'primary' : 'outline'}
          onClick={() => setMode('ask')}
          leftIcon={<ChatBubbleLeftRightIcon className="h-5 w-5" />}
        >
          Ask Question
        </Button>
      </div>

      {/* Company filter */}
      <Card padding="sm">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Company:</label>
          <select
            value={selectedCompany}
            onChange={(e) => setSelectedCompany(e.target.value)}
            className="flex-1 max-w-xs px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All companies</option>
            {companies?.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name} {company.ticker && `(${company.ticker})`}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {/* Search mode */}
      {mode === 'search' && (
        <>
          <form onSubmit={handleSearch}>
            <Input
              placeholder="Search documents..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
            />
          </form>

          {searchLoading && <InlineLoading message="Searching..." />}

          {searchResults && searchResults.length > 0 && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500">
                Found {searchResults.length} results
              </p>
              {searchResults.map((result, index) => (
                <Card key={index} hover>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-gray-900">{result.text}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="default" size="sm">
                          Score: {(result.score * 100).toFixed(0)}%
                        </Badge>
                        {result.metadata?.document_type ? (
                          <Badge variant="info" size="sm">
                            {String(result.metadata.document_type)}
                          </Badge>
                        ) : null}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {query && searchResults?.length === 0 && !searchLoading && (
            <EmptyState
              title="No results found"
              description="Try adjusting your search terms or selecting a different company"
            />
          )}
        </>
      )}

      {/* Ask mode */}
      {mode === 'ask' && (
        <>
          <form onSubmit={handleAsk} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Question
              </label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What are the company's main strategic initiatives for 2025?"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button
              type="submit"
              isLoading={askMutation.isPending}
              disabled={!question || !selectedCompany}
            >
              Ask Question
            </Button>
            {!selectedCompany && (
              <p className="text-sm text-amber-600">Please select a company first</p>
            )}
          </form>

          {askMutation.data && (
            <Card>
              <CardHeader title="Answer" />
              <div className="prose prose-sm max-w-none">
                <p>{askMutation.data.answer}</p>
              </div>

              {askMutation.data.citations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Citations</h4>
                  <div className="space-y-2">
                    {askMutation.data.citations.map((citation, index) => (
                      <blockquote
                        key={index}
                        className="text-sm text-gray-600 italic border-l-2 border-gray-200 pl-3"
                      >
                        "{citation.quote}"
                        <footer className="text-xs text-gray-400 mt-1 not-italic">
                          — {citation.document_title}
                          {citation.speaker && `, ${citation.speaker}`}
                        </footer>
                      </blockquote>
                    ))}
                  </div>
                </div>
              )}

              {askMutation.data.related_topics.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Related Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {askMutation.data.related_topics.map((topic, index) => (
                      <Badge key={index} variant="default">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-4 text-right">
                <span className="text-sm text-gray-500">
                  Confidence: {Math.round(askMutation.data.confidence * 100)}%
                </span>
              </div>
            </Card>
          )}

          {askMutation.isError && (
            <Alert type="error" title="Error">
              Failed to get an answer. Please try again.
            </Alert>
          )}
        </>
      )}
    </div>
  );
}
