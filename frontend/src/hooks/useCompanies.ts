import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { companiesApi } from '../api';
import type { CreateCompanyRequest } from '../types';

export const companyKeys = {
  all: ['companies'] as const,
  lists: () => [...companyKeys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...companyKeys.lists(), filters] as const,
  details: () => [...companyKeys.all, 'detail'] as const,
  detail: (id: string) => [...companyKeys.details(), id] as const,
  stats: (id: string) => [...companyKeys.detail(id), 'stats'] as const,
  documents: (id: string) => [...companyKeys.detail(id), 'documents'] as const,
  initiatives: (id: string) => [...companyKeys.detail(id), 'initiatives'] as const,
  insights: (id: string) => [...companyKeys.detail(id), 'insights'] as const,
};

export function useCompanies() {
  return useQuery({
    queryKey: companyKeys.lists(),
    queryFn: () => companiesApi.list(),
  });
}

export function useCompany(id: string) {
  return useQuery({
    queryKey: companyKeys.detail(id),
    queryFn: () => companiesApi.get(id),
    enabled: !!id,
  });
}

export function useCompanyStats(id: string) {
  return useQuery({
    queryKey: companyKeys.stats(id),
    queryFn: () => companiesApi.getStats(id),
    enabled: !!id,
  });
}

export function useCompanyDocuments(id: string) {
  return useQuery({
    queryKey: companyKeys.documents(id),
    queryFn: () => companiesApi.getDocuments(id),
    enabled: !!id,
  });
}

export function useCompanyInitiatives(id: string) {
  return useQuery({
    queryKey: companyKeys.initiatives(id),
    queryFn: () => companiesApi.getInitiatives(id),
    enabled: !!id,
  });
}

export function useCompanyInsights(id: string) {
  return useQuery({
    queryKey: companyKeys.insights(id),
    queryFn: () => companiesApi.getInsights(id),
    enabled: !!id,
  });
}

export function useCreateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateCompanyRequest) => companiesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

export function useUpdateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateCompanyRequest> }) =>
      companiesApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

export function useDeleteCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => companiesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}
