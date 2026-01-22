import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BANKER_COLORS } from '@/lib/colors';

interface BankerData {
  nome: string;
  clientes_count: number;
  evolution: Array<{ date: string; value: number }>;
  pl_inicial: number;
  pl_final: number;
  variacao: number;
}

interface BankerCardProps {
  banker: BankerData;
  bankerOrder: string[];
}

const BankerCard = ({ banker, bankerOrder }: BankerCardProps) => {
  const bankerIndex = bankerOrder.indexOf(banker.nome);
  const color = BANKER_COLORS[bankerIndex % BANKER_COLORS.length];
  
  const isPositive = banker.variacao >= 0;
  const variationPercent = banker.pl_inicial !== 0 ? ((banker.variacao / banker.pl_inicial) * 100).toFixed(2) : '0';

  // Formata dados para o gráfico
  const chartData = banker.evolution.map(item => {
    const [year, month, day] = item.date.split('-');
    return {
      ...item,
      displayDate: `${day}/${month}`,
    };
  });

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload?.[0]) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-2"
        >
          <p className="text-xs text-muted-foreground">
            {new Date(payload[0].payload.date).toLocaleDateString('pt-BR')}
          </p>
          <p className="text-xs font-semibold" style={{ color }}>
            ${payload[0].value.toLocaleString('en-US')}
          </p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card p-6 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white group-hover:text-prunus-gold transition-colors">
            {banker.nome}
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            {banker.clientes_count} cliente{banker.clientes_count !== 1 ? 's' : ''}
          </p>
        </div>
        <span className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : ''}{variationPercent}%
        </span>
      </div>

      {/* Chart */}
      <div className="h-48 -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 40, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={true} vertical={false} />
            <XAxis 
              dataKey="displayDate"
              stroke="rgba(255,255,255,0.3)"
              style={{ fontSize: '12px' }}
              interval={Math.floor(chartData.length / 6)}
            />
            <YAxis 
              stroke="rgba(255,255,255,0.3)"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-white/10">
        <div>
          <p className="text-xs text-muted-foreground mb-1">Inicial</p>
          <p className="font-semibold text-sm">
            ${(banker.pl_inicial / 1000000).toFixed(2)}M
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Atual</p>
          <p className="font-semibold text-sm">
            ${(banker.pl_final / 1000000).toFixed(2)}M
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Variação</p>
          <p className={`font-semibold text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}${(banker.variacao / 1000).toFixed(0)}K
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default BankerCard;
