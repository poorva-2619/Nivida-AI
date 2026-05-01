import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Pages
import Login from './pages/Login';
import AdminDashboard from './pages/admin/AdminDashboard';
import TenderUpload from './pages/admin/TenderUpload';
import CriteriaReview from './pages/admin/CriteriaReview';
import EvaluationResults from './pages/admin/EvaluationResults';
import FraudAlerts from './pages/admin/FraudAlerts';
import ReportExport from './pages/admin/ReportExport';
import VendorDashboard from './pages/vendor/VendorDashboard';
import TenderBrowse from './pages/vendor/TenderBrowse';
import DocumentUpload from './pages/vendor/DocumentUpload';
import SubmissionStatus from './pages/vendor/SubmissionStatus';

const ProtectedRoute = ({ children, allowedRole }) => {
  const { isLoggedIn, role } = useAuthStore();
  
  if (!isLoggedIn) {
    return <Navigate to="/" replace />;
  }
  
  if (allowedRole && role !== allowedRole) {
    return <Navigate to={role === 'admin' ? '/admin/dashboard' : '/vendor/dashboard'} replace />;
  }
  
  return children;
};

function App() {
  const { isLoggedIn, role } = useAuthStore();

  return (
    <Router>
      <Routes>
        <Route path="/" element={
          isLoggedIn ? <Navigate to={role === 'admin' ? '/admin/dashboard' : '/vendor/dashboard'} replace /> : <Login />
        } />
        
        {/* Admin Routes */}
        <Route path="/admin/dashboard" element={<ProtectedRoute allowedRole="admin"><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/tender-upload" element={<ProtectedRoute allowedRole="admin"><TenderUpload /></ProtectedRoute>} />
        <Route path="/admin/criteria" element={<ProtectedRoute allowedRole="admin"><CriteriaReview /></ProtectedRoute>} />
        <Route path="/admin/results" element={<ProtectedRoute allowedRole="admin"><EvaluationResults /></ProtectedRoute>} />
        <Route path="/admin/fraud" element={<ProtectedRoute allowedRole="admin"><FraudAlerts /></ProtectedRoute>} />
        <Route path="/admin/report" element={<ProtectedRoute allowedRole="admin"><ReportExport /></ProtectedRoute>} />

        {/* Vendor Routes */}
        <Route path="/vendor/dashboard" element={<ProtectedRoute allowedRole="vendor"><VendorDashboard /></ProtectedRoute>} />
        <Route path="/vendor/tenders" element={<ProtectedRoute allowedRole="vendor"><TenderBrowse /></ProtectedRoute>} />
        <Route path="/vendor/upload" element={<ProtectedRoute allowedRole="vendor"><DocumentUpload /></ProtectedRoute>} />
        <Route path="/vendor/status" element={<ProtectedRoute allowedRole="vendor"><SubmissionStatus /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;
