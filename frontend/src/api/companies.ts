import apiClient from './client';
import type { Company, CreateCompanyRequest, Document, Initiative, Insight } from '../types';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const companiesApi = {
  list: async (params?: { page?: number; page_size?: number }): Promise<Company[]> => {
    const response = await apiClient.get<PaginatedResponse<Company>>('/companies', { params });
    return response.items;
  },

  get: async (id: string): Promise<Company> => {
    return apiClient.get(`/companies/${id}`);
  },

  create: async (data: CreateCompanyRequest): Promise<Company> => {
    return apiClient.post('/companies', data);
  },

  update: async (id: string, data: Partial<CreateCompanyRequest>): Promise<Company> => {
    return apiClient.patch(`/companies/${id}`, data);
  },

  delete: async (id: string): Promise<void> => {
    return apiClient.delete(`/companies/${id}`);
  },

  getByTicker: async (ticker: string): Promise<Company | null> => {
    return apiClient.get(`/companies/ticker/${ticker}`);
  },

  getDocuments: async (companyId: string): Promise<Document[]> => {
    return apiClient.get(`/companies/${companyId}/documents`);
  },

  getInitiatives: async (companyId: string): Promise<Initiative[]> => {
    return apiClient.get(`/companies/${companyId}/initiatives`);
  },

  getInsights: async (companyId: string): Promise<Insight[]> => {
    return apiClient.get(`/companies/${companyId}/insights`);
  },

  getStats: async (companyId: string): Promise<{
    document_count: number;
    initiative_count: number;
    insight_count: number;
    last_updated: string | null;
  }> => {
    return apiClient.get(`/companies/${companyId}/stats`);
  },
};

export default companiesApi;
