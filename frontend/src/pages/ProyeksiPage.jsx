import { useState, useEffect } from 'react';
import { TrendingUp, Download, Info, Activity } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import Select from '../components/Select';
import LineChart from '../components/LineChart';
import MetricCard from '../components/MetricCard';
import { projectionAPI, dataAPI } from '../services/api';

const MODEL_OPTIONS = [
  { value: 'ensemble', label: 'Ensemble (Recommended)' },
  { value: 'ols', label: 'OLS Regression' },
  { value: 'arima', label: 'ARIMA' },
  { value: 'exp_smoothing', label: 'Exponential Smoothing' }
];

const RESPONSE_VAR_OPTIONS = [
  { value: 'PAD', label: 'Total PAD' },
  { value: 'PKB', label: 'PKB' },
  { value: 'BBNKB', label: 'BBNKB' }
];

const FORECAST_YEARS_OPTIONS = [
  { value: 2, label: '2 Tahun' },
  { value: 3, label: '3 Tahun' },
  { value: 5, label: '5 Tahun' },
  { value: 10, label: '10 Tahun' }
];

const PREDICTOR_VARS = [
  'PDRB', 'Rasio Gini', 'IPM', 'TPT', 'Kemiskinan', 'Inflasi', 'Suku Bunga'
];

export default function ProyeksiPage() {
  const [loading, setLoading] = useState(false);
  const [modelType, setModelType] = useState('ensemble');
  const [responseVar, setResponseVar] = useState('PAD');
  const [forecastYears, setForecastYears] = useState(5);
  const [projectionResult, setProjectionResult] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [error, setError] = useState(null);

  // Load historical data on mount
  useEffect(() => {
    loadHistoricalData();
  }, []);

  const loadHistoricalData = async () => {
    try {
      const response = await dataAPI.loadHistoricalData();
      setHistoricalData(response.data.data);
    } catch (err) {
      console.error('Error loading historical data:', err);
    }
  };

  const handleGenerateProjection = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        response_var: responseVar,
        predictor_vars: modelType === 'ols' || modelType === 'ensemble' ? PREDICTOR_VARS : null,
        forecast_years: forecastYears,
        model_type: modelType,
        include_confidence_intervals: true
      };

      const response = await projectionAPI.generateProjection(params);
      setProjectionResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating projection');
      console.error('Error generating projection:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const prepareChartData = () => {
    if (!projectionResult) return null;

    const { historical, forecast } = projectionResult;

    // Combine historical and forecast data
    const labels = [...historical.years, ...forecast.years];

    const datasets = [
      {
        label: 'Data Historis',
        data: [...historical.values, ...Array(forecast.years.length).fill(null)],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2
      },
      {
        label: 'Proyeksi',
        data: [...Array(historical.years.length).fill(null), ...forecast.predictions],
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5]
      }
    ];

    // Add confidence intervals if available
    if (forecast.lower_ci && forecast.upper_ci) {
      datasets.push({
        label: 'Lower CI (95%)',
        data: [...Array(historical.years.length).fill(null), ...forecast.lower_ci],
        borderColor: 'rgba(139, 92, 246, 0.3)',
        backgroundColor: 'rgba(139, 92, 246, 0.05)',
        borderWidth: 1,
        borderDash: [2, 2],
        fill: false
      });

      datasets.push({
        label: 'Upper CI (95%)',
        data: [...Array(historical.years.length).fill(null), ...forecast.upper_ci],
        borderColor: 'rgba(139, 92, 246, 0.3)',
        backgroundColor: 'rgba(139, 92, 246, 0.05)',
        borderWidth: 1,
        borderDash: [2, 2],
        fill: '-1'
      });
    }

    return {
      labels,
      datasets
    };
  };

  const calculateGrowthRate = () => {
    if (!projectionResult) return null;

    const { predictions } = projectionResult.forecast;
    if (predictions.length < 2) return null;

    const firstYear = predictions[0];
    const lastYear = predictions[predictions.length - 1];
    const years = predictions.length - 1;

    const cagr = (Math.pow(lastYear / firstYear, 1 / years) - 1) * 100;
    return cagr;
  };

  const calculateTotalProjected = () => {
    if (!projectionResult) return 0;
    return projectionResult.forecast.predictions.reduce((sum, val) => sum + val, 0);
  };

  const chartData = prepareChartData();
  const growthRate = calculateGrowthRate();
  const totalProjected = calculateTotalProjected();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <TrendingUp size={32} className="text-purple-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Proyeksi PAD</h1>
            <p className="text-gray-600 mt-2">Proyeksi multi-tahun dengan confidence intervals</p>
          </div>
        </div>
      </div>

      {/* Configuration Card */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Konfigurasi Proyeksi</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Variabel Target
            </label>
            <Select
              value={responseVar}
              onChange={(e) => setResponseVar(e.target.value)}
              options={RESPONSE_VAR_OPTIONS}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <Select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              options={MODEL_OPTIONS}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Periode Proyeksi
            </label>
            <Select
              value={forecastYears}
              onChange={(e) => setForecastYears(Number(e.target.value))}
              options={FORECAST_YEARS_OPTIONS}
            />
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleGenerateProjection}
              disabled={loading}
              className="w-full"
            >
              {loading ? 'Generating...' : 'Generate Proyeksi'}
            </Button>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info size={20} className="text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-900">
              <p className="font-semibold mb-1">Tentang Model:</p>
              <p>
                {modelType === 'ensemble' && 'Ensemble menggabungkan OLS, ARIMA, dan Exponential Smoothing untuk hasil yang lebih robust.'}
                {modelType === 'ols' && 'OLS menggunakan regresi linier untuk memprediksi berdasarkan variabel makroekonomi.'}
                {modelType === 'arima' && 'ARIMA cocok untuk data time series dengan trend dan seasonality.'}
                {modelType === 'exp_smoothing' && 'Exponential Smoothing memberikan bobot lebih pada data terbaru.'}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-900">{error}</p>
        </div>
      )}

      {/* Results */}
      {projectionResult && (
        <>
          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              title="Total Proyeksi"
              value={formatCurrency(totalProjected)}
              subtitle={`${forecastYears} tahun ke depan`}
              icon={TrendingUp}
              color="purple"
            />
            <MetricCard
              title="CAGR"
              value={growthRate ? `${growthRate.toFixed(2)}%` : 'N/A'}
              subtitle="Compound Annual Growth Rate"
              icon={Activity}
              color="blue"
            />
            <MetricCard
              title="Proyeksi Tahun Pertama"
              value={formatCurrency(projectionResult.forecast.predictions[0])}
              subtitle={`Tahun ${projectionResult.forecast.years[0]}`}
              icon={TrendingUp}
              color="green"
            />
          </div>

          {/* Chart */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Grafik Proyeksi</h2>
              <Button variant="outline" size="sm">
                <Download size={16} className="mr-2" />
                Export Chart
              </Button>
            </div>

            {chartData && (
              <LineChart
                data={chartData}
                height={400}
                options={{
                  plugins: {
                    title: {
                      display: true,
                      text: `Proyeksi ${responseVar} (${projectionResult.model_type.toUpperCase()})`
                    },
                    tooltip: {
                      callbacks: {
                        label: function(context) {
                          return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                      }
                    }
                  },
                  scales: {
                    y: {
                      ticks: {
                        callback: function(value) {
                          return formatCurrency(value);
                        }
                      }
                    }
                  }
                }}
              />
            )}
          </Card>

          {/* Forecast Table */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Detail Proyeksi</h2>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tahun
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Proyeksi
                    </th>
                    {projectionResult.forecast.lower_ci && (
                      <>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Lower CI (95%)
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Upper CI (95%)
                        </th>
                      </>
                    )}
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Growth vs Previous
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {projectionResult.forecast.years.map((year, index) => {
                    const prediction = projectionResult.forecast.predictions[index];
                    const prevPrediction = index > 0
                      ? projectionResult.forecast.predictions[index - 1]
                      : projectionResult.historical.values[projectionResult.historical.values.length - 1];
                    const growth = ((prediction - prevPrediction) / prevPrediction * 100).toFixed(2);

                    return (
                      <tr key={year}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {year}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                          {formatCurrency(prediction)}
                        </td>
                        {projectionResult.forecast.lower_ci && (
                          <>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatCurrency(projectionResult.forecast.lower_ci[index])}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatCurrency(projectionResult.forecast.upper_ci[index])}
                            </td>
                          </>
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`${growth >= 0 ? 'text-green-600' : 'text-red-600'} font-medium`}>
                            {growth >= 0 ? '+' : ''}{growth}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Model Info */}
          {projectionResult.forecast.model_params && (
            <Card>
              <h2 className="text-xl font-semibold mb-4">Informasi Model</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {modelType === 'ols' && (
                  <>
                    <div>
                      <p className="text-sm text-gray-500">R-squared</p>
                      <p className="text-lg font-semibold">{projectionResult.forecast.r_squared?.toFixed(4)}</p>
                    </div>
                  </>
                )}
                {(modelType === 'arima' || modelType === 'ensemble') && (
                  <>
                    {projectionResult.forecast.aic && (
                      <div>
                        <p className="text-sm text-gray-500">AIC</p>
                        <p className="text-lg font-semibold">{projectionResult.forecast.aic.toFixed(2)}</p>
                      </div>
                    )}
                    {projectionResult.forecast.bic && (
                      <div>
                        <p className="text-sm text-gray-500">BIC</p>
                        <p className="text-lg font-semibold">{projectionResult.forecast.bic.toFixed(2)}</p>
                      </div>
                    )}
                  </>
                )}
                {modelType === 'ensemble' && projectionResult.forecast.weights && (
                  <>
                    <div>
                      <p className="text-sm text-gray-500">ARIMA Weight</p>
                      <p className="text-lg font-semibold">{(projectionResult.forecast.weights.arima * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Exp Smoothing Weight</p>
                      <p className="text-lg font-semibold">{(projectionResult.forecast.weights.exp_smoothing * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">OLS Weight</p>
                      <p className="text-lg font-semibold">{(projectionResult.forecast.weights.ols * 100).toFixed(0)}%</p>
                    </div>
                  </>
                )}
              </div>
            </Card>
          )}
        </>
      )}

      {/* Empty State */}
      {!projectionResult && !loading && !error && (
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-12 text-center">
          <TrendingUp size={64} className="text-purple-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Siap Generate Proyeksi</h2>
          <p className="text-gray-600">
            Pilih konfigurasi di atas dan klik "Generate Proyeksi" untuk memulai.
          </p>
        </div>
      )}
    </div>
  );
}
