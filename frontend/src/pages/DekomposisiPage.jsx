import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, TrendingDown } from 'lucide-react';
import Card from '../components/Card';
import Select from '../components/Select';
import WaterfallChart from '../components/WaterfallChart';
import BarChart from '../components/BarChart';
import { dataAPI } from '../services/api';

const YEAR_OPTIONS = [
  { value: 2024, label: '2024' },
  { value: 2023, label: '2023' },
  { value: 2022, label: '2022' },
  { value: 2021, label: '2021' },
  { value: 2020, label: '2020' }
];

export default function DekomposisiPage() {
  const [selectedYear, setSelectedYear] = useState(2024);
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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  const getYearData = () => {
    return historicalData.find(d => d.Tahun === selectedYear) || null;
  };

  const getPreviousYearData = () => {
    return historicalData.find(d => d.Tahun === selectedYear - 1) || null;
  };

  const calculateDecomposition = () => {
    const currentYear = getYearData();
    const previousYear = getPreviousYearData();

    if (!currentYear || !previousYear) return null;

    const pkbChange = currentYear.PKB - previousYear.PKB;
    const bbnkbChange = currentYear.BBNKB - previousYear.BBNKB;
    const totalChange = currentYear.PAD - previousYear.PAD;

    return {
      base: previousYear.PAD,
      pkb: pkbChange,
      bbnkb: bbnkbChange,
      total: currentYear.PAD,
      totalChange
    };
  };

  const decomposition = calculateDecomposition();
  const currentYear = getYearData();

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 size={32} className="text-green-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dekomposisi PAD</h1>
            <p className="text-gray-600 mt-2">Analisis faktor-faktor kontribusi PAD</p>
          </div>
        </div>
        <div className="w-40">
          <Select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            options={YEAR_OPTIONS}
          />
        </div>
      </div>

      {/* Summary Cards */}
      {decomposition && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <p className="text-sm text-gray-600">Base ({selectedYear - 1})</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(decomposition.base)}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600">Perubahan PKB</p>
            <div className="flex items-center gap-2">
              <p className={`text-2xl font-bold ${decomposition.pkb >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(Math.abs(decomposition.pkb))}
              </p>
              {decomposition.pkb >= 0 ? <TrendingUp className="text-green-600" /> : <TrendingDown className="text-red-600" />}
            </div>
          </Card>
          <Card>
            <p className="text-sm text-gray-600">Perubahan BBNKB</p>
            <div className="flex items-center gap-2">
              <p className={`text-2xl font-bold ${decomposition.bbnkb >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(Math.abs(decomposition.bbnkb))}
              </p>
              {decomposition.bbnkb >= 0 ? <TrendingUp className="text-green-600" /> : <TrendingDown className="text-red-600" />}
            </div>
          </Card>
          <Card>
            <p className="text-sm text-gray-600">Total ({selectedYear})</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(decomposition.total)}</p>
          </Card>
        </div>
      )}

      {/* Waterfall Chart */}
      {decomposition && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Waterfall Analysis</h2>
          <WaterfallChart
            data={{
              labels: [`${selectedYear - 1} Base`, 'PKB Change', 'BBNKB Change', 'Other', `${selectedYear} Total`],
              datasets: [{
                label: 'PAD Decomposition',
                data: [
                  decomposition.base,
                  decomposition.pkb,
                  decomposition.bbnkb,
                  decomposition.totalChange - decomposition.pkb - decomposition.bbnkb,
                  decomposition.total
                ]
              }]
            }}
            height={350}
          />
        </Card>
      )}

      {/* Component Contribution */}
      {currentYear && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Kontribusi Komponen {selectedYear}</h2>
          <BarChart
            data={{
              labels: ['PKB', 'BBNKB', 'Lainnya'],
              datasets: [{
                label: 'Kontribusi',
                data: [
                  currentYear.PKB,
                  currentYear.BBNKB,
                  currentYear.PAD - currentYear.PKB - currentYear.BBNKB
                ],
                backgroundColor: [
                  'rgba(59, 130, 246, 0.8)',
                  'rgba(34, 197, 94, 0.8)',
                  'rgba(139, 92, 246, 0.8)'
                ]
              }]
            }}
            height={300}
          />
        </Card>
      )}

      {/* Detailed Table */}
      {currentYear && (
        <Card>
          <h2 className="text-xl font-semibold mb-4">Detail Komponen</h2>
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
                <tr>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">PKB</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{formatCurrency(currentYear.PKB)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">
                    {((currentYear.PKB / currentYear.PAD) * 100).toFixed(1)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">BBNKB</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{formatCurrency(currentYear.BBNKB)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">
                    {((currentYear.BBNKB / currentYear.PAD) * 100).toFixed(1)}%
                  </td>
                </tr>
                <tr className="bg-gray-50 font-semibold">
                  <td className="px-6 py-4 text-sm text-gray-900">Total PAD</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">{formatCurrency(currentYear.PAD)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 text-right">100.0%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
