export const BANKER_COLORS = [
  '#D4AF37', // Ouro
  '#22c55e', // Verde
  '#3b82f6', // Azul
  '#f97316', // Laranja
  '#ec4899', // Rosa
  '#14b8a6', // Teal
  '#f59e0b', // Âmbar
  '#8b5cf6', // Roxo
];

export const getBankerColor = (bankerName: string, bankers: string[]): string => {
  const index = bankers.indexOf(bankerName);
  return BANKER_COLORS[index % BANKER_COLORS.length];
};
