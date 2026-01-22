import { motion } from 'framer-motion';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const data = [
  { date: '2024-10-28', value: 402270 },
  { date: '2024-11-10', value: 417384 },
  { date: '2024-11-28', value: 455780 },
  { date: '2024-12-09', value: 450501 },
  { date: '2024-12-27', value: 485000 },
  { date: '2025-01-04', value: 478000 },
  { date: '2025-01-18', value: 512390 },
];

const stats = {
  max: 512390,
  min: 402270,
  media: 457332,
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card-gold p-4"
      >
        <p className="text-xs text-muted-foreground mb-1">
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

interface EvolutionChartProps {
  clientName: string;
}

const EvolutionChart = ({ clientName }: EvolutionChartProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.25 }}
      className="glass-card p-6 chart-container h-[360px]"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">Evolução de P&L</h3>
          <p className="text-sm text-muted-foreground">{clientName}</p>
        </div>
        <div className="text-right text-xs space-y-1">
          <p><span className="text-green-400">Máx:</span> ${stats.max.toLocaleString()}</p>
          <p><span className="text-prunus-gold">Média:</span> ${stats.media.toLocaleString()}</p>
          <p><span className="text-red-400">Mín:</span> ${stats.min.toLocaleString()}</p>
        </div>
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="hsl(160, 60%, 40%)" />
                <stop offset="50%" stopColor="hsl(39, 40%, 64%)" />
                <stop offset="100%" stopColor="hsl(39, 50%, 70%)" />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(160, 30%, 25%)" />
            <XAxis 
              dataKey="date" 
              stroke="hsl(0, 0%, 50%)"
              tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
              tick={{ fontSize: 10 }}
            />
            <YAxis 
              stroke="hsl(0, 0%, 50%)"
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              tick={{ fontSize: 10 }}
              domain={['dataMin - 20000', 'dataMax + 20000']}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine 
              y={stats.media} 
              stroke="hsl(39, 40%, 64%)" 
              strokeDasharray="5 5" 
              opacity={0.5}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="url(#lineGradient)"
              strokeWidth={3}
              dot={{ 
                fill: 'hsl(39, 40%, 64%)', 
                strokeWidth: 2, 
                stroke: 'hsl(160, 65%, 12%)',
                r: 5
              }}
              activeDot={{ 
                r: 8, 
                fill: 'hsl(39, 50%, 70%)',
                stroke: 'hsl(39, 40%, 64%)',
                strokeWidth: 2
              }}
              animationDuration={1500}
              animationEasing="ease-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default EvolutionChart;
