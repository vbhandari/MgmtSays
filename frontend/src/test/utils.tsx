import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { render, RenderOptions } from '@testing-library/react';

// Create a test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

interface WrapperProps {
  children: ReactNode;
}

const createWrapper = () => {
  const queryClient = createTestQueryClient();

  const Wrapper = ({ children }: WrapperProps) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );

  return { Wrapper, queryClient };
};

// Custom render function
export const renderWithProviders = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const { Wrapper, queryClient } = createWrapper();
  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
    queryClient,
  };
};

// Re-export everything from testing-library
export * from '@testing-library/react';
export { renderWithProviders as render };
