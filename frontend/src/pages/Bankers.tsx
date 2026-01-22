import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import BankersEvolutionChart from '../components/BankersEvolutionChart';
import BankerCard from '../components/BankerCard';
import BankersCaptacaoChart from '../components/BankersCaptacaoChart';
import { BANKER_COLORS } from '@/lib/colors';

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

interface BankerPL {
  nome: string;
  clientes_count: number;
  evolution: EvolutionPoint[];
  pl_inicial: number;
  pl_final: number;
  variacao: number;
}

const Bankers = () => {
  const [bankersCaptacao, setBankersCaptacao] = useState<BankerCaptacao[]>([]);
  const [bankersPL, setBankersPL] = useState<BankerPL[]>([]);
  const [allBankersInOrder, setAllBankersInOrder] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'captacao' | 'pl'>('captacao');

  useEffect(() => {
    const fetchBankers = async () => {
      try {
        setLoading(true);
        
        // Fetch ambos os endpoints em paralelo
        const [captacaoRes, plRes] = await Promise.all([
          fetch('http://localhost:8000/api/bankers/captacao?t=' + Date.now()),
          fetch('http://localhost:8000/api/bankers/evolution?t=' + Date.now())
        ]);
        
        if (!captacaoRes.ok || !plRes.ok) {
          throw new Error(`Erro ao carregar dados`);
        }

        const captacaoResult = await captacaoRes.json();
        const plResult = await plRes.json();
        
        if (captacaoResult.success && Array.isArray(captacaoResult.data) &&
            plResult.success && Array.isArray(plResult.data)) {
          
          // Guarda a ordem original da API (usar ambas para garantir consistência)
          const captacaoOrder = captacaoResult.data.map(b => b.nome);
          const plOrder = plResult.data.map(b => b.nome);
          
          // Usa a ordem de P&L como referência (mais consistente)
          setAllBankersInOrder(plOrder);
          
          // Ordena bankers por captação final decrescente
          const sortedCaptacao = [...captacaoResult.data].sort((a, b) => b.captacao_final - a.captacao_final);
          setBankersCaptacao(sortedCaptacao);
          
          // Ordena bankers por P&L final decrescente
          const sortedPL = [...plResult.data].sort((a, b) => b.pl_final - a.pl_final);
          setBankersPL(sortedPL);
          
          setError(null);
        } else {
          throw new Error('Formato inválido da API');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
        console.error('❌ Erro ao carregar bankers:', errorMsg);
        setError(errorMsg);
        setBankersCaptacao([]);
        setBankersPL([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBankers();
  }, []);

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center h-96"
      >
        <p className="text-muted-foreground">Carregando dados dos bankers...</p>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center h-96"
      >
        <p className="text-red-400">Erro: {error}</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Tabs para alternar entre Captação e P&L */}
      <div className="flex gap-4 border-b border-white/10">
        <button
          onClick={() => setActiveTab('captacao')}
          className={`px-4 py-3 font-medium text-sm transition-all relative ${
            activeTab === 'captacao'
              ? 'text-prunus-gold'
              : 'text-muted-foreground hover:text-white'
          }`}
        >
          Captação
          {activeTab === 'captacao' && (
            <motion.div
              layoutId="tab-indicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-prunus-gold"
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab('pl')}
          className={`px-4 py-3 font-medium text-sm transition-all relative ${
            activeTab === 'pl'
              ? 'text-prunus-gold'
              : 'text-muted-foreground hover:text-white'
          }`}
        >
          P&L
          {activeTab === 'pl' && (
            <motion.div
              layoutId="tab-indicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-prunus-gold"
            />
          )}
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'captacao' ? (
          <motion.div
            key="captacao"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Gráfico Grande de Captação */}
            <BankersCaptacaoChart bankerOrder={allBankersInOrder} />
          </motion.div>
        ) : (
          <motion.div
            key="pl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Gráfico Grande de P&L */}
            <BankersEvolutionChart bankerOrder={allBankersInOrder} />

            {/* Cards de P&L por Banker */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h2 className="text-lg font-serif text-gold-gradient mb-4">P&L por Banker</h2>
              
              <div className="text-xs text-muted-foreground mb-4">
                {bankersPL.length} banker{bankersPL.length !== 1 ? 's' : ''} cadastrado{bankersPL.length !== 1 ? 's' : ''}
              </div>

              <AnimatePresence>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {bankersPL.map((banker) => (
                    <BankerCard key={banker.nome} banker={banker} bankerOrder={allBankersInOrder} />
                  ))}
                </div>
              </AnimatePresence>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default Bankers;
