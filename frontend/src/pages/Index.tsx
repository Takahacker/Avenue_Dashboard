import { useState, useEffect } from 'react';
import { Users, DollarSign, TrendingUp, Briefcase } from 'lucide-react';
import AnimatedBackground from '@/components/AnimatedBackground';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import MetricCard from '@/components/MetricCard';
import EvolutionChart from '@/components/EvolutionChart';
import AllocationPieChart from '@/components/AllocationPieChart';
import CaptacaoEvolutionChart from '@/components/CaptacaoEvolutionChart';
import SettingsPopup from '@/components/SettingsPopup';
import ClientsTable from '@/components/ClientsTable';
import ClientsView from '@/pages/Clients';
import BankersView from '@/pages/Bankers';

interface Metrics {
  totalClientes: number;
  novosClientes: number;
  plTotal: number;
  plVariacao: number;
  captacaoPeriodo: number;
  top3Bankers: Array<{
    nome: string;
    captacao: number;
  }>;
}

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/metrics?t=' + Date.now());
        const result = await response.json();
        if (result.success) {
          setMetrics(result.metrics);
        }
      } catch (err) {
        console.error('Erro ao carregar métricas:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return '$' + (value / 1000000).toFixed(3) + 'M';
    }
    if (value >= 1000) {
      return '$' + (value / 1000).toFixed(0) + 'K';
    }
    return '$' + value.toFixed(0);
  };

  return (
    <div className="min-h-screen">
      <AnimatedBackground />
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} onSettingsClick={() => setIsSettingsOpen(!isSettingsOpen)} />
      
      <main className="ml-64 p-6">
        <Header />

        <SettingsPopup isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />

        {/* Metrics Row - Only visible on dashboard tab */}
        {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <MetricCard
            title="Total Clientes"
            value={loading ? "-" : String(metrics?.totalClientes || 0)}
            change={loading ? "-" : String(metrics?.novosClientes || 0)}
            changeType="positive"
            icon={Users}
            delay={0}
          />
          <MetricCard
            title="PL Total"
            value={loading ? "-" : formatCurrency(metrics?.plTotal || 0)}
            change={loading ? "-" : `${metrics?.plVariacao || 0}%`}
            changeType={metrics?.plVariacao && metrics.plVariacao >= 0 ? "positive" : "negative"}
            icon={DollarSign}
            delay={0.1}
          />
          <MetricCard
            title="Captação no Período"
            value={loading ? "-" : formatCurrency(metrics?.captacaoPeriodo || 0)}
            icon={TrendingUp}
            delay={0.2}
          />
          <div className="glass-card p-6 backdrop-blur-md rounded-lg border border-prunus-gold/20 flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-4">Top 3 Bankers</h3>
              <div className="space-y-3">
                {loading ? (
                  <p className="text-muted-foreground text-sm">Carregando...</p>
                ) : metrics?.top3Bankers && metrics.top3Bankers.length > 0 ? (
                  metrics.top3Bankers.map((banker, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-xs text-muted-foreground">{banker.nome}</span>
                      <span className="text-sm font-semibold text-prunus-gold">{formatCurrency(banker.captacao)}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-sm">Sem dados</p>
                )}
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Charts Row 1 - Only visible on dashboard tab */}
        {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 gap-6 mb-6">
          <EvolutionChart clientName="Todos os Clientes" />
        </div>
        )}

        {/* Charts Row 2 - Captação Evolution and Allocation - Only visible on dashboard tab */}
        {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <CaptacaoEvolutionChart />
          </div>
          <AllocationPieChart />
        </div>
        )}

        {/* Conditional Content */}
        {activeTab === 'dashboard' && (
          <>
            {/* Clients Table */}
            <ClientsTable />
          </>
        )}

        {activeTab === 'clients' && <ClientsView />}

        {activeTab === 'bankers' && <BankersView />}
      </main>
    </div>
  );
};

export default Index;
