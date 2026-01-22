import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import avenueLogo from '@/assets/avenue-logo.png';
import avenueLogoLight from '@/assets/Avenue_light_mode.png';

const Header = () => {
  const { isDarkMode } = useTheme();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="glass-card mb-6 p-4 flex items-center justify-between"
    >
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <img src={isDarkMode ? avenueLogo : avenueLogoLight} alt="Avenue" className="h-8 w-auto" />
          <div className={`h-6 w-px ${isDarkMode ? 'bg-white/20' : 'bg-black/10'}`} />
          <div>
            <h1 className="text-xl font-serif text-gold-gradient">Dashboard Avenue</h1>
            <p className={`text-xs ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>período de 01/12/2025 a 30/01/2026</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Current Date */}
        <div className={`text-sm ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
          {new Date().toLocaleDateString('pt-BR', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
          })}
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
