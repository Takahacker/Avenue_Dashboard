import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  delay?: number;
}

const MetricCard = ({ title, value, change, changeType = 'neutral', icon: Icon, delay = 0 }: MetricCardProps) => {
  const changeColors = {
    positive: 'text-green-400',
    negative: 'text-red-400',
    neutral: 'text-muted-foreground',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      className="metric-card group"
    >
      <div className="flex items-start justify-between mb-4">
        <motion.div
          className="p-3 rounded-xl bg-gradient-to-br from-prunus-gold/20 to-transparent border border-prunus-gold/20"
          whileHover={{ rotate: 5 }}
        >
          <Icon className="w-5 h-5 text-prunus-gold" />
        </motion.div>
        {change && (
          <span className={`text-sm font-medium ${changeColors[changeType]}`}>
            {changeType === 'positive' && '+'}
            {change}
          </span>
        )}
      </div>
      
      <p className="text-sm text-muted-foreground mb-1">{title}</p>
      <motion.p
        className="text-2xl font-semibold text-gold-gradient"
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.2 }}
      >
        {value}
      </motion.p>
    </motion.div>
  );
};

export default MetricCard;
