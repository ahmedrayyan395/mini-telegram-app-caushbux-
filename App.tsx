import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { TonConnectUIProvider } from '@tonconnect/ui-react';
import { Buffer } from 'buffer';

// Import types and the API functions
import type { User } from './types';
import { loginWithTelegram, adminLogout, devLogin } from './services/api';

// Import Layouts and Components
import Layout from './components/Layout';
import ProtectedRoute from './components/admin/ProtectedRoute';

// Import User Pages
import EarningsPage from './pages/EarningsPage';
import QuestsPage from './pages/QuestsPage';
import FriendsPage from './pages/FriendsPage';
import WithdrawPage from './pages/WithdrawPage';
import NewTaskPage from './pages/NewTaskPage';
import NewPartnerTaskPage from './pages/NewPartnerTaskPage';
import GamePage from './pages/GamePage';
import SpinWheelPage from './pages/SpinWheelPage';
import SpaceDefenderPage from './pages/SpaceDefenderPage';
import StreetRacingPage from './pages/StreetRacingPage';

// Import Admin Pages
import LoginPage from './pages/admin/LoginPage';
import AdminLayout from './pages/admin/AdminLayout';
import DashboardPage from './pages/admin/DashboardPage';
import UsersPage from './pages/admin/UsersPage';
import PromoCodesPage from './pages/admin/PromoCodesPage';
import TasksPage from './pages/admin/TasksPage';
import SettingsPage from './pages/admin/SettingsPage';
import HomePage from './pages/HomePage';




/**
 * Extend the global Window interface to include the Telegram WebApp object.
 * This is necessary for TypeScript to recognize window.Telegram.
 */
declare global {
  interface Window {
    Buffer: typeof Buffer;
    Telegram: {
      WebApp: {
        initData: string;
        ready: () => void;
        expand: () => void;
        // You can add other Telegram WebApp properties here if you use them
      }
    }
  }
}

// A required polyfill for the @tonconnect/ui-react library to work correctly.
window.Buffer = Buffer;

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);



const IS_DEV_MODE = false;
const DEV_USER_ID = 3; // The ID of the user from your database you want to simulate.


// In App.tsx

  useEffect(() => {
    // --- START OF EFFECT ---
    console.log("1. useEffect has started.");

    const authenticateApp = async () => {
      try {
        console.log("3. authenticateApp function has been called.");
        
        if (IS_DEV_MODE) {
          console.log(`4. DEV MODE is ON. Calling devLogin with User ID: ${DEV_USER_ID}`);
          const devUser = await devLogin(DEV_USER_ID);
          console.log("6. devLogin was successful. Received user data:", devUser);
          
          // CRITICAL CHECK: Is the received data valid?
          if (!devUser || typeof devUser.id !== 'number') {
            throw new Error("devLogin returned invalid data.");
          }

          console.log("7. User data is valid. Calling setUser...");
          setUser(devUser);
          console.log("8. setUser has been called successfully.");

        } else {
          // --- PRODUCTION MODE ---
          console.log("4. PROD MODE is ON. Checking for Telegram WebApp...");
          
          if (!window.Telegram?.WebApp) {
              throw new Error("Telegram WebApp object is not available.");
          }

          console.log("5. PROD MODE: Waiting for Telegram to be ready...");
          window.Telegram.WebApp.ready();
          window.Telegram.WebApp.expand();
          
          const initData = window.Telegram.WebApp.initData;
          console.log("6. PROD MODE: Telegram is ready. initData length:", initData?.length || 0);

          if (!initData) {
            throw new Error("initData is empty even after ready() was called.");
          }
          
          console.log("7. PROD MODE: Calling loginWithTelegram...");
          const authenticatedUser = await loginWithTelegram(initData);
          console.log("8. PROD MODE: loginWithTelegram was successful. Received user data:", authenticatedUser);
          
          if (!authenticatedUser || typeof authenticatedUser.id !== 'number') {
            throw new Error("loginWithTelegram returned invalid data.");
          }

          console.log("9. PROD MODE: User data is valid. Calling setUser...");
          setUser(authenticatedUser);
          console.log("10. PROD MODE: setUser has been called successfully.");
        }
      } catch (err: any) {
        console.error("--- CATCH BLOCK TRIGGERED ---");
        console.error("An error occurred during authentication:", err);
        const errorMessage = err.data?.message || err.data?.error || err.message || "An unknown error occurred.";
        setError(errorMessage);
      } finally {
        console.log("--- FINALLY BLOCK TRIGGERED ---");
        console.log("Setting loading to false.");
        setLoading(false);
      }
    };
    
    // --- START OF EXECUTION LOGIC ---
    console.log("2. About to call authenticateApp.");
    authenticateApp();

    // Admin auth check
    if (localStorage.getItem('admin_token')) {
        setIsAdminAuthenticated(true);
    }
    
  }, []); // Empty dependency array ensures this runs only once.
  
  const handleSetUser = (update: React.SetStateAction<User | null>) => {
    setUser(update);
  };
  
 
  const handleAdminLogin = () => {
      setIsAdminAuthenticated(true);
  };
  
 
  const handleAdminLogout = () => {
      adminLogout(); // This function should remove the token from localStorage
      setIsAdminAuthenticated(false);
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">Authenticating...</div>;
  }

  if (error) {
    // This component will now display a detailed error message instead of crashing.
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-900 text-red-500 p-4 text-center">
        <h2 className="text-2xl font-bold mb-4">Authentication Error</h2>
        <p>Could not load user data. Please try again.</p>
        <pre className="mt-4 p-4 bg-slate-800 rounded-md text-left text-sm text-red-400 w-full max-w-lg">
          {error}
        </pre>
      </div>
    );
  }

   if (!user) {
    // This will be shown briefly if auth finishes but something went wrong with setUser.
    // Or if an unauthenticated user tries to access the app.
    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900 text-yellow-500">
            Authentication successful, but user data is not available. Please reload.
        </div>
    );
  }

  // -- Main Application Routes --
  return (
    <TonConnectUIProvider manifestUrl="https://ton-connect.github.io/demo-dapp-with-react-ui/tonconnect-manifest.json">
        <div className="min-h-screen bg-slate-900 text-white font-sans">
            <Routes>
               {/* Admin Routes */}
                <Route path="/admin/login" element={<LoginPage onLogin={handleAdminLogin} />} />

                <Route path="/admin" element={ <ProtectedRoute isAuthenticated={isAdminAuthenticated} /> }>
                  <Route element={<AdminLayout onLogout={handleAdminLogout} />}>
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="users" element={<UsersPage />} />
                    <Route path="promocodes" element={<PromoCodesPage />} />
                    <Route path="tasks" element={<TasksPage />} />
                    <Route path="settings" element={<SettingsPage />} />
                    <Route index element={<Navigate to="dashboard" />} />
                  </Route>
                </Route>

                {/* User Routes */}
                {/* Standalone pages without the main layout/navbar */}
                <Route path="/new-task" element={<NewTaskPage user={user} setUser={handleSetUser} />} />
                <Route path="/new-partner-task" element={<NewPartnerTaskPage user={user} setUser={handleSetUser} />} />
                <Route path="/spin-wheel" element={<SpinWheelPage user={user} setUser={handleSetUser} />} />
                <Route path="/game/space-defender" element={<SpaceDefenderPage user={user} setUser={setUser} />} />
                <Route path="/game/street-racing" element={<StreetRacingPage user={user} setUser={setUser} />} />

                {/* Main user pages with the shared Layout (navbar, etc.) */}
                
                <Route element={<Layout user={user} />}>
                    <Route path="/" element={<EarningsPage setUser={setUser} />} />
                    {/* <Route path="/" element={<HomePage />} /> */}
                    
                    <Route path="/quests" element={<QuestsPage />} />
                    <Route path="/game" element={<GamePage />} />
                    <Route path="/friends" element={<FriendsPage user={user} setUser={handleSetUser} />} />
                    
                    <Route path="/withdraw" element={<WithdrawPage user={user} setUser={handleSetUser} />} />
                </Route>



            </Routes>
        </div>
    </TonConnectUIProvider>
  );

  
};

export default App;