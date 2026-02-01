import { useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { Card, Button, Input, Badge, InlineLoading, EmptyState, Alert } from '../components/ui';
import { useCompanies, useCreateCompany } from '../hooks';
import toast from 'react-hot-toast';

export default function CompanyList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const { data: companies, isLoading, error } = useCompanies();
  const createMutation = useCreateCompany();

  // Filter companies based on search
  const filteredCompanies = companies?.filter((company) =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    company.ticker?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreateCompany = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      await createMutation.mutateAsync({
        name: formData.get('name') as string,
        ticker: formData.get('ticker') as string || undefined,
        industry: formData.get('industry') as string || undefined,
        description: formData.get('description') as string || undefined,
      });
      
      toast.success('Company created successfully');
      setShowCreateModal(false);
    } catch (error) {
      toast.error('Failed to create company');
    }
  };

  if (isLoading) {
    return <InlineLoading message="Loading companies..." />;
  }

  if (error) {
    return (
      <Alert type="error" title="Error">
        Failed to load companies. Please try again.
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Companies</h2>
          <p className="text-gray-500">Manage companies and their disclosures</p>
        </div>
        <Button
          leftIcon={<PlusIcon className="h-5 w-5" />}
          onClick={() => setShowCreateModal(true)}
        >
          Add Company
        </Button>
      </div>

      {/* Search */}
      <div className="max-w-md">
        <Input
          placeholder="Search companies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
        />
      </div>

      {/* Company list */}
      {filteredCompanies && filteredCompanies.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCompanies.map((company) => (
            <Link key={company.id} to={`/companies/${company.id}`}>
              <Card hover>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{company.name}</h3>
                    {company.ticker && (
                      <Badge variant="primary" size="sm" className="mt-1">
                        {company.ticker}
                      </Badge>
                    )}
                  </div>
                </div>
                {company.industry && (
                  <p className="mt-2 text-sm text-gray-500">{company.industry}</p>
                )}
                {company.description && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    {company.description}
                  </p>
                )}
                <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-400">
                  Added {new Date(company.created_at).toLocaleDateString()}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No companies found"
          description={
            searchTerm
              ? 'Try adjusting your search terms'
              : 'Get started by adding your first company'
          }
          action={
            !searchTerm && (
              <Button onClick={() => setShowCreateModal(true)}>
                Add Company
              </Button>
            )
          }
        />
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md m-4">
            <h3 className="text-lg font-semibold mb-4">Add New Company</h3>
            <form onSubmit={handleCreateCompany} className="space-y-4">
              <Input
                label="Company Name"
                name="name"
                required
                placeholder="e.g., Apple Inc."
              />
              <Input
                label="Ticker Symbol"
                name="ticker"
                placeholder="e.g., AAPL"
              />
              <Input
                label="Industry"
                name="industry"
                placeholder="e.g., Technology"
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of the company..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" isLoading={createMutation.isPending}>
                  Create Company
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
