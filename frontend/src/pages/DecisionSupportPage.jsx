import { useState, useEffect } from 'react';
import { Target, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import Card from '../components/Card';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import { dataAPI, projectionAPI } from '../services/api';

export default function DecisionSupportPage() {
  const [projection, setProjection] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const projResponse = await projectionAPI.generateProjection({
        response_var: 'PAD',
        forecast_years: 3,
        model_type: 'ensemble',
        include_confidence_intervals: true
      });
      setProjection(projResponse.data);
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

  const recommendations = [
    {
      title: 'Tingkatkan Kepatuhan Pajak',
      description: 'Fokus pada pengurangan tunggakan pajak kendaraan bermotor',
      impact: 'High',
      status: 'recommended'
    },
    {
      title: 'Optimalisasi Digitalisasi',
      description: 'Perluas layanan e-Samsat untuk meningkatkan efisiensi',
      impact: 'Medium',
      status: 'in-progress'
    },
    {
      title: 'Monitoring PDRB',
      description: 'PDRB menunjukkan tren positif yang berkorelasi dengan PAD',
      impact: 'High',
      status: 'monitoring'
    }
  ];

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Target size={32} className="text-green-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Decision Support</h1>
          <p className="text-gray-600 mt-2">Executive dashboard dan rekomendasi strategis</p>
        </div>
      </div>

      {projection && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              title="Proyeksi 2025"
              value={formatCurrency(projection.forecast.predictions[0])}
              subtitle="Target tahun depan"
              icon={TrendingUp}
              color="green"
            />
            <MetricCard
              title="Growth Rate"
              value={`${((projection.forecast.predictions[0] / projection.historical.values[projection.historical.values.length - 1] - 1) * 100).toFixed(2)}%`}
              subtitle="vs tahun sebelumnya"
              icon={TrendingUp}
              color="blue"
            />
            <MetricCard
              title="Confidence"
              value="95%"
              subtitle="Interval kepercayaan"
              icon={CheckCircle}
              color="purple"
            />
          </div>

          <Card>
            <h2 className="text-xl font-semibold mb-4">Trend & Proyeksi PAD</h2>
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
                    label: 'Projection',
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
        </>
      )}

      <Card>
        <h2 className="text-xl font-semibold mb-4">Rekomendasi Strategis</h2>
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      rec.impact === 'High' ? 'bg-red-100 text-red-800' :
                      rec.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {rec.impact} Impact
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm">{rec.description}</p>
                </div>
                <div className="ml-4">
                  {rec.status === 'recommended' && <AlertCircle className="text-blue-500" size={24} />}
                  {rec.status === 'in-progress' && <TrendingUp className="text-yellow-500" size={24} />}
                  {rec.status === 'monitoring' && <CheckCircle className="text-green-500" size={24} />}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Risk Assessment</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border-l-4 border-green-500 bg-green-50 p-4 rounded">
            <h3 className="font-semibold text-green-900 mb-1">Low Risk</h3>
            <p className="text-sm text-green-700">PDRB growth stable, economic indicators positive</p>
          </div>
          <div className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded">
            <h3 className="font-semibold text-yellow-900 mb-1">Medium Risk</h3>
            <p className="text-sm text-yellow-700">Inflation volatility may impact collection rates</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
