import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, MoreHorizontal } from 'lucide-react';

const clients = [
  {
    id: 1,
    name: 'Adilson Ferreira da Silva Junior',
    email: 'adilson.light@gmail.com',
    banker: 'Francisco Luiz Hintze Maranho',
    portfolio: 245000,
    change: 8.5,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 2,
    name: 'Andre luis costa',
    email: 'andreluiscosta.96@gmail.com',
    banker: 'Bruno Leite Bernardes',
    portfolio: 512390,
    change: 12.3,
    perfil: 'Balanced-Risk Portfolio',
  },
  {
    id: 3,
    name: 'BRUNA PAIVA SBOARINI',
    email: 'vendasara1@gmail.com',
    banker: 'Felipe De Oliveira Criscuolo',
    portfolio: 178900,
    change: 5.2,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 4,
    name: 'EDUARDO SBOARINI',
    email: 'araimportsadm@gmail.com',
    banker: 'Felipe De Oliveira Criscuolo',
    portfolio: 345000,
    change: 9.8,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 5,
    name: 'Ettore Vasconcellos Paiola',
    email: 'ettorevp@gmail.com',
    banker: 'Tiago Paiola Mantovani',
    portfolio: 567800,
    change: 18.5,
    perfil: 'Aggressive-Risk Portfolio',
  },
  {
    id: 6,
    name: 'MARIA ALICE AMADO GOUVEIA VENTURINI',
    email: 'JOSE.OTAVIO@TERRACONTTEMPORANEA.COM.BR',
    banker: 'Eduardo Santo Corsatto Vieira',
    portfolio: 289000,
    change: 6.3,
    perfil: 'Bonds',
  },
  {
    id: 7,
    name: 'Mara Silvia Porto Vilela',
    email: 'VILELAMARA4@GMAIL.COM',
    banker: 'Daniela Machado',
    portfolio: 156700,
    change: 3.8,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 8,
    name: 'SILVIO LUIZ VENTURINI',
    email: 'silvio@terraconttemporanea.com.br',
    banker: 'Eduardo Santo Corsatto Vieira',
    portfolio: 423500,
    change: 11.2,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 9,
    name: 'Wanderley Crestoni Fernandes',
    email: 'wancrestoni@gmail.com',
    banker: 'André Guilherme',
    portfolio: 234567,
    change: 7.5,
    perfil: 'Conservador PF',
  },
  {
    id: 10,
    name: 'Jones Antonio Pagno',
    email: 'jonespagno@gmail.com',
    banker: 'Alan Finazzi Sbeghen',
    portfolio: 198400,
    change: 4.9,
    perfil: 'Low-Risk Portfolio',
  },
  {
    id: 11,
    name: 'Agel Gustavo Turim',
    email: 'agelgustavo@gmail.com',
    banker: 'Eduardo Marquesi de Oliveira',
    portfolio: 378600,
    change: 13.7,
    perfil: 'Balanced-Risk Portfolio',
  },
];

const allocationColors: Record<string, string> = {
  'Low-Risk Portfolio': 'bg-green-500/20 text-green-400 border-green-500/30',
  'Balanced-Risk Portfolio': 'bg-prunus-gold/20 text-prunus-gold border-prunus-gold/30',
  'Aggressive-Risk Portfolio': 'bg-red-500/20 text-red-400 border-red-500/30',
  'Bonds': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Conservador PF': 'bg-green-500/20 text-green-400 border-green-500/30',
};

const ClientsTable = () => {
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
          <p className="text-sm text-muted-foreground">Acompanhe a performance de seus clientes</p>
        </div>
        <motion.button
          className="px-4 py-2 rounded-xl glass-card-gold text-sm font-medium"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Ver Todos
        </motion.button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Cliente
              </th>
              <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Portfólio
              </th>
              <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Variação
              </th>
              <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Perfil
              </th>
              <th className="text-right py-3 px-4"></th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client, index) => (
              <motion.tr
                key={client.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
              >
                <td className="py-4 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-prunus-gold/30 to-prunus-green-light/30 flex items-center justify-center border border-prunus-gold/20">
                      <span className="text-sm font-medium">
                        {client.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium group-hover:text-prunus-gold transition-colors">
                        {client.name}
                      </p>
                      <p className="text-xs text-muted-foreground">{client.email}</p>
                    </div>
                  </div>
                </td>
                <td className="py-4 px-4">
                  <span className="font-semibold">
                    ${client.portfolio.toLocaleString('en-US')}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <div className="flex items-center gap-1">
                    {client.change >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-400" />
                    )}
                    <span className={client.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                      {client.change >= 0 ? '+' : ''}{client.change}%
                    </span>
                  </div>
                </td>
                <td className="py-4 px-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${allocationColors[client.perfil]}`}>
                    {client.perfil}
                  </span>
                </td>
                <td className="py-4 px-4 text-right">
                  <motion.button
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100"
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
    </motion.div>
  );
};

export default ClientsTable;
