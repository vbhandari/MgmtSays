import { useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeftIcon, CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Card, Button, Input, Alert } from '../components/ui';
import { useCompany, useUploadDocument } from '../hooks';
import toast from 'react-hot-toast';
import type { DocumentType } from '../types';

const documentTypes: { value: DocumentType; label: string }[] = [
  { value: 'earnings_call', label: 'Earnings Call Transcript' },
  { value: 'annual_report', label: 'Annual Report' },
  { value: 'quarterly_report', label: 'Quarterly Report (10-Q)' },
  { value: 'investor_presentation', label: 'Investor Presentation' },
  { value: 'press_release', label: 'Press Release' },
  { value: 'sec_filing', label: 'SEC Filing' },
  { value: 'other', label: 'Other' },
];

const fiscalPeriods = ['Q1', 'Q2', 'Q3', 'Q4', 'FY'];

export default function DocumentUpload() {
  const { companyId } = useParams<{ companyId: string }>();
  const navigate = useNavigate();
  
  const { data: company } = useCompany(companyId!);
  const uploadMutation = useUploadDocument();

  const [files, setFiles] = useState<File[]>([]);
  const [documentType, setDocumentType] = useState<DocumentType>('earnings_call');
  const [fiscalPeriod, setFiscalPeriod] = useState('');
  const [fiscalYear, setFiscalYear] = useState<number>(new Date().getFullYear());
  const [title, setTitle] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    const validFiles = droppedFiles.filter(
      (file) =>
        file.type === 'application/pdf' ||
        file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
        file.type === 'text/plain' ||
        file.type === 'text/html'
    );
    
    if (validFiles.length < droppedFiles.length) {
      toast.error('Some files were skipped. Supported formats: PDF, DOCX, TXT, HTML');
    }
    
    setFiles((prev) => [...prev, ...validFiles]);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error('Please select at least one file');
      return;
    }

    if (!title && files.length === 1) {
      setTitle(files[0].name.replace(/\.[^/.]+$/, ''));
    }

    try {
      for (const file of files) {
        const docTitle = files.length === 1 ? title : file.name.replace(/\.[^/.]+$/, '');
        
        await uploadMutation.mutateAsync({
          company_id: companyId!,
          title: docTitle,
          document_type: documentType,
          file,
          fiscal_period: fiscalPeriod || undefined,
          fiscal_year: fiscalYear,
        });
      }

      toast.success(`${files.length} document(s) uploaded successfully`);
      navigate(`/companies/${companyId}`);
    } catch (error) {
      toast.error('Failed to upload documents');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back button */}
      <Link
        to={`/companies/${companyId}`}
        className="flex items-center text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeftIcon className="h-4 w-4 mr-1" />
        Back to {company?.name || 'company'}
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
        <p className="text-gray-500 mt-1">
          Upload earnings calls, annual reports, and other management disclosures
        </p>
      </div>

      <Card>
        {/* Drop zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          `}
        >
          <CloudArrowUpIcon className="h-12 w-12 mx-auto text-gray-400" />
          <p className="mt-4 text-lg font-medium text-gray-700">
            Drag and drop files here
          </p>
          <p className="mt-1 text-sm text-gray-500">
            or click to select files
          </p>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.html,.htm"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            style={{ position: 'absolute', top: 0, left: 0 }}
          />
          <Button variant="outline" className="mt-4 relative">
            Select Files
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.html,.htm"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </Button>
          <p className="mt-2 text-xs text-gray-400">
            Supported: PDF, DOCX, TXT, HTML
          </p>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="mt-6 space-y-2">
            <h3 className="font-medium text-gray-900">Selected Files</h3>
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center">
                  <DocumentIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <span className="ml-2 text-xs text-gray-400">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-red-500"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Document details */}
        <div className="mt-6 space-y-4">
          <h3 className="font-medium text-gray-900">Document Details</h3>
          
          {files.length === 1 && (
            <Input
              label="Document Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Q4 2024 Earnings Call Transcript"
            />
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document Type
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {documentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fiscal Period
              </label>
              <select
                value={fiscalPeriod}
                onChange={(e) => setFiscalPeriod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select period</option>
                {fiscalPeriods.map((period) => (
                  <option key={period} value={period}>
                    {period}
                  </option>
                ))}
              </select>
            </div>
            <Input
              label="Fiscal Year"
              type="number"
              value={fiscalYear}
              onChange={(e) => setFiscalYear(parseInt(e.target.value))}
              min={2000}
              max={2100}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" onClick={() => navigate(`/companies/${companyId}`)}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            isLoading={uploadMutation.isPending}
            disabled={files.length === 0}
          >
            Upload {files.length > 0 ? `(${files.length})` : ''}
          </Button>
        </div>
      </Card>

      <Alert type="info" title="Processing">
        After upload, documents will be processed automatically. This includes:
        text extraction, chunking, indexing, and AI analysis. Processing may take
        a few minutes depending on document size.
      </Alert>
    </div>
  );
}
