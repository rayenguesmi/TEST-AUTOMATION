import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import Sidebar from './components/Sidebar';
import Register from './pages/Register';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VerifyEmail from './pages/VerifyEmail';
import UserDashboard from './pages/UserDashboard';
import MesTests from './pages/MesTests';
import Projets from './pages/Projets';
import UrlsSurveillees from './pages/UrlsSurveillees';
import AdminDashboard from './pages/AdminDashboard';

// ─── Loading Screen ──────────────────────────────────────────────────────────
const LoadingScreen = () => (
  <div style={{
    height: '100vh', width: '100vw',
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    background: 'var(--bg-base)', gap: 20,
  }}>
    <img src="/logo.png" alt="AutoTest" style={{
      width: 64, height: 64,
      objectFit: 'contain',
      filter: 'drop-shadow(0 0 16px rgba(34,211,238,0.4))',
      animation: 'pulse-dot 2s ease-in-out infinite',
    }} />
    <div style={{ display: 'flex', gap: 6 }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: '50%',
          background: 'var(--color-brand)', opacity: 0.6,
          animation: `pulse-dot 1.2s ease-in-out ${i * 0.2}s infinite`,
        }} />
      ))}
    </div>
  </div>
);

// ─── Protected Route ─────────────────────────────────────────────────────────
const ProtectedRoute = ({ children, role }) => {
  const { user, loading } = useAuth();

  if (loading) return <LoadingScreen />;

  if (!user) return <Navigate to="/login" replace />;

  // Admin on a user-only route → redirect to admin dashboard
  if (role === 'user' && user.role === 'admin') {
    return <Navigate to="/admin/dashboard" replace />;
  }

  // Non-admin on an admin-only route → redirect to user dashboard
  if (role === 'admin' && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="layout-root">
      <Sidebar />
      <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        {children}
      </main>
    </div>
  );
};

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/verify-email" element={<VerifyEmail />} />

            {/* User Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute role="user"><UserDashboard /></ProtectedRoute>
            } />
            <Route path="/my-tests" element={
              <ProtectedRoute role="user"><MesTests /></ProtectedRoute>
            } />
            <Route path="/projects" element={
              <ProtectedRoute role="user"><Projets /></ProtectedRoute>
            } />
            <Route path="/urls" element={
              <ProtectedRoute role="user"><UrlsSurveillees /></ProtectedRoute>
            } />

            {/* Admin Routes */}
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="/admin/dashboard" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/users" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/health" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/logs" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/tests" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/settings" element={
              <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
            } />

            {/* Default */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
