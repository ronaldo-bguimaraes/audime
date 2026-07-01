import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { AuthProvider } from "./hooks/useAuth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { NavBar } from "./components/NavBar";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Extrair } from "./pages/Extrair";
import { NotaDetalhe } from "./pages/NotaDetalhe";
import styles from "./App.module.css";

function AppLayout() {
  return (
    <div className={styles.layout}>
      <NavBar />
      <main className={styles.main}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/extrair"
            element={
              <ProtectedRoute>
                <Extrair />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notas/:id"
            element={
              <ProtectedRoute>
                <NotaDetalhe />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<AppLayout />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
