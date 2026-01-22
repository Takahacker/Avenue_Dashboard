import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface ClientEvolution {
  nome: string;
  banker: string;
  email: string;
  pl_inicial: number;
  pl_final: number;
  variacao: number;
  evolution: Array<{ date: string; value: number }>;
}

interface ClientCardProps {
  client: ClientEvolution;
  delay?: number;
}

const ClientCard = ({ client, delay = 0 }: ClientCardProps) => {
  const isPositive = client.variacao >= 0;
  const variationPercent = client.pl_inicial !== 0 
    ? ((client.variacao / client.pl_inicial) * 100).toFixed(2)
    : '0.00';

  // Verifica se é novo cliente (primeira data não é 2025-12-01)
  const firstDate = client.evolution[0]?.date || '';
  const isNewClient = firstDate !== '2025-12-01';

  const formatValue = (value: number) => {
    return '$' + value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  };

  const formatDate = (dateString: string) => {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
  };

  // Formata dados para o gráfico
  const chartData = client.evolution.map(item => {
    const [year, month, day] = item.date.split('-');
    return {
      ...item,
      displayDate: `${day}/${month}`,
    };
  });

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-black/40 border border-white/20 rounded-lg p-2 backdrop-blur-sm">
          <p className="text-xs text-gold-gradient">{data.date}</p>
          <p className="text-sm font-semibold text-white">
            ${data.value.toLocaleString('en-US')}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.02 }}
      className="glass-card p-6 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white group-hover:text-prunus-gold transition-colors">
            {client.nome}
          </h3>
          <p className="text-xs text-muted-foreground mt-1">{client.banker}</p>
          <p className="text-xs text-muted-foreground">{client.email}</p>
        </div>
        <div className="flex flex-col items-end gap-3">
          {isNewClient && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: delay + 0.2 }}
              className="bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg px-3 py-1 text-xs font-medium whitespace-nowrap"
            >
              <div>NOVO cliente</div>
              <div className="text-xs opacity-80">{formatDate(firstDate)}</div>
            </motion.div>
          )}
          <div className="flex items-center gap-2">
            {isPositive ? (
              <TrendingUp className="w-5 h-5 text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
            <span className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
              {isPositive ? '+' : ''}{variationPercent}%
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-48 -mx-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 40, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
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
              stroke="#D4AF37"
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
          <p className="font-semibold text-sm">{formatValue(client.pl_inicial)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Atual</p>
          <p className="font-semibold text-sm">{formatValue(client.pl_final)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Variação</p>
          <p className={`font-semibold text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}{formatValue(client.variacao)}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ClientCard;
