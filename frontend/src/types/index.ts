// API Types

export interface Company {
  id: string;
  name: string;
  ticker: string | null;
  industry: string | null;
  sector: string | null;
  description: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string | null;
}

export interface Document {
  id: string;
  company_id: string;
  title: string;
  document_type: DocumentType;
  source_url: string | null;
  file_path: string | null;
  publish_date: string | null;
  fiscal_period: string | null;
  fiscal_year: number | null;
  processing_status: ProcessingStatus;
  chunk_count: number;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string | null;
  processed_at: string | null;
}

export type DocumentType = 
  | 'earnings_call'
  | 'annual_report'
  | 'quarterly_report'
  | 'investor_presentation'
  | 'press_release'
  | 'sec_filing'
  | 'other';

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Initiative {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  category: InitiativeCategory;
  status: InitiativeStatus;
  timeline: string | null;
  metrics: string[] | null;
  first_mentioned_date: string | null;
  last_mentioned_date: string | null;
  mention_count: number;
  confidence_score: number;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string | null;
  evidence?: Evidence[];
}

export type InitiativeCategory = 
  | 'strategy'
  | 'product'
  | 'market'
  | 'operational'
  | 'financial'
  | 'technology'
  | 'regulatory'
  | 'competitive';

export type InitiativeStatus = 'active' | 'completed' | 'abandoned' | 'on_hold';

export interface Insight {
  id: string;
  company_id: string;
  document_id: string;
  insight_type: string;
  category: string;
  title: string;
  content: string;
  importance_score: number;
  confidence_score: number;
  sentiment: 'positive' | 'negative' | 'neutral' | 'mixed' | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface Evidence {
  id: string;
  initiative_id: string;
  document_id: string;
  chunk_id: string | null;
  quote: string;
  context: string | null;
  page_number: number | null;
  speaker: string | null;
  speaker_role: string | null;
  relevance_score: number;
  created_at: string;
  document?: Document;
}

export interface SearchResult {
  chunk_id: string;
  text: string;
  score: number;
  document_id: string;
  metadata: Record<string, unknown>;
  highlights?: string[];
}

export interface AnalysisResult {
  question: string;
  answer: string;
  citations: Citation[];
  confidence: number;
  related_topics: string[];
}

export interface Citation {
  quote: string;
  document_id: string;
  document_title: string;
  page_number?: number;
  speaker?: string;
}

// Request/Response types
export interface CreateCompanyRequest {
  name: string;
  ticker?: string;
  industry?: string;
  sector?: string;
  description?: string;
}

export interface UploadDocumentRequest {
  company_id: string;
  title: string;
  document_type: DocumentType;
  file: File;
  fiscal_period?: string;
  fiscal_year?: number;
}

export interface SearchRequest {
  query: string;
  company_id?: string;
  document_ids?: string[];
  top_k?: number;
}

export interface AskQuestionRequest {
  question: string;
  company_id: string;
  document_ids?: string[];
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}
