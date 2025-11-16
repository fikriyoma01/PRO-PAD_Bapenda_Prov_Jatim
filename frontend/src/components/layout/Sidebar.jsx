import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Database,
  LineChart,
  TrendingUp,
  BarChart3,
  Lightbulb,
  Settings,
  FileText,
  Users,
  Layers,
  Edit,
  CheckSquare,
  BookOpen,
  Activity,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '../../lib/utils';

const navigationItems = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'Datasets', path: '/datasets', icon: Database },
  { name: 'Pemodelan', path: '/pemodelan', icon: LineChart },
  { name: 'Proyeksi', path: '/proyeksi', icon: TrendingUp },
  { name: 'Dekomposisi', path: '/dekomposisi', icon: BarChart3 },
  { name: 'Insight', path: '/insight', icon: Lightbulb },
  { name: 'HKPD', path: '/hkpd', icon: FileText },
  { name: 'Scenario Builder', path: '/scenario-builder', icon: Layers },
  { name: 'Decision Support', path: '/decision-support', icon: CheckSquare },
];

const settingsItems = [
  { name: 'UI Customization', path: '/ui-customization', icon: Settings },
  { name: 'Variable Manager', path: '/variable-manager', icon: Edit },
  { name: 'Policy Settings', path: '/policy-settings', icon: Users },
  { name: 'Data Editor', path: '/data-editor', icon: Database },
];

const otherItems = [
  { name: 'Metodologi', path: '/metodologi', icon: BookOpen },
  { name: 'Audit', path: '/audit', icon: Activity },
];

export default function Sidebar({ isOpen, onToggle }) {
  const location = useLocation();

  const NavItem = ({ item }) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.path;

    return (
      <Link
        to={item.path}
        className={cn(
          'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors duration-200',
          isActive
            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
            : 'text-gray-700 hover:bg-gray-100'
        )}
      >
        <Icon size={20} />
        <span className="text-sm font-medium">{item.name}</span>
      </Link>
    );
  };

  return (
    <>
      {/* Sidebar */}
      <aside
        className={cn(
          'bg-white border-r border-gray-200 transition-all duration-300 flex flex-col',
          isOpen ? 'w-64' : 'w-0 overflow-hidden'
        )}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="gradient-header text-white px-4 py-3 rounded-lg text-center">
            <h1 className="text-xl font-bold">PRO-PAD</h1>
            <p className="text-xs opacity-90">Bapenda Prov Jatim</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Main Navigation */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
              Analisis
            </h3>
            <div className="space-y-1">
              {navigationItems.map((item) => (
                <NavItem key={item.path} item={item} />
              ))}
            </div>
          </div>

          {/* Settings */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
              Pengaturan
            </h3>
            <div className="space-y-1">
              {settingsItems.map((item) => (
                <NavItem key={item.path} item={item} />
              ))}
            </div>
          </div>

          {/* Other */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
              Lainnya
            </h3>
            <div className="space-y-1">
              {otherItems.map((item) => (
                <NavItem key={item.path} item={item} />
              ))}
            </div>
          </div>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            © 2024 Bapenda Jatim
          </div>
        </div>
      </aside>
    </>
  );
}
