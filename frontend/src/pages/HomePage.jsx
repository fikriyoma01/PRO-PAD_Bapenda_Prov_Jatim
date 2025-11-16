import { useState, useEffect } from 'react';
import { Building2, TrendingUp, Database, BookOpen, Zap, Shield } from 'lucide-react';
import MetricCard from '../components/ui/MetricCard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import LineChart from '../components/charts/LineChart';
import { formatRupiah, formatCompactNumber, calculatePercentageChange } from '../lib/utils';
import { dataAPI } from '../services/api';

export default function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // For now, use mock data until backend is ready
      const mockData = generateMockData();
      setData(mockData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const years = [2018, 2019, 2020, 2021, 2022, 2023, 2024];
    const historicalData = years.map(year => ({
      Tahun: year,
      PKB: 4000000000000 + (year - 2018) * 500000000000,
      BBNKB: 2000000000000 + (year - 2018) * 300000000000,
    }));

    return { historicalData };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const latestYear = 2024;
  const latestPKB = data.historicalData[data.historicalData.length - 1].PKB;
  const latestBBNKB = data.historicalData[data.historicalData.length - 1].BBNKB;
  const prevPKB = data.historicalData[data.historicalData.length - 2].PKB;
  const prevBBNKB = data.historicalData[data.historicalData.length - 2].BBNKB;

  const pkbGrowth = calculatePercentageChange(prevPKB, latestPKB);
  const bbnkbGrowth = calculatePercentageChange(prevBBNKB, latestBBNKB);
  const totalPAD = latestPKB + latestBBNKB;

  // Prepare chart data
  const chartData = data.historicalData.map(item => ({
    year: item.Tahun.toString(),
    PKB: item.PKB / 1e9, // Convert to billions
    BBNKB: item.BBNKB / 1e9,
    Total: (item.PKB + item.BBNKB) / 1e9,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="gradient-header text-white rounded-lg p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-3 flex items-center justify-center gap-3">
            <Building2 size={40} />
            Dashboard Proyeksi PAD Jawa Timur
          </h1>
          <p className="text-xl opacity-90">
            Sistem Analisis & Proyeksi Pendapatan Asli Daerah Berbasis Data Science
          </p>
        </div>
      </div>

      {/* Welcome Card */}
      <Card>
        <CardContent className="text-center p-8">
          <h2 className="text-2xl font-bold text-blue-700 mb-4">
            Selamat Datang di Dashboard PAD Jawa Timur
          </h2>
          <p className="text-lg text-gray-600 leading-relaxed">
            Dashboard ini menyediakan analisis mendalam dan proyeksi akurat untuk{' '}
            <strong>PKB (Pajak Kendaraan Bermotor)</strong> dan{' '}
            <strong>BBNKB (Bea Balik Nama Kendaraan Bermotor)</strong>{' '}
            menggunakan metodologi statistik dan machine learning.
          </p>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp size={24} />
          Ringkasan Data Terkini
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title={`PKB ${latestYear}`}
            value={formatCompactNumber(latestPKB)}
            change={pkbGrowth}
            changeLabel="vs tahun lalu"
            icon={TrendingUp}
            iconColor="text-blue-600"
            iconBgColor="bg-blue-100"
          />

          <MetricCard
            title={`BBNKB ${latestYear}`}
            value={formatCompactNumber(latestBBNKB)}
            change={bbnkbGrowth}
            changeLabel="vs tahun lalu"
            icon={TrendingUp}
            iconColor="text-purple-600"
            iconBgColor="bg-purple-100"
          />

          <MetricCard
            title={`Total PAD ${latestYear}`}
            value={formatCompactNumber(totalPAD)}
            icon={Database}
            iconColor="text-green-600"
            iconBgColor="bg-green-100"
          />

          <MetricCard
            title="Data Range"
            value="2018-2024"
            change={data.historicalData.length}
            changeLabel="Years"
            icon={Database}
            iconColor="text-orange-600"
            iconBgColor="bg-orange-100"
          />
        </div>
      </div>

      {/* Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp size={20} />
            Tren Historis PAD
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LineChart
            data={chartData}
            lines={[
              { dataKey: 'PKB', name: 'PKB', color: '#3b82f6' },
              { dataKey: 'BBNKB', name: 'BBNKB', color: '#8b5cf6' },
              { dataKey: 'Total', name: 'Total PAD', color: '#10b981' },
            ]}
            xKey="year"
            formatY="currency"
            height={400}
          />
        </CardContent>
      </Card>

      {/* Feature Cards */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Zap size={24} />
          Fitur Utama
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={TrendingUp}
            title="Pemodelan Statistik"
            description="Model OLS Regression, ARIMA, dan Exponential Smoothing untuk proyeksi akurat"
            color="blue"
          />

          <FeatureCard
            icon={Database}
            title="Analisis Data"
            description="Eksplorasi data historis dengan visualisasi interaktif dan statistik deskriptif"
            color="purple"
          />

          <FeatureCard
            icon={BookOpen}
            title="Scenario Builder"
            description="Analisis what-if untuk berbagai skenario ekonomi dan kebijakan"
            color="green"
          />

          <FeatureCard
            icon={Shield}
            title="Validasi Model"
            description="Cross-validation, backtesting, dan analisis sensitivitas"
            color="orange"
          />

          <FeatureCard
            icon={TrendingUp}
            title="Decision Support"
            description="Rekomendasi strategis berbasis data untuk pengambilan keputusan"
            color="red"
          />

          <FeatureCard
            icon={Database}
            title="Audit Trail"
            description="Pelacakan lengkap aktivitas dan perubahan data untuk transparansi"
            color="indigo"
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description, color }) {
  const colorClasses = {
    blue: 'from-blue-50 to-blue-100 border-blue-200',
    purple: 'from-purple-50 to-purple-100 border-purple-200',
    green: 'from-green-50 to-green-100 border-green-200',
    orange: 'from-orange-50 to-orange-100 border-orange-200',
    red: 'from-red-50 to-red-100 border-red-200',
    indigo: 'from-indigo-50 to-indigo-100 border-indigo-200',
  };

  const iconColors = {
    blue: 'text-blue-600',
    purple: 'text-purple-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    indigo: 'text-indigo-600',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-lg p-6 hover:shadow-md transition-shadow`}>
      <Icon size={32} className={`${iconColors[color]} mb-3`} />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
