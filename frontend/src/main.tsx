import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Loading from "./components/Loading";

// Lazy load pages เพื่อเพิ่มประสิทธิภาพ


interface ProtectedRoute {
  path: string;
  component: React.LazyExoticComponent<React.FC>;
}

interface UnprotectedRoute {
  path: string;
  component: React.LazyExoticComponent<React.FC>;
}

// กำหนด array ของ routes สำหรับหน้าเพิ่มเติม
const protectedroutes: ProtectedRoute[] = [
  
];


// กำหนด array ของ routes สำหรับหน้าเพิ่มเติม
const unprotectedroutes: UnprotectedRoute[] = [
  {path:"/app", component: lazy(() => import("./App"))}
];

// Render แอปพลิเคชัน
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<Loading />}>
            <Routes>
              {/* unprotected routes */}
              
              
              {unprotectedroutes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={
                      <route.component />
                  }
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