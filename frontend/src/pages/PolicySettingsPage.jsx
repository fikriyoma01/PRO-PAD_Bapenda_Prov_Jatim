import { useState, useEffect } from 'react';
import { Settings, Save, RotateCcw, TrendingUp, Target, AlertCircle, CheckCircle } from 'lucide-react';
import { Card } from '../components/ui/Card';
import Button from '../components/ui/Button';
import MetricCard from '../components/ui/MetricCard';
import { dataAPI } from '../services/api';

const DEFAULT_SETTINGS = {
  targets: {
    2025: 0,
    2026: 0,
    2027: 0
  },
  parameters: {
    pkb_tax_rate: 1.5,
    bbnkb_tax_rate: 10.0,
    compliance_rate: 85.0,
    collection_efficiency: 92.0,
    annual_growth_target: 6.0
  },
  policies: {
    digitalization_boost: false,
    enforcement_program: false,
    tax_amnesty: false
  }
};

export default function PolicySettingsPage() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [historicalData, setHistoricalData] = useState([]);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
    loadSettings();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await dataAPI.loadHistoricalData();
      setHistoricalData(response.data.data);

      // Auto-calculate suggested targets based on historical growth
      if (response.data.data.length > 0) {
        const latestYear = response.data.data[response.data.data.length - 1];
        const avgGrowthRate = 1.06; // 6% default growth

        setSettings(prev => ({
          ...prev,
          targets: {
            2025: Math.round(latestYear.PAD * avgGrowthRate),
            2026: Math.round(latestYear.PAD * Math.pow(avgGrowthRate, 2)),
            2027: Math.round(latestYear.PAD * Math.pow(avgGrowthRate, 3))
          }
        }));
      }
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSettings = () => {
    const saved = localStorage.getItem('policy_settings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  };

  const handleSaveSettings = () => {
    try {
      localStorage.setItem('policy_settings', JSON.stringify(settings));
      setSaveStatus('success');
      setHasChanges(false);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error('Error saving:', err);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleResetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
    setHasChanges(true);
  };

  const handleTargetChange = (year, value) => {
    setSettings(prev => ({
      ...prev,
      targets: {
        ...prev.targets,
        [year]: parseFloat(value) || 0
      }
    }));
    setHasChanges(true);
  };

  const handleParameterChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [key]: parseFloat(value) || 0
      }
    }));
    setHasChanges(true);
  };

  const handlePolicyToggle = (key) => {
    setSettings(prev => ({
      ...prev,
      policies: {
        ...prev.policies,
        [key]: !prev.policies[key]
      }
    }));
    setHasChanges(true);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const calculateGapToTarget = () => {
    if (historicalData.length === 0) return null;
    const latestYear = historicalData[historicalData.length - 1];
    const target2025 = settings.targets[2025];
    const gap = target2025 - latestYear.PAD;
    const gapPercentage = ((gap / latestYear.PAD) * 100).toFixed(2);
    return { gap, gapPercentage, current: latestYear.PAD };
  };

  const gapAnalysis = calculateGapToTarget();

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings size={32} className="text-red-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Policy Settings</h1>
            <p className="text-gray-600 mt-2">Pengaturan kebijakan dan target PAD</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleResetSettings}>
            <RotateCcw size={16} className="mr-2" />
            Reset
          </Button>
          <Button onClick={handleSaveSettings} disabled={!hasChanges}>
            <Save size={16} className="mr-2" />
            {saveStatus === 'success' ? 'Saved!' : 'Save Settings'}
          </Button>
        </div>
      </div>

      {/* Status Banner */}
      {saveStatus === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="text-green-600" size={24} />
          <p className="text-green-800 font-medium">Settings berhasil disimpan!</p>
        </div>
      )}

      {hasChanges && !saveStatus && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="text-yellow-600" size={24} />
          <p className="text-yellow-800 font-medium">Ada perubahan yang belum disimpan</p>
        </div>
      )}

      {/* Gap Analysis */}
      {gapAnalysis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="PAD Saat Ini"
            value={formatCurrency(gapAnalysis.current)}
            subtitle="Tahun terkini"
            icon={TrendingUp}
            color="blue"
          />
          <MetricCard
            title="Target 2025"
            value={formatCurrency(settings.targets[2025])}
            subtitle="Target tahun depan"
            icon={Target}
            color="green"
          />
          <MetricCard
            title="Gap to Target"
            value={`${gapAnalysis.gapPercentage}%`}
            subtitle={formatCurrency(gapAnalysis.gap)}
            icon={gapAnalysis.gap >= 0 ? TrendingUp : AlertCircle}
            color={gapAnalysis.gap >= 0 ? 'green' : 'red'}
          />
        </div>
      )}

      {/* PAD Targets */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Target PAD (3 Tahun Kedepan)</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[2025, 2026, 2027].map(year => (
            <div key={year}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target {year}
              </label>
              <input
                type="number"
                value={settings.targets[year]}
                onChange={(e) => handleTargetChange(year, e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="0"
              />
              <p className="text-xs text-gray-500 mt-1">
                {formatCurrency(settings.targets[year])}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Tax Parameters */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Parameter Pajak</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              PKB Tax Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.parameters.pkb_tax_rate}
              onChange={(e) => handleParameterChange('pkb_tax_rate', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-500 mt-1">Tarif Pajak Kendaraan Bermotor</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              BBNKB Tax Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.parameters.bbnkb_tax_rate}
              onChange={(e) => handleParameterChange('bbnkb_tax_rate', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-500 mt-1">Tarif Bea Balik Nama Kendaraan</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compliance Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.parameters.compliance_rate}
              onChange={(e) => handleParameterChange('compliance_rate', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-500 mt-1">Tingkat kepatuhan wajib pajak</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Collection Efficiency (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.parameters.collection_efficiency}
              onChange={(e) => handleParameterChange('collection_efficiency', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-500 mt-1">Efisiensi pengumpulan pajak</p>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Annual Growth Target (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.parameters.annual_growth_target}
              onChange={(e) => handleParameterChange('annual_growth_target', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <p className="text-xs text-gray-500 mt-1">Target pertumbuhan PAD tahunan</p>
          </div>
        </div>
      </Card>

      {/* Policy Initiatives */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Inisiatif Kebijakan</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Program Digitalisasi</h3>
              <p className="text-sm text-gray-600">
                Implementasi e-Samsat dan sistem pembayaran digital untuk meningkatkan efisiensi
              </p>
              <p className="text-xs text-blue-600 mt-1">Estimasi dampak: +3-5% collection efficiency</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={settings.policies.digitalization_boost}
                onChange={() => handlePolicyToggle('digitalization_boost')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Program Penegakan Hukum</h3>
              <p className="text-sm text-gray-600">
                Intensifikasi penegakan hukum terhadap wajib pajak yang menunggak
              </p>
              <p className="text-xs text-blue-600 mt-1">Estimasi dampak: +5-7% compliance rate</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={settings.policies.enforcement_program}
                onChange={() => handlePolicyToggle('enforcement_program')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Program Amnesti Pajak</h3>
              <p className="text-sm text-gray-600">
                Pembebasan denda untuk wajib pajak yang melunasi tunggakan
              </p>
              <p className="text-xs text-blue-600 mt-1">Estimasi dampak: +10-15% one-time collection</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={settings.policies.tax_amnesty}
                onChange={() => handlePolicyToggle('tax_amnesty')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Summary */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Ringkasan Konfigurasi</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Active Policies</h3>
            <ul className="space-y-1">
              {settings.policies.digitalization_boost && (
                <li className="text-sm text-blue-800 flex items-center gap-2">
                  <CheckCircle size={16} />
                  Program Digitalisasi
                </li>
              )}
              {settings.policies.enforcement_program && (
                <li className="text-sm text-blue-800 flex items-center gap-2">
                  <CheckCircle size={16} />
                  Program Penegakan Hukum
                </li>
              )}
              {settings.policies.tax_amnesty && (
                <li className="text-sm text-blue-800 flex items-center gap-2">
                  <CheckCircle size={16} />
                  Program Amnesti Pajak
                </li>
              )}
              {!settings.policies.digitalization_boost && !settings.policies.enforcement_program && !settings.policies.tax_amnesty && (
                <li className="text-sm text-gray-500">Tidak ada kebijakan aktif</li>
              )}
            </ul>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">Key Parameters</h3>
            <div className="space-y-1 text-sm text-green-800">
              <p>Compliance Rate: <span className="font-semibold">{settings.parameters.compliance_rate}%</span></p>
              <p>Collection Efficiency: <span className="font-semibold">{settings.parameters.collection_efficiency}%</span></p>
              <p>Growth Target: <span className="font-semibold">{settings.parameters.annual_growth_target}%</span></p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
