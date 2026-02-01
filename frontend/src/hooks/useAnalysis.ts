import { useQuery, useMutation } from '@tanstack/react-query';
import { analysisApi } from '../api';
import type { InitiativeCategory } from '../types';

export const analysisKeys = {
  all: ['analysis'] as const,
  search: (query: string, companyId?: string) => [...analysisKeys.all, 'search', query, companyId] as const,
  ask: (question: string, companyId: string) => [...analysisKeys.all, 'ask', question, companyId] as const,
  initiatives: () => [...analysisKeys.all, 'initiatives'] as const,
  initiativeList: (filters: Record<string, unknown>) => [...analysisKeys.initiatives(), 'list', filters] as const,
  initiative: (id: string) => [...analysisKeys.initiatives(), id] as const,
  initiativeTimeline: (id: string) => [...analysisKeys.initiative(id), 'timeline'] as const,
  insights: () => [...analysisKeys.all, 'insights'] as const,
  insightList: (filters: Record<string, unknown>) => [...analysisKeys.insights(), 'list', filters] as const,
  job: (id: string) => [...analysisKeys.all, 'job', id] as const,
};

export function useSearch(params: {
  query: string;
  company_id?: string;
  document_ids?: string[];
  top_k?: number;
}) {
  return useQuery({
    queryKey: analysisKeys.search(params.query, params.company_id),
    queryFn: () => analysisApi.search(params),
    enabled: !!params.query && params.query.length > 2,
  });
}

export function useAskQuestion() {
  return useMutation({
    mutationFn: (params: {
      question: string;
      company_id: string;
      document_ids?: string[];
    }) => analysisApi.ask(params),
  });
}

export function useInitiatives(params?: {
  company_id?: string;
  category?: InitiativeCategory;
  status?: string;
}) {
  return useQuery({
    queryKey: analysisKeys.initiativeList(params || {}),
    queryFn: () => analysisApi.getInitiatives(params),
  });
}

export function useInitiative(id: string) {
  return useQuery({
    queryKey: analysisKeys.initiative(id),
    queryFn: () => analysisApi.getInitiative(id),
    enabled: !!id,
  });
}

export function useInitiativeTimeline(id: string) {
  return useQuery({
    queryKey: analysisKeys.initiativeTimeline(id),
    queryFn: () => analysisApi.getInitiativeTimeline(id),
    enabled: !!id,
  });
}

export function useInsights(params?: {
  company_id?: string;
  document_id?: string;
  category?: string;
  min_importance?: number;
}) {
  return useQuery({
    queryKey: analysisKeys.insightList(params || {}),
    queryFn: () => analysisApi.getInsights(params),
  });
}

export function useRunAnalysis() {
  return useMutation({
    mutationFn: (params: { company_id: string; document_ids?: string[] }) =>
      analysisApi.runAnalysis(params),
  });
}

export function useAnalysisJob(jobId: string, enabled = true) {
  return useQuery({
    queryKey: analysisKeys.job(jobId),
    queryFn: () => analysisApi.getAnalysisStatus(jobId),
    enabled: !!jobId && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running' || data?.status === 'pending') {
        return 2000;
      }
      return false;
    },
  });
}
