import Header from './components/Header'
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from './context/AuthContext';
import { WorkflowProvider, useWorkflow } from './context/WorkflowContext';
import HomePage from './components/home/HomePage';
import DashboardLayout from './components/dashboard/DashboardLayout';
import { AnimatePresence } from 'framer-motion';

const AppContent = () => {
  const { currentView } = useWorkflow();

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main>
        <AnimatePresence mode="wait">
          {currentView === 'HOME' && <HomePage key="home" />}
          {currentView === 'DASHBOARD' && <DashboardLayout key="dashboard" />}
          {/* Platform view could just be Home for now or a placeholder */}
          {currentView === 'PLATFORM' && <HomePage key="platform" />}
        </AnimatePresence>
      </main>
    </div>
  );
};

function App() {
  const clientId = "12928679320-pdfoui313avkun1sbobnjsj7jd827jnt.apps.googleusercontent.com";
  console.log("Initializing Google OAuth with Client ID:", clientId);

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        <WorkflowProvider>
          <AppContent />
        </WorkflowProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  )
}

export default App
