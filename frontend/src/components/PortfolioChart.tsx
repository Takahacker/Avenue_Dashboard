import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
} from 'recharts';

const data = [
  { date: '2024-12-09', value: 125000, client: 'André Guilherme' },
  { date: '2024-12-13', value: 138274, client: 'André Guilherme' },
  { date: '2024-12-17', value: 132000, client: 'André Guilherme' },
  { date: '2024-12-21', value: 128500, client: 'André Guilherme' },
  { date: '2024-12-25', value: 135000, client: 'André Guilherme' },
  { date: '2024-12-29', value: 142000, client: 'André Guilherme' },
  { date: '2025-01-01', value: 138500, client: 'André Guilherme' },
  { date: '2025-01-05', value: 145812, client: 'André Guilherme' },
  { date: '2025-01-09', value: 142000, client: 'André Guilherme' },
  { date: '2025-01-13', value: 138072, client: 'André Guilherme' },
];

const CustomTooltip = ({ active, payload, label, isDarkMode }: any) => {
  if (active && payload && payload.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card-gold p-4"
      >
        <p className={`text-xs mb-1 ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
          {new Date(label).toLocaleDateString('pt-BR')}
        </p>
        <p className="text-lg font-semibold text-gold-gradient">
          ${payload[0].value.toLocaleString('en-US')}
        </p>
      </motion.div>
    );
  }
  return null;
};

interface PortfolioChartProps {
  title: string;
  clientName: string;
}

const PortfolioChart = ({ title, clientName }: PortfolioChartProps) => {
  const { isDarkMode } = useTheme();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="glass-card p-6 chart-container h-[360px]"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">{title}</h3>
          <p className={`text-sm ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>{clientName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-prunus-gold" />
          <span className={`text-xs ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>P&L Total</span>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(39, 40%, 64%)" stopOpacity={0.4} />
                <stop offset="95%" stopColor="hsl(39, 40%, 64%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={isDarkMode ? "hsl(160, 30%, 25%)" : "hsl(160, 30%, 85%)"} 
            />
            <XAxis 
              dataKey="date" 
              stroke={isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)"}
              tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
              tick={{ fontSize: 11, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
            />
            <YAxis 
              stroke={isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)"}
              tickFormatter={(value) => value !== undefined && value !== null ? `$${(Number(value) / 1000).toFixed(0)}k` : '$0k'}
              tick={{ fontSize: 11, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
            />
            <Tooltip content={<CustomTooltip isDarkMode={isDarkMode} />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(39, 40%, 64%)"
              strokeWidth={2}
              fill="url(#colorValue)"
              animationDuration={1500}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default PortfolioChart;
