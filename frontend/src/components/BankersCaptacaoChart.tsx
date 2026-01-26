import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { fetchAPI } from '@/lib/apiConfig';
import { BANKER_COLORS } from '@/lib/colors';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  TooltipProps
} from 'recharts';

interface EvolutionPoint {
  date: string;
  value: number;
}

interface BankerCaptacaoApiData {
  nome: string;
  evolution: EvolutionPoint[];
  captacao_total: number;
  captacao_inicial: number;
  captacao_final: number;
}

interface BankerCaptacaoData {
  date: string;
  [key: string]: string | number;
}

interface BankersEvolutionChartProps {
  bankerOrder?: string[];
}

interface ChartTooltipPayload {
  name: string;
  value: number;
  color: string;
}

const BankersCaptacaoChart = ({ bankerOrder }: BankersEvolutionChartProps) => {
  const { isDarkMode } = useTheme();
  const [data, setData] = useState<BankerCaptacaoData[]>([]);
  const [bankers, setBankers] = useState<string[]>([]);
  const [selectedBankers, setSelectedBankers] = useState<string[]>([]);
  const [filterOpen, setFilterOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetchAPI('/api/bankers/captacao');
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();
        if (result.success && Array.isArray(result.data)) {
          // Formata dados para o gráfico
          const bankerNames = result.data.map((b: BankerCaptacaoApiData) => b.nome);
          
          // Usa a ordem passada via props, ou a ordem da API como fallback
          const orderedBankers = bankerOrder && bankerOrder.length > 0 ? bankerOrder : bankerNames;
          
          setBankers(orderedBankers);
          setSelectedBankers(orderedBankers); // Default: todos selecionados

          // Agrupa dados por data
          const chartData: BankerCaptacaoData[] = [];
          if (result.data.length > 0 && result.data[0].evolution) {
            const firstBanker = result.data[0];
            firstBanker.evolution.forEach((item: EvolutionPoint, index: number) => {
              const datePoint: BankerCaptacaoData = { date: item.date };
              
              result.data.forEach((banker: BankerCaptacaoApiData) => {
                if (banker.evolution && banker.evolution[index]) {
                  datePoint[banker.nome as string] = banker.evolution[index].value;
                }
              });
              
              chartData.push(datePoint);
            });
          }
          
          setData(chartData);
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
  }, [bankerOrder]);

  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-3"
        >
          <p className="text-xs text-muted-foreground mb-1">
            {new Date(String(label) + 'T00:00:00').toLocaleDateString('pt-BR')}
          </p>
          {payload.map((entry: ChartTooltipPayload, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-xs font-semibold">
              {entry.name}: ${(entry.value as number).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          ))}
        </motion.div>
      );
    }
    return null;
  };

  const toggleBanker = (banker: string) => {
    setSelectedBankers(prev =>
      prev.includes(banker)
        ? prev.filter(b => b !== banker)
        : [...prev, banker]
    );
  };

  const selectAll = () => {
    setSelectedBankers(bankers);
  };

  const clearAll = () => {
    setSelectedBankers([]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
      className="glass-card p-6 chart-container flex flex-col"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">Captação por Banker</h3>
          <p className="text-xs text-muted-foreground mt-1">Inflows positivos + PL inicial de novos clientes - Período de 01/12/2025 a 20/01/2026</p>
        </div>
        
        {/* Filtro de Bankers */}
        <div className="relative">
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm transition-all"
          >
            <span>Bankers ({selectedBankers.length}/{bankers.length})</span>
            <ChevronDown size={16} className={`transition-transform ${filterOpen ? 'rotate-180' : ''}`} />
          </button>

          {filterOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 mt-2 w-80 rounded-lg border border-prunus-gold/20 bg-prunus-green-light/30 backdrop-blur-md p-4 z-50 shadow-lg"
            >
              <div className="flex gap-2 mb-3 pb-3 border-b border-prunus-gold/20">
                <button
                  onClick={selectAll}
                  className="text-xs px-3 py-1.5 rounded bg-prunus-gold text-prunus-green-dark font-semibold hover:bg-prunus-gold/90 transition-all"
                >
                  Todos
                </button>
                <button
                  onClick={clearAll}
                  className="text-xs px-3 py-1.5 rounded bg-prunus-green-light/50 hover:bg-prunus-green-light/70 transition-all border border-prunus-gold/30"
                >
                  Limpar
                </button>
              </div>

              <div className="space-y-3 max-h-72 overflow-y-auto scrollbar-thin">
                {bankers.map((banker) => (
                  <label key={banker} className="flex items-center gap-3 cursor-pointer text-sm p-2 rounded hover:bg-prunus-green-light/40 transition-colors group">
                    <input
                      type="checkbox"
                      checked={selectedBankers.includes(banker)}
                      onChange={() => toggleBanker(banker)}
                    />
                    <span className="truncate group-hover:text-prunus-gold">{banker}</span>
                  </label>
                ))}
              </div>
            </motion.div>
          )}
        </div>

        {loading && <p className="text-xs text-muted-foreground">Carregando...</p>}
        {error && <p className="text-xs text-red-400">{error}</p>}
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
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={data} margin={{ top: 10, right: 30, left: 40, bottom: 80 }}>
            <defs>
              {BANKER_COLORS.map((color, i) => (
                <linearGradient key={`grad-${i}`} id={`grad-${i}`} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor={color} />
                  <stop offset="100%" stopColor={color} stopOpacity={0.5} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? "rgba(255,255,255,0.1)" : "rgba(45, 95, 63, 0.15)"} vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke={isDarkMode ? "rgba(255,255,255,0.3)" : "rgba(45, 95, 63, 0.5)"}
              tickFormatter={(value) => {
                const date = new Date(String(value) + 'T00:00:00');
                return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
              }}
              tick={{ fontSize: 10, fill: isDarkMode ? "rgba(255,255,255,0.6)" : "rgba(45, 95, 63, 0.7)" }}
            />
            <YAxis 
              stroke={isDarkMode ? "rgba(255,255,255,0.3)" : "rgba(45, 95, 63, 0.5)"}
              tickFormatter={(value) => value !== undefined && value !== null ? `$${(Number(value) / 1000).toFixed(0)}K` : '$0K'}
              tick={{ fontSize: 10, fill: isDarkMode ? "rgba(255,255,255,0.6)" : "rgba(45, 95, 63, 0.7)" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }}
              iconType="line"
              height={80}
            />
            {bankers.map((banker, index) => (
              selectedBankers.includes(banker) && (
                <Line
                  key={banker}
                  type="monotone"
                  dataKey={banker}
                  stroke={BANKER_COLORS[index % BANKER_COLORS.length]}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={true}
                />
              )
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </motion.div>
  );
};

export default BankersCaptacaoChart;

