import { Search } from 'lucide-react';
import { motion } from 'framer-motion';
import avenueLogo from '@/assets/avenue-logo.png';

const Header = () => {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="glass-card mb-6 p-4 flex items-center justify-between"
    >
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <img src={avenueLogo} alt="Avenue" className="h-8 w-auto" />
          <div className="h-6 w-px bg-white/20" />
          <h1 className="text-xl font-serif text-gold-gradient">Dashboard Avenue</h1>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar cliente..."
            className="w-64 pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm placeholder:text-muted-foreground focus:outline-none focus:border-prunus-gold/50 transition-colors"
          />
        </div>

        {/* Current Date */}
        <div className="text-sm text-muted-foreground">
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
