import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import BottomNav from './BottomNav';
import type { User } from '../types';

interface LayoutProps {
  // By changing this from `User | null` to just `User`, we are creating a contract.
  // We are telling this component: "You will ALWAYS receive a valid user object.
  // You do not need to check if it's null."
  // The guard clause in App.tsx enforces this contract.
  user: User;
}

const Layout: React.FC<LayoutProps> = ({ user }) => {
  return (
    <>
      {/* Now it's safe to pass the user prop down without any checks,
          because we know it's not null. */}
      <Header user={user} />
      <main className="pt-20 pb-24 px-4">
        <Outlet />
      </main>
      <BottomNav />
    </>
  );
};

export default Layout;