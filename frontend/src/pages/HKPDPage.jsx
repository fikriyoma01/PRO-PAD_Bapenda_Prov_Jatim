import { useState, useEffect } from 'react';
import { FileText, TrendingUp, DollarSign, PieChart as PieChartIcon, Info } from 'lucide-react';
import Card from '../components/ui/Card';
import MetricCard from '../components/ui/MetricCard';
import Select from '../components/ui/Select';
import BarChart from '../components/charts/BarChart';
import PieChart from '../components/charts/PieChart';
import { dataAPI } from '../services/api';

const SCENARIO_OPTIONS = [
  { value: 'current', label: 'Skenario Saat Ini (60/40)' },
  { value: 'balanced', label: 'Skenario Seimbang (50/50)' },
  { value: 'central_heavy', label: 'Skenario Pusat Dominan (70/30)' },
  { value: 'local_heavy', label: 'Skenario Daerah Dominan (40/60)' }
];

const REVENUE_SOURCES = [
  { key: 'PKB', label: 'Pajak Kendaraan Bermotor (PKB)' },
  { key: 'BBNKB', label: 'Bea Balik Nama Kendaraan Bermotor (BBNKB)' },
  { key: 'Pajak_BBM', label: 'Pajak Bahan Bakar Kendaraan Bermotor' },
  { key: 'Pajak_Rokok', label: 'Pajak Rokok' }
];

export default function HKPDPage() {
  const [selectedScenario, setSelectedScenario] = useState('current');
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await dataAPI.loadHistoricalData();
      setHistoricalData(response.data.data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScenarioAllocation = () => {
    const allocations = {
      current: { central: 60, local: 40 },
      balanced: { central: 50, local: 50 },
      central_heavy: { central: 70, local: 30 },
      local_heavy: { central: 40, local: 60 }
    };
    return allocations[selectedScenario];
  };

  const calculateHKPDImpact = () => {
    if (historicalData.length === 0) return null;

    const latestYear = historicalData[historicalData.length - 1];
    const allocation = getScenarioAllocation();

    const totalRevenue = latestYear.PAD || 0;
    const centralShare = totalRevenue * (allocation.central / 100);
    const localShare = totalRevenue * (allocation.local / 100);

    const pkbShare = (latestYear.PKB || 0) * (allocation.local / 100);
    const bbnkbShare = (latestYear.BBNKB || 0) * (allocation.local / 100);
    const otherShare = localShare - pkbShare - bbnkbShare;

    return {
      totalRevenue,
      centralShare,
      localShare,
      allocation,
      breakdown: {
        pkb: pkbShare,
        bbnkb: bbnkbShare,
        other: otherShare
      }
    };
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const impact = calculateHKPDImpact();

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText size={32} className="text-indigo-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">HKPD</h1>
            <p className="text-gray-600 mt-2">Analisis Hak Keuangan Pemerintah Daerah</p>
          </div>
        </div>
        <div className="w-64">
          <Select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            options={SCENARIO_OPTIONS}
          />
        </div>
      </div>

      {/* Info Banner */}
      <Card>
        <div className="flex items-start gap-3">
          <Info size={24} className="text-indigo-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Tentang HKPD</h3>
            <p className="text-sm text-gray-600">
              HKPD mengatur pembagian pendapatan antara pemerintah pusat dan daerah.
              Analisis ini membantu memahami dampak berbagai skenario alokasi terhadap PAD.
            </p>
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      {impact && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Total Pendapatan"
            value={formatCurrency(impact.totalRevenue)}
            subtitle="Tahun terkini"
            icon={DollarSign}
            color="indigo"
          />
          <MetricCard
            title="Bagian Pusat"
            value={formatCurrency(impact.centralShare)}
            subtitle={`${impact.allocation.central}% dari total`}
            icon={TrendingUp}
            color="blue"
          />
          <MetricCard
            title="Bagian Daerah"
            value={formatCurrency(impact.localShare)}
            subtitle={`${impact.allocation.local}% dari total`}
            icon={PieChartIcon}
            color="green"
          />
        </div>
      )}

      {/* Allocation Visualization */}
      {impact && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-xl font-semibold mb-4">Pembagian Pusat vs Daerah</h2>
            <PieChart
              data={{
                labels: ['Bagian Pusat', 'Bagian Daerah'],
                datasets: [{
                  data: [impact.centralShare, impact.localShare],
                  backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(34, 197, 94, 0.8)'
                  ]
                }]
              }}
              height={300}
            />
          </Card>

          <Card>
            <h2 className="text-xl font-semibold mb-4">Breakdown Bagian Daerah</h2>
            <PieChart
              data={{
                labels: ['PKB', 'BBNKB', 'Lainnya'],
                datasets: [{
                  data: [
                    impact.breakdown.pkb,
                    impact.breakdown.bbnkb,
                    impact.breakdown.other
                  ],
                  backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                  ]
                }]
              }}
              height={300}
            />
          </Card>
        </div>
      )}

      {/* Scenario Comparison */}
      {historicalData.length > 0 && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Perbandingan Semua Skenario</h2>
          <BarChart
            data={{
              labels: ['Saat Ini (60/40)', 'Seimbang (50/50)', 'Pusat Dominan (70/30)', 'Daerah Dominan (40/60)'],
              datasets: [
                {
                  label: 'Bagian Daerah',
                  data: [
                    historicalData[historicalData.length - 1].PAD * 0.40,
                    historicalData[historicalData.length - 1].PAD * 0.50,
                    historicalData[historicalData.length - 1].PAD * 0.30,
                    historicalData[historicalData.length - 1].PAD * 0.60
                  ],
                  backgroundColor: 'rgba(34, 197, 94, 0.8)'
                },
                {
                  label: 'Bagian Pusat',
                  data: [
                    historicalData[historicalData.length - 1].PAD * 0.60,
                    historicalData[historicalData.length - 1].PAD * 0.50,
                    historicalData[historicalData.length - 1].PAD * 0.70,
                    historicalData[historicalData.length - 1].PAD * 0.40
                  ],
                  backgroundColor: 'rgba(99, 102, 241, 0.8)'
                }
              ]
            }}
            height={300}
          />
        </Card>
      )}

      {/* Detailed Table */}
      {impact && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Detail Alokasi Skenario Terpilih</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Komponen</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Nilai</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Persentase</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr className="bg-indigo-50">
                  <td className="px-6 py-4 text-sm font-semibold text-gray-900">Total Pendapatan</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right font-semibold">{formatCurrency(impact.totalRevenue)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">100%</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-900 pl-12">Bagian Pemerintah Pusat</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{formatCurrency(impact.centralShare)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{impact.allocation.central}%</td>
                </tr>
                <tr className="bg-green-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 pl-12">Bagian Pemerintah Daerah</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right font-medium">{formatCurrency(impact.localShare)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{impact.allocation.local}%</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-600 pl-20">PKB</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">{formatCurrency(impact.breakdown.pkb)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">
                    {((impact.breakdown.pkb / impact.totalRevenue) * 100).toFixed(1)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-600 pl-20">BBNKB</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">{formatCurrency(impact.breakdown.bbnkb)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">
                    {((impact.breakdown.bbnkb / impact.totalRevenue) * 100).toFixed(1)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm text-gray-600 pl-20">Lainnya</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">{formatCurrency(impact.breakdown.other)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 text-right">
                    {((impact.breakdown.other / impact.totalRevenue) * 100).toFixed(1)}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Impact Analysis */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Analisis Dampak</h2>
        <div className="space-y-3">
          <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <h3 className="font-semibold text-blue-900 mb-1">Dampak Fiskal</h3>
            <p className="text-sm text-blue-800">
              Skenario {selectedScenario === 'current' ? 'saat ini' : selectedScenario === 'balanced' ? 'seimbang' : selectedScenario === 'central_heavy' ? 'pusat dominan' : 'daerah dominan'} memberikan alokasi {impact?.allocation.local}% untuk daerah,
              yang setara dengan {formatCurrency(impact?.localShare || 0)} dari total PAD.
            </p>
          </div>
          <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
            <h3 className="font-semibold text-green-900 mb-1">Implikasi Kebijakan</h3>
            <p className="text-sm text-green-800">
              Dengan alokasi ini, daerah memiliki fleksibilitas {impact?.allocation.local >= 50 ? 'tinggi' : 'sedang'} dalam mengelola anggaran
              untuk pembangunan dan pelayanan publik.
            </p>
          </div>
          <div className="p-4 bg-purple-50 border-l-4 border-purple-500 rounded">
            <h3 className="font-semibold text-purple-900 mb-1">Rekomendasi</h3>
            <p className="text-sm text-purple-800">
              {impact?.allocation.local >= 50
                ? 'Skenario ini mendukung desentralisasi fiskal yang kuat. Pastikan kapasitas pengelolaan keuangan daerah memadai.'
                : 'Skenario ini memperkuat peran koordinasi pusat. Perlu dipastikan mekanisme transfer dan redistribusi berjalan optimal.'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
