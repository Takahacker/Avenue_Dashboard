import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';

interface EvolutionPoint {
  date: string;
  value: number;
}

interface BankerCaptacao {
  nome: string;
  evolution: EvolutionPoint[];
  captacao_total: number;
  captacao_inicial: number;
  captacao_final: number;
}

interface BankerCaptacaoCardProps {
  banker: BankerCaptacao;
  color: string;
  bankerOrder?: string[];
}

interface TooltipPayload {
  value: number;
  payload: {
    date: string;
  };
}

const BankerCaptacaoCard = ({ banker, color }: BankerCaptacaoCardProps) => {
  if (!banker.evolution || banker.evolution.length === 0) {
    return null;
  }

  const variacao = banker.captacao_final - banker.captacao_inicial;
  const porcento = (banker.captacao_inicial && banker.captacao_inicial !== 0) ? ((variacao / banker.captacao_inicial) * 100).toFixed(1) : '0';
  const isPositive = variacao >= 0;

  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-prunus-green-light/80 border border-prunus-gold/30 rounded p-2 text-xs">
          <p className="text-prunus-gold font-semibold">
            ${(payload[0].value as number).toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </p>
          <p className="text-white/70 text-xs">
            {new Date((payload[0].payload as TooltipPayload['payload']).date + 'T00:00:00').toLocaleDateString('pt-BR')}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="glass-card p-6 h-80 flex flex-col rounded-xl overflow-hidden border border-white/10 hover:border-prunus-gold/30 transition-colors"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h4 className="font-semibold text-sm truncate pr-2">{banker.nome}</h4>
          <p className="text-xs text-muted-foreground mt-0.5">
            {new Date(banker.evolution[0].date + 'T00:00:00').toLocaleDateString('pt-BR')} - {new Date(banker.evolution[banker.evolution.length - 1].date + 'T00:00:00').toLocaleDateString('pt-BR')}
          </p>
        </div>
        <div className="w-2 h-8 rounded" style={{ backgroundColor: color }} />
      </div>

      {/* Chart */}
      <div className="flex-1 mb-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={banker.evolution} margin={{ top: 5, right: 5, left: -20, bottom: 20 }}>
            <defs>
              <linearGradient id={`gradient-${banker.nome}`} x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor={color} />
                <stop offset="100%" stopColor={color} stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke="rgba(255,255,255,0.2)"
              tick={{ fontSize: 9 }}
              tickFormatter={(value) => {
                const date = new Date(String(value) + 'T00:00:00');
                return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
              }}
              interval={Math.floor(banker.evolution.length / 4)}
            />
            <YAxis 
              stroke="rgba(255,255,255,0.2)"
              tick={{ fontSize: 9 }}
              tickFormatter={(value) => value !== undefined && value !== null ? `$${(Number(value) / 1000).toFixed(0)}K` : '$0K'}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-white/10">
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Inicial</p>
          <p className="text-sm font-semibold mt-1">
            ${(banker.captacao_inicial / 1000).toFixed(0)}K
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Final</p>
          <p className="text-sm font-semibold mt-1">
            ${(banker.captacao_final / 1000).toFixed(0)}K
          </p>
        </div>
        <div className={`text-center ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          <p className="text-xs text-muted-foreground">Variação</p>
          <div className="flex items-center justify-center gap-1 mt-1">
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <p className="text-sm font-semibold">
              {isPositive ? '+' : ''}{porcento}%
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default BankerCaptacaoCard;

