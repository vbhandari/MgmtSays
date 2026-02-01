import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        sidebarOpen: true,
        theme: 'light',

        toggleSidebar: () => {
          set((state) => ({ sidebarOpen: !state.sidebarOpen }));
        },

        setSidebarOpen: (open) => {
          set({ sidebarOpen: open });
        },

        setTheme: (theme) => {
          set({ theme });
        },
      }),
      {
        name: 'ui-storage',
      }
    ),
    { name: 'UIStore' }
  )
);

export default useUIStore;
