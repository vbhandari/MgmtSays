import apiClient from './client';
import type { Document, DocumentType } from '../types';

export const documentsApi = {
  list: async (params?: { 
    company_id?: string;
    document_type?: DocumentType;
    status?: string;
  }): Promise<Document[]> => {
    return apiClient.get('/documents', { params });
  },

  get: async (id: string): Promise<Document> => {
    return apiClient.get(`/documents/${id}`);
  },

  upload: async (data: {
    company_id: string;
    title: string;
    document_type: DocumentType;
    file: File;
    fiscal_period?: string;
    fiscal_year?: number;
  }): Promise<Document> => {
    const formData = new FormData();
    formData.append('company_id', data.company_id);
    formData.append('title', data.title);
    formData.append('document_type', data.document_type);
    formData.append('file', data.file);
    
    if (data.fiscal_period) {
      formData.append('fiscal_period', data.fiscal_period);
    }
    if (data.fiscal_year) {
      formData.append('fiscal_year', data.fiscal_year.toString());
    }

    return apiClient.upload('/documents/upload', formData);
  },

  delete: async (id: string): Promise<void> => {
    return apiClient.delete(`/documents/${id}`);
  },

  reprocess: async (id: string): Promise<Document> => {
    return apiClient.post(`/documents/${id}/reprocess`);
  },

  getStatus: async (id: string): Promise<{
    status: string;
    progress: number;
    message: string | null;
  }> => {
    return apiClient.get(`/documents/${id}/status`);
  },

  getChunks: async (id: string): Promise<{
    chunks: Array<{
      id: string;
      text: string;
      metadata: Record<string, unknown>;
    }>;
    total: number;
  }> => {
    return apiClient.get(`/documents/${id}/chunks`);
  },
};

export default documentsApi;
