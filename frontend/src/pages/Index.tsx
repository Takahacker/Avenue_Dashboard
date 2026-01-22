import { useState } from 'react';
import { Users, DollarSign, TrendingUp, Briefcase } from 'lucide-react';
import AnimatedBackground from '@/components/AnimatedBackground';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import MetricCard from '@/components/MetricCard';
import PortfolioChart from '@/components/PortfolioChart';
import EvolutionChart from '@/components/EvolutionChart';
import AllocationPieChart from '@/components/AllocationPieChart';
import PerformanceBarChart from '@/components/PerformanceBarChart';
import ClientsTable from '@/components/ClientsTable';

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen">
      <AnimatedBackground />
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="ml-64 p-6">
        <Header />

        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <MetricCard
            title="Total Clientes"
            value="24"
            change="3"
            changeType="positive"
            icon={Users}
            delay={0}
          />
          <MetricCard
            title="AUM Total"
            value="$4.2M"
            change="12.5%"
            changeType="positive"
            icon={DollarSign}
            delay={0.1}
          />
          <MetricCard
            title="Rentabilidade Média"
            value="8.7%"
            change="2.3%"
            changeType="positive"
            icon={TrendingUp}
            delay={0.2}
          />
          <MetricCard
            title="Novos Investimentos"
            value="$320K"
            change="15.8%"
            changeType="positive"
            icon={Briefcase}
            delay={0.3}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <PortfolioChart 
              title="Total de P&L" 
              clientName="André Guilherme" 
            />
          </div>
          <EvolutionChart clientName="André Luis Costa" />
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <PerformanceBarChart />
          </div>
          <AllocationPieChart />
        </div>

        {/* Clients Table */}
        <ClientsTable />
      </main>
    </div>
  );
};

export default Index;
