'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { user } = useAuth();

  if (!user) {
    return null; // Hide sidebar if not authenticated
  }

  // Define navigation items based on user role
  const navItems = [
    { href: '/dashboard', label: 'داشبورد', roles: ['ADMIN', 'OPERATOR', 'REPRESENTATIVE'] },
    { href: '/representatives', label: 'نمایندگان', roles: ['ADMIN', 'OPERATOR'] },
    { href: '/invoices', label: 'فاکتورها', roles: ['ADMIN', 'OPERATOR', 'REPRESENTATIVE'] },
    { href: '/accounting', label: 'حسابداری', roles: ['ADMIN'] },
    { href: '/settings', label: 'تنظیمات', roles: ['ADMIN'] },
  ];

  const filteredNavItems = navItems.filter(item => item.roles.includes(user.role));

  return (
    <aside className="w-64 bg-white border-l border-gray-200 h-screen fixed top-0 right-0 p-4 flex flex-col">
      <div className="mb-8 text-xl font-bold text-black">پنل مدیریت</div>
      <nav className="flex flex-col space-y-4">
        {filteredNavItems.map((item) => (
          <Link key={item.href} href={item.href}>
            <span
              className={`block px-4 py-2 rounded text-black hover:bg-gray-100 transition cursor-pointer ${
                pathname === item.href ? 'bg-gray-200 font-semibold' : ''
              }`}
            >
              {item.label}
            </span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
