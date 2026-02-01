import apiClient from './client';
import type { 
  SearchResult, 
  AnalysisResult, 
  Initiative, 
  Insight,
  InitiativeCategory 
} from '../types';

export const analysisApi = {
  search: async (params: {
    query: string;
    company_id?: string;
    document_ids?: string[];
    top_k?: number;
  }): Promise<SearchResult[]> => {
    return apiClient.post('/analysis/search', params);
  },

  ask: async (params: {
    question: string;
    company_id: string;
    document_ids?: string[];
  }): Promise<AnalysisResult> => {
    return apiClient.post('/analysis/ask', params);
  },

  getInitiatives: async (params?: {
    company_id?: string;
    category?: InitiativeCategory;
    status?: string;
  }): Promise<Initiative[]> => {
    return apiClient.get('/analysis/initiatives', { params });
  },

  getInitiative: async (id: string): Promise<Initiative> => {
    return apiClient.get(`/analysis/initiatives/${id}`);
  },

  getInitiativeTimeline: async (initiativeId: string): Promise<{
    initiative: Initiative;
    timeline: Array<{
      date: string;
      document_id: string;
      document_title: string;
      quote: string;
      context: string | null;
    }>;
  }> => {
    return apiClient.get(`/analysis/initiatives/${initiativeId}/timeline`);
  },

  getInsights: async (params?: {
    company_id?: string;
    document_id?: string;
    category?: string;
    min_importance?: number;
  }): Promise<Insight[]> => {
    return apiClient.get('/analysis/insights', { params });
  },

  runAnalysis: async (params: {
    company_id: string;
    document_ids?: string[];
  }): Promise<{
    job_id: string;
    status: string;
  }> => {
    return apiClient.post('/analysis/run', params);
  },

  getAnalysisStatus: async (jobId: string): Promise<{
    job_id: string;
    status: string;
    progress: number;
    result: unknown | null;
    error: string | null;
  }> => {
    return apiClient.get(`/analysis/jobs/${jobId}`);
  },

  compareInitiatives: async (initiativeIds: string[]): Promise<{
    initiatives: Initiative[];
    comparison: {
      common_themes: string[];
      differences: string[];
      timeline_overlap: boolean;
    };
  }> => {
    return apiClient.post('/analysis/initiatives/compare', { initiative_ids: initiativeIds });
  },
};

export default analysisApi;
