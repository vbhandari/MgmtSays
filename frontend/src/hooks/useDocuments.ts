import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi } from '../api';
import { companyKeys } from './useCompanies';
import type { DocumentType } from '../types';

export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...documentKeys.lists(), filters] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
  status: (id: string) => [...documentKeys.detail(id), 'status'] as const,
  chunks: (id: string) => [...documentKeys.detail(id), 'chunks'] as const,
};

export function useDocuments(params?: {
  company_id?: string;
  document_type?: DocumentType;
  status?: string;
}) {
  return useQuery({
    queryKey: documentKeys.list(params || {}),
    queryFn: () => documentsApi.list(params),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentsApi.get(id),
    enabled: !!id,
  });
}

export function useDocumentStatus(id: string, enabled = true) {
  return useQuery({
    queryKey: documentKeys.status(id),
    queryFn: () => documentsApi.getStatus(id),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Poll every 2 seconds while processing
      if (data?.status === 'processing') {
        return 2000;
      }
      return false;
    },
  });
}

export function useDocumentChunks(id: string) {
  return useQuery({
    queryKey: documentKeys.chunks(id),
    queryFn: () => documentsApi.getChunks(id),
    enabled: !!id,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      company_id: string;
      title: string;
      document_type: DocumentType;
      file: File;
      fiscal_period?: string;
      fiscal_year?: number;
    }) => documentsApi.upload(data),
    onSuccess: (_, { company_id }) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: companyKeys.documents(company_id) });
      queryClient.invalidateQueries({ queryKey: companyKeys.stats(company_id) });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useReprocessDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentsApi.reprocess(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: documentKeys.status(id) });
    },
  });
}
