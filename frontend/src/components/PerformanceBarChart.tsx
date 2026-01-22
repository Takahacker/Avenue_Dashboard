import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell 
} from 'recharts';
import { useState } from 'react';

const data = [
  { month: 'Jul', income: 32000, expense: 18000 },
  { month: 'Ago', income: 28000, expense: 22000 },
  { month: 'Set', income: 45000, expense: 15000 },
  { month: 'Out', income: 38000, expense: 28000 },
  { month: 'Nov', income: 52000, expense: 20000 },
  { month: 'Dez', income: 48000, expense: 35000 },
  { month: 'Jan', income: 55000, expense: 25000 },
];

const CustomTooltip = ({ active, payload, label, isDarkMode }: any) => {
  if (active && payload && payload.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card-gold p-4"
      >
        <p className={`text-xs mb-2 ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>{label}</p>
        <div className="space-y-1">
          <p className="text-sm">
            <span className="text-prunus-gold">●</span> Entrada: ${payload[0]?.value.toLocaleString()}
          </p>
          <p className="text-sm">
            <span className="text-prunus-green-light">●</span> Saída: ${payload[1]?.value.toLocaleString()}
          </p>
        </div>
      </motion.div>
    );
  }
  return null;
};

const PerformanceBarChart = () => {
  const { isDarkMode } = useTheme();
  const [hoveredBar, setHoveredBar] = useState<number | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.35 }}
      className="glass-card p-6 chart-container h-[400px]"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">Captação no Período</h3>
          <p className={`text-sm ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>Entradas e saídas mensais</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-prunus-gold" />
            <span className={`text-xs ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>Entrada</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-prunus-green-light" />
            <span className={`text-xs ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>Saída</span>
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={data} 
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            onMouseMove={(state) => {
              if (state?.activeTooltipIndex !== undefined) {
                setHoveredBar(state.activeTooltipIndex);
              }
            }}
            onMouseLeave={() => setHoveredBar(null)}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={isDarkMode ? "hsl(160, 30%, 25%)" : "hsl(160, 30%, 85%)"} 
            />
            <XAxis 
              dataKey="month" 
              stroke={isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)"}
              tick={{ fontSize: 11, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
            />
            <YAxis 
              stroke={isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)"}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              tick={{ fontSize: 11, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
            />
            <Tooltip 
              content={<CustomTooltip isDarkMode={isDarkMode} />} 
              cursor={{ fill: isDarkMode ? 'hsl(160, 30%, 20%)' : 'hsl(160, 30%, 85%)' }} 
            />
            <Bar 
              dataKey="income" 
              radius={[4, 4, 0, 0]}
              animationDuration={1200}
              animationEasing="ease-out"
            >
              {data.map((_, index) => (
                <Cell
                  key={`income-${index}`}
                  fill={hoveredBar === index ? 'hsl(39, 50%, 70%)' : 'hsl(39, 40%, 64%)'}
                  style={{ transition: 'fill 0.3s ease' }}
                />
              ))}
            </Bar>
            <Bar 
              dataKey="expense" 
              radius={[4, 4, 0, 0]}
              animationDuration={1200}
              animationEasing="ease-out"
              animationBegin={200}
            >
              {data.map((_, index) => (
                <Cell
                  key={`expense-${index}`}
                  fill={hoveredBar === index ? 'hsl(160, 55%, 40%)' : 'hsl(160, 45%, 30%)'}
                  style={{ transition: 'fill 0.3s ease' }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default PerformanceBarChart;
