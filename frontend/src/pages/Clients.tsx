import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, X } from 'lucide-react';
import ClientCard from '@/components/ClientCard';

interface ClientEvolution {
  nome: string;
  banker: string;
  email: string;
  pl_inicial: number;
  pl_final: number;
  variacao: number;
  evolution: Array<{ date: string; value: number }>;
}

const ClientsView = () => {
  const [clients, setClients] = useState<ClientEvolution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBanker, setSelectedBanker] = useState<string>('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [filterNewClients, setFilterNewClients] = useState(false);

  useEffect(() => {
    const fetchClientsEvolution = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/clients/evolution?t=' + Date.now());
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
          setClients(result.data);
          setError(null);
        } else {
          throw new Error('Formato inválido da API');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
        console.error('❌ Erro:', errorMsg);
        setError(errorMsg);
        setClients([]);
      } finally {
        setLoading(false);
      }
    };

    fetchClientsEvolution();
  }, []);

  // Pega lista única de bankers
  const uniqueBankers = Array.from(new Set(clients.map(c => c.banker))).sort();

  // Filtra clientes por banker selecionado e novo cliente
  const filteredClients = clients.filter(c => {
    const matchesBanker = !selectedBanker || c.banker === selectedBanker;
    const isNewClient = c.evolution[0]?.date !== '2025-12-01';
    const matchesNewClientFilter = !filterNewClients || isNewClient;
    return matchesBanker && matchesNewClientFilter;
  });

  return (
    <div className="w-full">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-6"
      >
        <h2 className="text-2xl font-bold text-white mb-2">Evolução de PL por Cliente</h2>
        <p className="text-sm text-muted-foreground">
          Acompanhe a evolução do Patrimônio Líquido de cada cliente no período de 01/12/2025 a 20/01/2026
        </p>
      </motion.div>

      {/* Filter Section */}
      {!loading && clients.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6"
        >
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gold-gradient">Banker:</span>
            
            {/* Dropdown Button */}
            <div className="relative">
              <motion.button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  selectedBanker || isDropdownOpen
                    ? 'bg-prunus-gold/30 text-prunus-gold border border-prunus-gold/50'
                    : 'bg-white/5 text-muted-foreground border border-white/10 hover:bg-white/10'
                }`}
              >
                <span className="truncate">
                  {selectedBanker || 'Selecionar...'}
                </span>
                <motion.div
                  animate={{ rotate: isDropdownOpen ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-4 h-4" />
                </motion.div>
              </motion.button>

              {/* Dropdown Menu */}
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full left-0 mt-2 w-64 glass-card rounded-lg p-3 z-50 shadow-lg"
                  >
                    {/* All option */}
                    <motion.button
                      onClick={() => {
                        setSelectedBanker('');
                        setIsDropdownOpen(false);
                      }}
                      whileHover={{ x: 4 }}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-all mb-2 ${
                        !selectedBanker
                          ? 'bg-prunus-gold/20 text-prunus-gold'
                          : 'text-muted-foreground hover:bg-white/5'
                      }`}
                    >
                      Todos
                    </motion.button>

                    {/* Banker options */}
                    {uniqueBankers.map((banker) => (
                      <motion.button
                        key={banker}
                        onClick={() => {
                          setSelectedBanker(banker);
                          setIsDropdownOpen(false);
                        }}
                        whileHover={{ x: 4 }}
                        className={`w-full text-left px-3 py-2 rounded-lg transition-all mb-2 last:mb-0 ${
                          selectedBanker === banker
                            ? 'bg-prunus-gold/20 text-prunus-gold'
                            : 'text-muted-foreground hover:bg-white/5'
                        }`}
                      >
                        {banker}
                      </motion.button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Clear Filter Button */}
            {selectedBanker && (
              <motion.button
                onClick={() => setSelectedBanker('')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-lg bg-white/5 text-muted-foreground hover:text-red-400 border border-white/10 hover:border-red-400/30 transition-all"
              >
                <X className="w-4 h-4" />
              </motion.button>
            )}

            {/* New Client Checkbox */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="newClientFilter"
                checked={filterNewClients}
                onChange={(e) => setFilterNewClients(e.target.checked)}
                className="w-4 h-4 rounded cursor-pointer appearance-none bg-white/5 border border-white/20 checked:bg-prunus-gold/30 checked:border-prunus-gold/50 transition-all"
              />
              <label htmlFor="newClientFilter" className="text-sm font-medium text-gold-gradient cursor-pointer">
                Novo cliente
              </label>
            </div>
          </div>
        </motion.div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Carregando dados dos clientes...</p>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-96">
          <p className="text-red-400">Erro: {error}</p>
        </div>
      ) : filteredClients.length === 0 ? (
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">
            {selectedBanker ? `Nenhum cliente encontrado para ${selectedBanker}` : 'Sem dados disponíveis'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredClients.map((client, index) => (
            <ClientCard key={client.nome} client={client} delay={0.05 * index} />
          ))}
        </div>
      )}

      {/* Results Counter */}
      {!loading && clients.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 text-center text-sm text-muted-foreground"
        >
          Mostrando {filteredClients.length} de {clients.length} cliente{clients.length !== 1 ? 's' : ''}
        </motion.div>
      )}
    </div>
  );
};

export default ClientsView;
