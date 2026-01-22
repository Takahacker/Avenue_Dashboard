import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { useState } from 'react';

const scrollbarStyle = `
  .allocation-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .allocation-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
  }
  .allocation-scrollbar::-webkit-scrollbar-thumb {
    background: hsl(39, 40%, 64%, 0.4);
    border-radius: 10px;
  }
  .allocation-scrollbar::-webkit-scrollbar-thumb:hover {
    background: hsl(39, 40%, 64%, 0.6);
  }
`;

if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = scrollbarStyle;
  document.head.appendChild(style);
}

const data = [
  { name: 'Low-Risk Portfolio', value: 6, color: 'hsl(39, 40%, 64%)' },
  { name: 'Balanced-Risk Portfolio', value: 2, color: 'hsl(160, 65%, 35%)' },
  { name: 'Aggressive-Risk Portfolio', value: 1, color: 'hsl(39, 50%, 50%)' },
  { name: 'Bonds', value: 1, color: 'hsl(160, 45%, 25%)' },
  { name: 'Conservador PF', value: 1, color: 'hsl(0, 0%, 50%)' },
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    const percentage = ((payload[0].value / total) * 100).toFixed(1);
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card-gold p-3"
      >
        <p className="text-sm font-medium">{payload[0].name}</p>
        <p className="text-lg font-semibold text-gold-gradient">{payload[0].value} clientes ({percentage}%)</p>
      </motion.div>
    );
  }
  return null;
};

const AllocationPieChart = () => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const handleMouseEnter = (_: any, index: number) => {
    setActiveIndex(index);
  };

  const handleMouseLeave = () => {
    setActiveIndex(null);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="glass-card p-6 chart-container flex flex-col"
    >
      <div className="mb-4">
        <h3 className="text-lg font-serif text-gold-gradient">Distribuição de Perfis</h3>
        <p className="text-sm text-muted-foreground">Distribuição por perfil de risco</p>
      </div>

      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              animationDuration={1000}
              animationEasing="ease-out"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke="transparent"
                  style={{
                    filter: activeIndex === index ? 'drop-shadow(0 0 8px hsl(39, 40%, 64%))' : 'none',
                    transform: activeIndex === index ? 'scale(1.05)' : 'scale(1)',
                    transformOrigin: 'center',
                    transition: 'all 0.3s ease',
                  }}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="allocation-scrollbar grid grid-cols-1 gap-2 mt-4 overflow-y-auto max-h-40 pr-2">
        {data.map((item, index) => (
          <motion.div
            key={item.name}
            className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
            onMouseEnter={() => setActiveIndex(index)}
            onMouseLeave={() => setActiveIndex(null)}
            whileHover={{ x: 4 }}
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-muted-foreground flex-1">{item.name}</span>
            <span className="text-xs font-medium">{item.value}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default AllocationPieChart;
