import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, MoreHorizontal } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface ClientData {
  nome: string;
  cpf: string;
  banker: string;
  email: string;
  pl: number;
  data: string;
}

// Mapeamento de perfil por nome do cliente
const clientProfiles: Record<string, string> = {
  'Adilson Ferreira da Silva Junior': 'Low-Risk Portfolio',
  'Andre luis costa': 'Balanced-Risk Portfolio',
  'BRUNA PAIVA SBOARINI': 'Low-Risk Portfolio',
  'EDUARDO SBOARINI': 'Low-Risk Portfolio',
  'Ettore Vasconcellos Paiola': 'Aggressive-Risk Portfolio',
  'MARIA ALICE AMADO GOUVEIA VENTURINI': 'Bonds',
  'Mara Silvia Porto Vilela': 'Low-Risk Portfolio',
  'SILVIO LUIZ VENTURINI': 'Low-Risk Portfolio',
  'Wanderley Crestoni Fernandes': 'Conservador PF',
  'Jones Antonio Pagno': 'Low-Risk Portfolio',
  'Agel Gustavo Turim': 'Balanced-Risk Portfolio',
};

const allocationColors: Record<string, string> = {
  'Low-Risk Portfolio': 'bg-green-500/20 text-green-400 border-green-500/30',
  'Balanced-Risk Portfolio': 'bg-prunus-gold/20 text-prunus-gold border-prunus-gold/30',
  'Aggressive-Risk Portfolio': 'bg-red-500/20 text-red-400 border-red-500/30',
  'Bonds': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Conservador PF': 'bg-green-500/20 text-green-400 border-green-500/30',
};

const ClientsTable = () => {
  const { isDarkMode } = useTheme();
  const [clients, setClients] = useState<ClientData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastDate, setLastDate] = useState<string>('');

  useEffect(() => {
    const fetchClients = async () => {
      try {
        setLoading(true);
        const response = await fetchAPI('/api/clients/pl');
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && Array.isArray(result.data)) {
          setClients(result.data);
          setLastDate(result.lastDate);
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

    fetchClients();
  }, []);
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
      className="glass-card p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-serif text-gold-gradient">Clientes Avenue</h3>
          <p className={`text-sm ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>P&L dos clientes - {lastDate ? new Date(lastDate).toLocaleDateString('pt-BR') : 'Carregando...'}</p>
        </div>
        <motion.button
          className="px-4 py-2 rounded-xl glass-card-gold text-sm font-medium"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Ver Todos
        </motion.button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className={isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}>Carregando dados...</p>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-red-400">Erro: {error}</p>
        </div>
      ) : clients.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <p className={isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}>Sem dados disponíveis</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className={`border-b ${isDarkMode ? 'border-white/10' : 'border-black/10'}`}>
                <th className={`text-left py-3 px-4 text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
                  Cliente
                </th>
                <th className={`text-left py-3 px-4 text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
                  Banker
                </th>
                <th className={`text-left py-3 px-4 text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
                  Perfil
                </th>
                <th className={`text-left py-3 px-4 text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>
                  P&L em {lastDate ? new Date(lastDate).toLocaleDateString('pt-BR') : 'carregando...'}
                </th>
                <th className="text-right py-3 px-4"></th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client, index) => (
                <motion.tr
                  key={client.cpf}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className={`border-b transition-colors cursor-pointer group ${isDarkMode ? 'border-white/5 hover:bg-white/5' : 'border-black/5 hover:bg-black/5'}`}
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-prunus-gold/30 to-prunus-green-light/30 flex items-center justify-center border border-prunus-gold/20">
                        <span className="text-sm font-medium">
                          {client.nome.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium group-hover:text-prunus-gold transition-colors">
                          {client.nome}
                        </p>
                        <p className={`text-xs ${isDarkMode ? 'text-muted-foreground' : 'text-gray-600'}`}>{client.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-sm">{client.banker}</span>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`text-xs px-3 py-1 rounded-full border inline-block ${clientProfiles[client.nome] ? allocationColors[clientProfiles[client.nome]] || 'bg-gray-500/20 text-gray-400' : 'bg-gray-500/20 text-gray-400'}`}>
                      {clientProfiles[client.nome] || 'N/A'}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className="font-semibold">
                      ${client.pl.toLocaleString('en-US')}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <motion.button
                      className={`p-2 rounded-lg transition-colors opacity-0 group-hover:opacity-100 ${isDarkMode ? 'hover:bg-white/10' : 'hover:bg-black/10'}`}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </motion.button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};

export default ClientsTable;
