import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { fetchAPI } from '@/lib/apiConfig';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  TooltipProps
} from 'recharts';

interface EvolutionPoint {
  date: string;
  value: number;
}

interface ChartTooltipPayload {
  value: number;
  date: string;
}

const CaptacaoEvolutionChart = () => {
  const { isDarkMode } = useTheme();
  const [data, setData] = useState<EvolutionPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [captacaoTotal, setCaptacaoTotal] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetchAPI('/api/captacao/evolucao');
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();
        if (result.success && Array.isArray(result.data)) {
          setData(result.data);
          setCaptacaoTotal(result.captacao_total || 0);
          setError(null);
        } else {
          throw new Error('Formato inválido da API');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
        console.error('❌ Erro:', errorMsg);
        setError(errorMsg);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload[0]) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-3"
        >
          <p className="text-xs text-muted-foreground mb-1">
            {new Date(String(payload[0].payload.date) + 'T00:00:00').toLocaleDateString('pt-BR')}
          </p>
          <p className="text-xs font-semibold text-prunus-gold">
            ${(payload[0].value as number).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
      transition={{ duration: 0.6, delay: 0.1 }}
      className="glass-card p-6 chart-container flex flex-col"
    >
      <div className="mb-4">
        <h3 className="text-lg font-serif text-gold-gradient">Captação no Período</h3>
        <p className="text-xs text-muted-foreground mt-1">Entradas e saídas/mês</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-80">
          <p className="text-muted-foreground">Carregando gráfico...</p>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-80">
          <p className="text-red-400">Erro: {error}</p>
        </div>
      ) : data.length === 0 ? (
        <div className="flex items-center justify-center h-80">
          <p className="text-muted-foreground">Sem dados disponíveis</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 40, bottom: 40 }}>
            <defs>
              <linearGradient id="colorCapt" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2d5f3f" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2d5f3f" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? "rgba(255,255,255,0.1)" : "rgba(45, 95, 63, 0.15)"} vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke={isDarkMode ? "rgba(255,255,255,0.3)" : "rgba(45, 95, 63, 0.5)"}
              tickFormatter={(value) => {
                const date = new Date(String(value) + 'T00:00:00');
                return `${date.getDate()}/${date.getMonth() + 1}`;
              }}
              tick={{ fontSize: 10, fill: isDarkMode ? "rgba(255,255,255,0.6)" : "rgba(45, 95, 63, 0.7)" }}
              interval={Math.floor(data.length / 8)}
            />
            <YAxis 
              stroke={isDarkMode ? "rgba(255,255,255,0.3)" : "rgba(45, 95, 63, 0.5)"}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
              tick={{ fontSize: 10, fill: isDarkMode ? "rgba(255,255,255,0.6)" : "rgba(45, 95, 63, 0.7)" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#d4af37"
              strokeWidth={2.5}
              fill="url(#colorCapt)"
              isAnimationActive={true}
              animationDuration={800}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </motion.div>
  );
};

export default CaptacaoEvolutionChart;
