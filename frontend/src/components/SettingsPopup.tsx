import { Settings, Sun, Moon, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';

interface SettingsPopupProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsPopup = ({ isOpen, onClose }: SettingsPopupProps) => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 dark:bg-white/40"
          />
          
          {/* Popup - Canto superior esquerdo do conteúdo principal */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: -10 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: -10 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className="fixed top-24 left-80 glass-card p-6 rounded-xl border border-prunus-gold/20 w-64 z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-prunus-gold" />
                <h2 className="text-lg font-serif text-gold-gradient">Configurações</h2>
              </div>
              <button
                onClick={onClose}
                className="p-1 hover:bg-white/10 dark:hover:bg-black/10 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            {/* Theme Toggle */}
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-white/5 dark:bg-black/5 rounded-lg border border-white/10 dark:border-black/10">
                <div className="flex items-center gap-3">
                  {isDarkMode ? (
                    <Moon className="w-4 h-4 text-prunus-gold" />
                  ) : (
                    <Sun className="w-4 h-4 text-prunus-gold" />
                  )}
                  <span className="text-sm font-medium">
                    {isDarkMode ? 'Modo Escuro' : 'Modo Claro'}
                  </span>
                </div>
                <motion.button
                  onClick={toggleTheme}
                  className="relative w-12 h-6 bg-prunus-gold/30 rounded-full p-1 transition-colors hover:bg-prunus-gold/40"
                  whileTap={{ scale: 0.95 }}
                >
                  <motion.div
                    initial={false}
                    animate={{ x: isDarkMode ? 24 : 0 }}
                    className="w-4 h-4 bg-prunus-gold rounded-full"
                    transition={{ type: 'spring', damping: 15 }}
                  />
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default SettingsPopup;
