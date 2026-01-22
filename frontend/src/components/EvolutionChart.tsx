import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';

interface ChartData {
  date: string;
  value: number;
}

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

interface EvolutionChartProps {
  clientName: string;
}

const EvolutionChart = ({ clientName }: EvolutionChartProps) => {
  const { isDarkMode } = useTheme();
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/pl/total?t=' + Date.now());
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          // Filtra APENAS dados de 2025-12-01 em diante e soma 1 dia em cada data
          const filtered = result.data
            .filter((item: ChartData) => item.date >= '2025-12-01')
            .map((item: ChartData) => ({
              ...item,
              // Soma 1 dia na data para corrigir offset
              date: new Date(new Date(item.date).getTime() + 86400000).toISOString().split('T')[0]
            }));
          
          if (filtered.length === 0) {
            throw new Error('Nenhum dado válido encontrado');
          }

          console.log('✅ Dados carregados:', {
            total: filtered.length,
            primeira: filtered[0].date,
            ultima: filtered[filtered.length - 1].date
          });

          setData(filtered);
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.25 }}
      className="glass-card p-6 chart-container h-[360px]"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">Total de PL</h3>
        </div>
        {loading && (
          <p className="text-xs text-muted-foreground">Carregando...</p>
        )}
        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}
      </div>

      <div className="h-48">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">Carregando gráfico...</p>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-red-400">Erro: {error}</p>
          </div>
        ) : data.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">Sem dados disponíveis</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="hsl(160, 60%, 40%)" />
                  <stop offset="50%" stopColor="hsl(39, 40%, 64%)" />
                  <stop offset="100%" stopColor="hsl(39, 50%, 70%)" />
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
                tick={{ fontSize: 10, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
              />
              <YAxis 
                stroke={isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)"}
                tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
                tick={{ fontSize: 10, fill: isDarkMode ? "hsl(0, 0%, 50%)" : "hsl(160, 20%, 40%)" }}
                domain={['dataMin - 100000', 'dataMax + 100000']}
              />
              <Tooltip content={<CustomTooltip isDarkMode={isDarkMode} />} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="url(#lineGradient)"
                strokeWidth={3}
                dot={{ 
                  fill: 'hsl(39, 40%, 64%)', 
                  strokeWidth: 2, 
                  stroke: isDarkMode ? 'hsl(160, 65%, 12%)' : 'hsl(0, 0%, 100%)',
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
        )}
      </div>
    </motion.div>
  );
};

export default EvolutionChart;
