import { LayoutDashboard, Users, TrendingUp, PieChart, Briefcase, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import prunusLogo from '@/assets/prunus-logo.png';
import prunusLogoLight from '@/assets/Prunus_light_mode.png';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onSettingsClick?: () => void;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'clients', label: 'Clientes', icon: Users },
  { id: 'bankers', label: 'Bankers', icon: Briefcase },
];

const Sidebar = ({ activeTab, onTabChange, onSettingsClick }: SidebarProps) => {
  const { isDarkMode } = useTheme();

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sidebar-glass fixed left-0 top-0 h-screen w-64 flex flex-col z-50"
    >
      {/* Logo Section */}
      <div className={`p-6 ${isDarkMode ? 'border-white/10' : 'border-black/10'} border-b`}>
        <motion.img
          src={isDarkMode ? prunusLogo : prunusLogoLight}
          alt="Prunus Asset"
          className="h-12 w-auto"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        />
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`nav-item w-full ${isActive ? 'active' : ''}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </motion.button>
          );
        })}
      </nav>

      {/* Settings Button at Bottom */}
      <div className={`p-4 ${isDarkMode ? 'border-white/10' : 'border-black/10'} border-t`}>
        <motion.button
          className={`nav-item w-full ${isDarkMode ? 'text-muted-foreground hover:text-prunus-gold' : 'text-gray-600 hover:text-prunus-gold'}`}
          whileHover={{ x: 4 }}
          whileTap={{ scale: 0.98 }}
          onClick={onSettingsClick}
        >
          <Settings className="w-5 h-5" />
          <span>Configurações</span>
        </motion.button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
