import { Link, useLocation } from 'react-router-dom';
import { Home as HomeIcon, LayoutDashboard, LineChart, Database } from 'lucide-react';
import clsx from 'clsx';

export default function Navbar() {
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/', icon: HomeIcon },
    { name: 'Planner', path: '/planner', icon: LayoutDashboard },
    { name: 'Scenarios', path: '/scenarios', icon: LineChart },
    { name: 'Insights', path: '/insights', icon: Database },
  ];

  return (
    <nav className="bg-brand-700 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center gap-2">
              <span className="font-bold text-xl tracking-tight">HomeGoal AI</span>
            </Link>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-4">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path || (link.path !== '/' && location.pathname.startsWith(link.path));
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={clsx(
                    "px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors",
                    isActive 
                      ? "bg-brand-800 text-white" 
                      : "text-brand-100 hover:bg-brand-600 hover:text-white"
                  )}
                >
                  <Icon size={18} />
                  {link.name}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Mobile nav (bottom bar style) */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 bg-white shadow-[0_-2px_10px_rgba(0,0,0,0.1)] z-50 border-t border-gray-200">
        <div className="flex justify-around items-center h-16">
           {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path || (link.path !== '/' && location.pathname.startsWith(link.path));
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={clsx(
                    "flex flex-col items-center justify-center w-full h-full space-y-1 transition-colors",
                    isActive ? "text-brand-700" : "text-gray-500 hover:text-gray-900"
                  )}
                >
                  <Icon size={20} />
                  <span className="text-[10px] font-medium">{link.name}</span>
                </Link>
              );
            })}
        </div>
      </div>
    </nav>
  );
}
