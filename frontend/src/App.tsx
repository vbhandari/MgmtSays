import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import CompanyList from './pages/CompanyList';
import CompanyDetail from './pages/CompanyDetail';
import DocumentUpload from './pages/DocumentUpload';
import Analysis from './pages/Analysis';
import Timeline from './pages/Timeline';
import Search from './pages/Search';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#363636',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="companies" element={<CompanyList />} />
          <Route path="companies/:companyId" element={<CompanyDetail />} />
          <Route path="companies/:companyId/upload" element={<DocumentUpload />} />
          <Route path="companies/:companyId/analysis" element={<Analysis />} />
          <Route path="companies/:companyId/timeline" element={<Timeline />} />
          <Route path="search" element={<Search />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
