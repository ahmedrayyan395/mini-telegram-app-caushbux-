import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { TonConnectUIProvider } from '@tonconnect/ui-react';
import { Buffer } from 'buffer';

import type { User } from './types';
import { fetchUser } from './services/api';

import Layout from './components/Layout';
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

// Admin Imports
import LoginPage from './pages/admin/LoginPage';
import AdminLayout from './pages/admin/AdminLayout';
import ProtectedRoute from './components/admin/ProtectedRoute';
import DashboardPage from './pages/admin/DashboardPage';
import UsersPage from './pages/admin/UsersPage';
import PromoCodesPage from './pages/admin/PromoCodesPage';
import TasksPage from './pages/admin/TasksPage';
import SettingsPage from './pages/admin/SettingsPage';


// Extend the Window interface to include Buffer for polyfill
declare global {
  interface Window {
    Buffer: typeof Buffer;
  }
}

// Buffer polyfill for @tonconnect/ui-react
window.Buffer = Buffer;

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);


  useEffect(() => {
    fetchUser().then(setUser);
    // Check for existing admin token in localStorage
    if (localStorage.getItem('admin_token')) {
        setIsAdminAuthenticated(true);
    }
  }, []);
  


  const handleSetUser = (update: React.SetStateAction<User | null>) => {
    setUser(update);
  };
  
  const handleAdminLogin = () => {
      setIsAdminAuthenticated(true);
  };
  
  const handleAdminLogout = () => {
      localStorage.removeItem('admin_token');
      setIsAdminAuthenticated(false);
  };

  return (
    <TonConnectUIProvider manifestUrl="https://ton-connect.github.io/demo-dapp-with-react-ui/tonconnect-manifest.json">
        <div className="min-h-screen bg-slate-900 text-white font-sans">
            <Routes>
               {/* Admin Routes */}
                <Route path="/admin/login" element={<LoginPage onLogin={handleAdminLogin} />} />

                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute isAuthenticated={isAdminAuthenticated} />
                  }

                >
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
                <Route path="/new-task" element={<NewTaskPage user={user} setUser={handleSetUser} />} />
                <Route path="/new-partner-task" element={<NewPartnerTaskPage user={user} setUser={handleSetUser} />} />
                <Route path="/spin-wheel" element={<SpinWheelPage user={user} setUser={handleSetUser} />} />
                <Route path="/game/space-defender" element={<SpaceDefenderPage user={user} setUser={setUser} />} />
                <Route path="/game/street-racing" element={<StreetRacingPage user={user} setUser={setUser} />} />

                <Route element={<Layout user={user} />}>
                    <Route path="/" element={<EarningsPage setUser={handleSetUser} />} />
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















