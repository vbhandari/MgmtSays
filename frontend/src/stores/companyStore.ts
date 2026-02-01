import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Company } from '../types';

interface CompanyState {
  selectedCompany: Company | null;
  recentCompanies: Company[];
  setSelectedCompany: (company: Company | null) => void;
  addRecentCompany: (company: Company) => void;
  clearRecentCompanies: () => void;
}

export const useCompanyStore = create<CompanyState>()(
  devtools(
    persist(
      (set, get) => ({
        selectedCompany: null,
        recentCompanies: [],

        setSelectedCompany: (company) => {
          set({ selectedCompany: company });
          if (company) {
            get().addRecentCompany(company);
          }
        },

        addRecentCompany: (company) => {
          set((state) => {
            const filtered = state.recentCompanies.filter((c) => c.id !== company.id);
            return {
              recentCompanies: [company, ...filtered].slice(0, 5),
            };
          });
        },

        clearRecentCompanies: () => {
          set({ recentCompanies: [] });
        },
      }),
      {
        name: 'company-storage',
        partialize: (state) => ({
          recentCompanies: state.recentCompanies,
        }),
      }
    ),
    { name: 'CompanyStore' }
  )
);

export default useCompanyStore;
