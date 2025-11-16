import { useState, useEffect } from 'react';
import { Layers, TrendingUp, TrendingDown, Minus, Play, RotateCcw } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import BarChart from '../components/charts/BarChart';
import LineChart from '../components/charts/LineChart';
import { projectionAPI, dataAPI } from '../services/api';

const PREDICTOR_VARS = [
  { key: 'PDRB', label: 'PDRB', unit: 'Triliun Rp', min: -30, max: 30, step: 1 },
  { key: 'Rasio Gini', label: 'Rasio Gini', unit: '', min: -50, max: 50, step: 1 },
  { key: 'IPM', label: 'IPM', unit: '', min: -20, max: 20, step: 1 },
  { key: 'TPT', label: 'TPT', unit: '%', min: -50, max: 50, step: 1 },
  { key: 'Kemiskinan', label: 'Kemiskinan', unit: '%', min: -50, max: 50, step: 1 },
  { key: 'Inflasi', label: 'Inflasi', unit: '%', min: -100, max: 100, step: 5 },
  { key: 'Suku Bunga', label: 'Suku Bunga', unit: '%', min: -100, max: 100, step: 5 }
];

const PRESET_SCENARIOS = {
  baseline: { name: 'Baseline', adjustments: {} },
  optimistic: {
    name: 'Optimis',
    adjustments: {
      PDRB: 10,
      'Rasio Gini': -5,
      IPM: 5,
      TPT: -10,
      Kemiskinan: -10,
      Inflasi: -20,
      'Suku Bunga': -20
    }
  },
  pessimistic: {
    name: 'Pesimis',
    adjustments: {
      PDRB: -10,
      'Rasio Gini': 5,
      IPM: -5,
      TPT: 10,
      Kemiskinan: 10,
      Inflasi: 20,
      'Suku Bunga': 20
    }
  },
  recovery: {
    name: 'Pemulihan',
    adjustments: {
      PDRB: 15,
      'Rasio Gini': -10,
      IPM: 10,
      TPT: -15,
      Kemiskinan: -15,
      Inflasi: 0,
      'Suku Bunga': -10
    }
  }
};

export default function ScenarioBuilderPage() {
  const [adjustments, setAdjustments] = useState({});
  const [scenarios, setScenarios] = useState({});
  const [loading, setLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState([]);
  const [forecastYears] = useState(5);
  const [responseVar] = useState('PAD');

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

  const handleAdjustmentChange = (varKey, value) => {
    setAdjustments(prev => ({
      ...prev,
      [varKey]: parseFloat(value)
    }));
  };

  const resetAdjustments = () => {
    setAdjustments({});
  };

  const loadPreset = (presetKey) => {
    setAdjustments(PRESET_SCENARIOS[presetKey].adjustments);
  };

  const runScenario = async () => {
    setLoading(true);
    try {
      // Generate base forecast data from historical trends
      if (historicalData.length === 0) return;

      const baseForecastData = {};
      PREDICTOR_VARS.forEach(({ key }) => {
        const historicalValues = historicalData.map(row => row[key]);
        const lastValue = historicalValues[historicalValues.length - 1];

        // Simple linear projection
        const growthRate = 0.03; // 3% default growth
        const forecastValues = [];
        for (let i = 1; i <= forecastYears; i++) {
          forecastValues.push(lastValue * Math.pow(1 + growthRate, i));
        }
        baseForecastData[key] = forecastValues;
      });

      // Run scenario analysis with adjustments
      const scenarioParams = {
        response_var: responseVar,
        predictor_vars: PREDICTOR_VARS.map(v => v.key),
        base_forecast_data: baseForecastData,
        forecast_years: forecastYears,
        scenario_adjustments: {
          custom: Object.keys(adjustments).length > 0
            ? Object.entries(adjustments).reduce((acc, [key, val]) => {
                acc[key] = val / 100; // Convert percentage to decimal
                return acc;
              }, {})
            : 0.0
        }
      };

      // Also run baseline and standard scenarios
      const allScenarios = {};

      // Custom scenario (if adjustments exist)
      if (Object.keys(adjustments).length > 0) {
        const customResponse = await projectionAPI.getScenarioAnalysis(scenarioParams);
        allScenarios.custom = customResponse.data.scenarios.custom;
      }

      // Standard scenarios (optimistic, moderate, pessimistic)
      const standardParams = {
        ...scenarioParams,
        scenario_adjustments: undefined
      };
      const standardResponse = await projectionAPI.getScenarioAnalysis(standardParams);

      setScenarios({
        ...allScenarios,
        ...standardResponse.data.scenarios
      });

    } catch (err) {
      console.error('Error running scenario:', err);
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

  const prepareComparisonChart = () => {
    if (Object.keys(scenarios).length === 0) return null;

    const labels = ['Pesimis', 'Moderat', 'Optimis'];
    if (scenarios.custom) labels.push('Custom');

    const data = {
      labels,
      datasets: [{
        label: 'Total Proyeksi (5 Tahun)',
        data: [
          scenarios.pessimistic?.total || 0,
          scenarios.moderate?.total || 0,
          scenarios.optimistic?.total || 0,
          scenarios.custom?.total || 0
        ].filter(v => v > 0),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(139, 92, 246, 0.8)'
        ]
      }]
    };

    return data;
  };

  const prepareTimeSeriesChart = () => {
    if (Object.keys(scenarios).length === 0) return null;

    const years = ['2025', '2026', '2027', '2028', '2029'];

    const datasets = [];

    if (scenarios.pessimistic) {
      datasets.push({
        label: 'Pesimis',
        data: scenarios.pessimistic.predictions,
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2
      });
    }

    if (scenarios.moderate) {
      datasets.push({
        label: 'Moderat',
        data: scenarios.moderate.predictions,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2
      });
    }

    if (scenarios.optimistic) {
      datasets.push({
        label: 'Optimis',
        data: scenarios.optimistic.predictions,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 2
      });
    }

    if (scenarios.custom) {
      datasets.push({
        label: 'Custom',
        data: scenarios.custom.predictions,
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        borderDash: [5, 5]
      });
    }

    return { labels: years, datasets };
  };

  const comparisonChart = prepareComparisonChart();
  const timeSeriesChart = prepareTimeSeriesChart();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Layers size={32} className="text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Scenario Builder</h1>
            <p className="text-gray-600 mt-2">Analisis what-if interaktif untuk proyeksi PAD</p>
          </div>
        </div>
      </div>

      {/* Preset Scenarios */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Skenario Preset</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {Object.entries(PRESET_SCENARIOS).map(([key, scenario]) => (
            <Button
              key={key}
              variant="outline"
              onClick={() => loadPreset(key)}
              className="justify-start"
            >
              {scenario.name}
            </Button>
          ))}
        </div>
      </Card>

      {/* Variable Adjustments */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Penyesuaian Variabel</h2>
          <Button variant="outline" size="sm" onClick={resetAdjustments}>
            <RotateCcw size={16} className="mr-2" />
            Reset
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {PREDICTOR_VARS.map(({ key, label, unit, min, max, step }) => {
            const value = adjustments[key] || 0;
            const Icon = value > 0 ? TrendingUp : value < 0 ? TrendingDown : Minus;
            const color = value > 0 ? 'text-green-600' : value < 0 ? 'text-red-600' : 'text-gray-400';

            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">
                    {label} {unit && `(${unit})`}
                  </label>
                  <div className="flex items-center gap-2">
                    <Icon size={16} className={color} />
                    <span className={`text-sm font-semibold ${color}`}>
                      {value > 0 ? '+' : ''}{value}%
                    </span>
                  </div>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={step}
                  value={value}
                  onChange={(e) => handleAdjustmentChange(key, e.target.value)}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{min}%</span>
                  <span>{max}%</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <Button
            onClick={runScenario}
            disabled={loading}
            className="w-full"
            size="lg"
          >
            <Play size={20} className="mr-2" />
            {loading ? 'Running Scenario...' : 'Run Scenario Analysis'}
          </Button>
        </div>
      </Card>

      {/* Results */}
      {Object.keys(scenarios).length > 0 && (
        <>
          {/* Comparison Chart */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Perbandingan Skenario</h2>
            {comparisonChart && (
              <BarChart
                data={comparisonChart}
                height={300}
                options={{
                  plugins: {
                    tooltip: {
                      callbacks: {
                        label: function(context) {
                          return formatCurrency(context.parsed.y);
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

          {/* Time Series Chart */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Proyeksi Time Series</h2>
            {timeSeriesChart && (
              <LineChart
                data={timeSeriesChart}
                height={400}
                options={{
                  plugins: {
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

          {/* Summary Table */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Ringkasan Skenario</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Skenario
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Total (5 Tahun)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rata-rata/Tahun
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Adjustment
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(scenarios).map(([key, data]) => {
                    const avg = data.total / forecastYears;
                    const adjustmentPercent = (data.adjustment || 0) * 100;

                    return (
                      <tr key={key}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium capitalize">
                          {key === 'pessimistic' && 'Pesimis'}
                          {key === 'moderate' && 'Moderat'}
                          {key === 'optimistic' && 'Optimis'}
                          {key === 'custom' && 'Custom'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                          {formatCurrency(data.total)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {formatCurrency(avg)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`${
                            adjustmentPercent > 0 ? 'text-green-600' :
                            adjustmentPercent < 0 ? 'text-red-600' :
                            'text-gray-600'
                          } font-medium`}>
                            {adjustmentPercent > 0 ? '+' : ''}{adjustmentPercent.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      {/* Empty State */}
      {Object.keys(scenarios).length === 0 && !loading && (
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-12 text-center">
          <Layers size={64} className="text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Siap Membuat Skenario</h2>
          <p className="text-gray-600">
            Sesuaikan variabel menggunakan slider di atas atau pilih preset skenario,
            kemudian klik "Run Scenario Analysis" untuk melihat hasil.
          </p>
        </div>
      )}
    </div>
  );
}
