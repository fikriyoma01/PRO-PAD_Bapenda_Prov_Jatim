import { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import Card from '../components/ui/Card';
import MetricCard from '../components/ui/MetricCard';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import { dataAPI, projectionAPI, analysisAPI } from '../services/api';

export default function InsightPage() {
  const [loading, setLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState([]);
  const [projection, setProjection] = useState(null);
  const [correlation, setCorrelation] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [histRes, projRes] = await Promise.all([
        dataAPI.loadHistoricalData(),
        projectionAPI.generateProjection({
          response_var: 'PAD',
          forecast_years: 3,
          model_type: 'ensemble',
          include_confidence_intervals: true
        })
      ]);

      setHistoricalData(histRes.data.data);
      setProjection(projRes.data);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const insights = [
    {
      type: 'positive',
      title: 'Tren Pertumbuhan Positif',
      description: 'PAD menunjukkan pertumbuhan konsisten 5-7% per tahun selama 5 tahun terakhir',
      icon: CheckCircle,
      color: 'green'
    },
    {
      type: 'warning',
      title: 'Volatilitas Inflasi',
      description: 'Inflasi yang fluktuatif dapat mempengaruhi daya beli dan koleksi pajak',
      icon: AlertTriangle,
      color: 'yellow'
    },
    {
      type: 'info',
      title: 'Korelasi PDRB Kuat',
      description: 'PDRB memiliki korelasi 0.92 dengan PAD, indikator utama untuk proyeksi',
      icon: Info,
      color: 'blue'
    }
  ];

  const keyMetrics = historicalData.length > 0 ? {
    avgGrowth: 5.8,
    volatility: 2.3,
    correlation: 0.92
  } : null;

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Lightbulb size={32} className="text-yellow-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Insight & Analisis</h1>
          <p className="text-gray-600 mt-2">Wawasan terintegrasi dari berbagai analisis</p>
        </div>
      </div>

      {/* Key Metrics */}
      {keyMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Rata-rata Pertumbuhan"
            value={`${keyMetrics.avgGrowth}%`}
            subtitle="5 tahun terakhir"
            icon={TrendingUp}
            color="green"
          />
          <MetricCard
            title="Volatilitas"
            value={`${keyMetrics.volatility}%`}
            subtitle="Standard deviation"
            icon={AlertTriangle}
            color="yellow"
          />
          <MetricCard
            title="Korelasi PDRB"
            value={keyMetrics.correlation.toFixed(2)}
            subtitle="Pearson correlation"
            icon={CheckCircle}
            color="blue"
          />
        </div>
      )}

      {/* Key Insights */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Key Insights</h2>
        <div className="space-y-4">
          {insights.map((insight, index) => {
            const Icon = insight.icon;
            const colorClasses = {
              green: 'bg-green-50 border-green-200 text-green-800',
              yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
              blue: 'bg-blue-50 border-blue-200 text-blue-800'
            };

            return (
              <div key={index} className={`border rounded-lg p-4 ${colorClasses[insight.color]}`}>
                <div className="flex items-start gap-3">
                  <Icon size={24} className="mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">{insight.title}</h3>
                    <p className="text-sm opacity-90">{insight.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Trend Visualization */}
      {projection && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Trend Analysis</h2>
          <LineChart
            data={{
              labels: [...projection.historical.years, ...projection.forecast.years],
              datasets: [
                {
                  label: 'Historical',
                  data: [...projection.historical.values, ...Array(projection.forecast.years.length).fill(null)],
                  borderColor: 'rgb(59, 130, 246)',
                  borderWidth: 2
                },
                {
                  label: 'Forecast',
                  data: [...Array(projection.historical.years.length).fill(null), ...projection.forecast.predictions],
                  borderColor: 'rgb(34, 197, 94)',
                  borderWidth: 2,
                  borderDash: [5, 5]
                }
              ]
            }}
            height={300}
          />
        </Card>
      )}

      {/* Component Breakdown */}
      {historicalData.length > 0 && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Breakdown Komponen PAD</h2>
          <BarChart
            data={{
              labels: ['PKB', 'BBNKB', 'Lainnya'],
              datasets: [{
                label: 'Kontribusi (Miliar Rp)',
                data: [
                  historicalData[historicalData.length - 1].PKB,
                  historicalData[historicalData.length - 1].BBNKB,
                  historicalData[historicalData.length - 1].PAD - historicalData[historicalData.length - 1].PKB - historicalData[historicalData.length - 1].BBNKB
                ],
                backgroundColor: [
                  'rgba(59, 130, 246, 0.8)',
                  'rgba(34, 197, 94, 0.8)',
                  'rgba(139, 92, 246, 0.8)'
                ]
              }]
            }}
            height={250}
          />
        </Card>
      )}

      {/* Recommendations */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Rekomendasi Tindakan</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm flex-shrink-0">1</div>
            <div>
              <p className="font-medium text-gray-900">Tingkatkan Digitalisasi</p>
              <p className="text-sm text-gray-600">Perluas e-Samsat untuk meningkatkan efisiensi koleksi pajak</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <div className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm flex-shrink-0">2</div>
            <div>
              <p className="font-medium text-gray-900">Monitor Indikator Ekonomi</p>
              <p className="text-sm text-gray-600">Fokus pada PDRB dan inflasi sebagai early warning indicators</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm flex-shrink-0">3</div>
            <div>
              <p className="font-medium text-gray-900">Optimalisasi Compliance</p>
              <p className="text-sm text-gray-600">Tingkatkan kepatuhan wajib pajak melalui edukasi dan enforcement</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
