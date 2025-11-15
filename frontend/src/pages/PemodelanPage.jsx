import { useState } from 'react';
import { LineChart as LineChartIcon, Play, TrendingUp, Activity } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import LineChart from '../components/charts/LineChart';
import TornadoChart from '../components/charts/TornadoChart';
import { modelAPI, analysisAPI } from '../services/api';
import { formatRupiah, formatPercentage } from '../lib/utils';

export default function PemodelanPage() {
  const [selectedModel, setSelectedModel] = useState('ols');
  const [selectedResponse, setSelectedResponse] = useState('PKB');
  const [selectedPredictors, setSelectedPredictors] = useState(['PDRB', 'IPM', 'Gini']);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [sensitivity, setSensitivity] = useState(null);

  const modelOptions = [
    { value: 'ols', label: 'OLS Regression' },
    { value: 'arima', label: 'ARIMA' },
    { value: 'exp_smoothing', label: 'Exponential Smoothing' },
    { value: 'ensemble', label: 'Ensemble (All Models)' },
  ];

  const responseOptions = [
    { value: 'PKB', label: 'PKB (Pajak Kendaraan Bermotor)' },
    { value: 'BBNKB', label: 'BBNKB (Bea Balik Nama)' },
  ];

  const predictorOptions = [
    { value: 'PDRB', label: 'PDRB' },
    { value: 'Gini', label: 'Rasio Gini' },
    { value: 'IPM', label: 'IPM' },
    { value: 'TPT', label: 'TPT (Tingkat Pengangguran)' },
    { value: 'Kemiskinan', label: 'Kemiskinan' },
    { value: 'Inflasi', label: 'Inflasi' },
    { value: 'SukuBunga', label: 'Suku Bunga' },
  ];

  const runModel = async () => {
    setLoading(true);
    setResults(null);
    setSensitivity(null);

    try {
      let modelResults;

      if (selectedModel === 'ols') {
        const response = await modelAPI.runOLSRegression({
          response_var: selectedResponse,
          predictor_vars: selectedPredictors,
          forecast_years: 2,
        });
        modelResults = response.data;
      } else if (selectedModel === 'arima') {
        const response = await modelAPI.runARIMA({
          response_var: selectedResponse,
          order: [1, 1, 1],
          forecast_steps: 2,
        });
        modelResults = response.data;
      } else if (selectedModel === 'exp_smoothing') {
        const response = await modelAPI.runExpSmoothing({
          response_var: selectedResponse,
          trend: 'add',
          forecast_steps: 2,
        });
        modelResults = response.data;
      } else if (selectedModel === 'ensemble') {
        const response = await modelAPI.runEnsemble({
          response_var: selectedResponse,
          predictor_vars: selectedPredictors,
          forecast_years: 2,
        });
        modelResults = response.data;
      }

      setResults(modelResults);

      // Run sensitivity analysis for OLS
      if (selectedModel === 'ols' || selectedModel === 'ensemble') {
        const sensResponse = await analysisAPI.getSensitivityAnalysis({
          response_var: selectedResponse,
          predictor_vars: selectedPredictors,
          variation_pct: 10,
        });
        setSensitivity(sensResponse.data);
      }
    } catch (error) {
      console.error('Error running model:', error);
      alert('Error running model. Please make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <LineChartIcon size={32} className="text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pemodelan Statistik</h1>
          <p className="text-gray-600 mt-2">OLS Regression, ARIMA, Exponential Smoothing, dan Ensemble</p>
        </div>
      </div>

      {/* Model Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Konfigurasi Model</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Model Type"
              value={selectedModel}
              onChange={setSelectedModel}
              options={modelOptions}
            />

            <Select
              label="Response Variable"
              value={selectedResponse}
              onChange={setSelectedResponse}
              options={responseOptions}
            />
          </div>

          {(selectedModel === 'ols' || selectedModel === 'ensemble') && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Predictor Variables
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {predictorOptions.map((option) => (
                  <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPredictors.includes(option.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedPredictors([...selectedPredictors, option.value]);
                        } else {
                          setSelectedPredictors(selectedPredictors.filter((p) => p !== option.value));
                        }
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6">
            <Button
              onClick={runModel}
              loading={loading}
              disabled={loading || (selectedModel === 'ols' && selectedPredictors.length === 0)}
              icon={Play}
            >
              Run Model
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {results && (
        <>
          {/* Model Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity size={20} />
                Model Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {results.results?.metrics && (
                  <>
                    <MetricBox
                      label="R²"
                      value={formatPercentage(results.results.metrics.r2 * 100, 2)}
                      description="Coefficient of Determination"
                    />
                    <MetricBox
                      label="RMSE"
                      value={formatRupiah(results.results.metrics.rmse)}
                      description="Root Mean Squared Error"
                    />
                    <MetricBox
                      label="MAPE"
                      value={formatPercentage(results.results.metrics.mape, 2)}
                      description="Mean Absolute Percentage Error"
                    />
                    <MetricBox
                      label="MAE"
                      value={formatRupiah(results.results.metrics.mae)}
                      description="Mean Absolute Error"
                    />
                  </>
                )}

                {results.results?.r_squared !== undefined && (
                  <>
                    <MetricBox
                      label="R²"
                      value={formatPercentage(results.results.r_squared * 100, 2)}
                      description="Coefficient of Determination"
                    />
                    <MetricBox
                      label="Adj R²"
                      value={formatPercentage(results.results.adj_r_squared * 100, 2)}
                      description="Adjusted R²"
                    />
                    <MetricBox
                      label="AIC"
                      value={results.results.aic.toFixed(2)}
                      description="Akaike Info Criterion"
                    />
                    <MetricBox
                      label="BIC"
                      value={results.results.bic.toFixed(2)}
                      description="Bayesian Info Criterion"
                    />
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Coefficients for OLS */}
          {results.results?.params && (
            <Card>
              <CardHeader>
                <CardTitle>Model Coefficients</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variable</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Coefficient</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Std Error</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P-value</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Significance</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(results.results.params).map(([key, value]) => (
                        <tr key={key}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{key}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{value.toExponential(4)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {results.results.std_errors[key].toExponential(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {results.results.pvalues[key].toFixed(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium ${
                                results.results.pvalues[key] < 0.05
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {results.results.pvalues[key] < 0.001 ? '***' : results.results.pvalues[key] < 0.01 ? '**' : results.results.pvalues[key] < 0.05 ? '*' : 'NS'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Sensitivity Analysis */}
          {sensitivity && (
            <Card>
              <CardHeader>
                <CardTitle>Sensitivity Analysis (Tornado Chart)</CardTitle>
              </CardHeader>
              <CardContent>
                <TornadoChart
                  data={sensitivity.sensitivity}
                  variableKey="variable"
                  positiveKey="impact_positive"
                  negativeKey="impact_negative"
                  height={Math.max(300, sensitivity.sensitivity.length * 40)}
                />
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>Most Sensitive:</strong> {sensitivity.interpretation.most_sensitive}
                  </p>
                  <p className="text-sm text-gray-700 mt-1">
                    <strong>Least Sensitive:</strong> {sensitivity.interpretation.least_sensitive}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

function MetricBox({ label, value, description }) {
  return (
    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
      <div className="text-xs font-medium text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-xs text-gray-500">{description}</div>
    </div>
  );
}
