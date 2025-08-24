import React, { lazy, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Loading from './components/Loading';

interface ProtectedRoute {
  path: string;
  component: React.LazyExoticComponent<React.FC>;
}

interface UnprotectedRoute {
  path: string;
  component: React.LazyExoticComponent<React.FC>;
}

const protectedroutes: ProtectedRoute[] = [
  { path: '/homes/system-admin', component: lazy(() => import('./pages/homes/SystemAdminHome')) },
  { path: '/homes/basetype-admin', component: lazy(() => import('./pages/homes/BasetypeAdminHome')) },
  { path: '/homes/hr-admin', component: lazy(() => import('./pages/homes/HrAdminHome')) },
  { path: '/homes/organization-admin', component: lazy(() => import('./pages/homes/OrganizationAdminHome')) },
  { path: '/homes/organization-user', component: lazy(() => import('./pages/homes/OrganizationUserHome')) },
  { path: '/homes/person-user', component: lazy(() => import('./pages/homes/PersonUserHome')) },
];

const unprotectedroutes: UnprotectedRoute[] = [
  { path: '/', component: lazy(() => import('./pages/RootPage')) },
  { path: '/login', component: lazy(() => import('./pages/login/Login')) },
  { path: '/register', component: lazy(() => import('./pages/register/Register')) },
];

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<Loading />}>
            <Routes>
              {unprotectedroutes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={<route.component />}
                />
              ))}
              {protectedroutes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={
                    <ProtectedRoute>
                      <route.component />
                    </ProtectedRoute>
                  }
                />
              ))}
              <Route path="*" element={<h1>404 Not Found</h1>} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>
);