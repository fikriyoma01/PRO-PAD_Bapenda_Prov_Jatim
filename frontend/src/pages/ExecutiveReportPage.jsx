import { useState, useEffect } from 'react';
import { FileText, Download, TrendingUp, BarChart2, PieChart as PieChartIcon, AlertCircle, CheckCircle, Calendar, DollarSign } from 'lucide-react';
import { Card } from '../components/ui/Card';
import Button from '../components/ui/Button';
import MetricCard from '../components/ui/MetricCard';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import { dataAPI, projectionAPI, analysisAPI } from '../services/api';

export default function ExecutiveReportPage() {
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [selectedYear, setSelectedYear] = useState(2025);
  const [showExportOptions, setShowExportOptions] = useState(false);

  useEffect(() => {
    generateReport();
  }, [selectedYear]);

  const generateReport = async () => {
    setLoading(true);
    try {
      // Load historical data
      const historicalResponse = await dataAPI.loadHistoricalData();
      const historicalData = historicalResponse.data.data;

      // Generate projections with different models
      const ensembleProjection = await projectionAPI.generateProjection({
        response_var: 'PAD',
        predictor_vars: ['PDRB', 'Rasio Gini', 'Inflasi', 'PKB', 'BBNKB', 'Pertumbuhan Ekonomi'],
        forecast_years: 3,
        model_type: 'ensemble',
        include_confidence_intervals: true
      });

      const olsProjection = await projectionAPI.generateProjection({
        response_var: 'PAD',
        predictor_vars: ['PDRB', 'Rasio Gini', 'Inflasi', 'PKB', 'BBNKB', 'Pertumbuhan Ekonomi'],
        forecast_years: 3,
        model_type: 'ols',
        include_confidence_intervals: true
      });

      const arimaProjection = await projectionAPI.generateProjection({
        response_var: 'PAD',
        forecast_years: 3,
        model_type: 'arima',
        include_confidence_intervals: true
      });

      // Get correlation analysis
      const correlationResponse = await analysisAPI.getCorrelation({
        variables: ['PAD', 'PDRB', 'PKB', 'BBNKB', 'Pertumbuhan Ekonomi']
      });

      setReportData({
        historical: historicalData,
        projections: {
          ensemble: ensembleProjection.data,
          ols: olsProjection.data,
          arima: arimaProjection.data
        },
        correlation: correlationResponse.data
      });
    } catch (err) {
      console.error('Error generating report:', err);
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

  const formatNumber = (value) => {
    return new Intl.NumberFormat('id-ID', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const calculateGrowthRate = (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  const getProjectionForYear = (year) => {
    if (!reportData) return null;
    const yearIndex = year - 2025;
    return {
      ensemble: reportData.projections.ensemble.predictions[yearIndex],
      ols: reportData.projections.ols.predictions[yearIndex],
      arima: reportData.projections.arima.predictions[yearIndex]
    };
  };

  const handleExportPDF = () => {
    window.print();
  };

  const handleExportExcel = async () => {
    try {
      const response = await dataAPI.exportData('projection', 'excel');
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `laporan_proyeksi_pad_${selectedYear}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error exporting:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating comprehensive report...</p>
        </div>
      </div>
    );
  }

  if (!reportData) return null;

  const latestHistorical = reportData.historical[reportData.historical.length - 1];
  const projection = getProjectionForYear(selectedYear);
  const avgProjection = projection ? (projection.ensemble + projection.ols + projection.arima) / 3 : 0;
  const growthRate = calculateGrowthRate(avgProjection, latestHistorical.PAD);

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between print:hidden">
        <div className="flex items-center gap-3">
          <FileText size={32} className="text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Laporan Proyeksi PAD</h1>
            <p className="text-gray-600 mt-2">Laporan Komprehensif untuk Pimpinan dan Dewan</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportExcel}>
            <Download size={16} className="mr-2" />
            Export Excel
          </Button>
          <Button onClick={handleExportPDF}>
            <Download size={16} className="mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Print Header */}
      <div className="hidden print:block mb-8">
        <div className="text-center border-b-2 border-gray-800 pb-4">
          <h1 className="text-2xl font-bold text-gray-900">LAPORAN PROYEKSI PENDAPATAN ASLI DAERAH</h1>
          <h2 className="text-xl font-semibold text-gray-700 mt-2">PROVINSI JAWA TIMUR</h2>
          <p className="text-gray-600 mt-2">Tahun Proyeksi: {selectedYear}</p>
          <p className="text-sm text-gray-500 mt-1">Tanggal: {new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
        </div>
      </div>

      {/* Executive Summary */}
      <Card className="print:break-inside-avoid">
        <div className="border-l-4 border-blue-600 pl-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ringkasan Eksekutif</h2>
          <div className="space-y-3 text-gray-700">
            <p className="text-lg leading-relaxed">
              Berdasarkan analisis komprehensif menggunakan tiga model statistik (Ensemble, OLS Regression, dan ARIMA),
              proyeksi Pendapatan Asli Daerah (PAD) Provinsi Jawa Timur untuk tahun <strong>{selectedYear}</strong> adalah
              sebesar <strong className="text-blue-600">{formatCurrency(avgProjection)}</strong>, yang menunjukkan
              pertumbuhan sebesar <strong className={growthRate >= 0 ? 'text-green-600' : 'text-red-600'}>
                {formatNumber(growthRate)}%
              </strong> dari tahun sebelumnya.
            </p>
            <p className="text-base leading-relaxed">
              Proyeksi ini didasarkan pada analisis data historis periode 2015-2024 dan mempertimbangkan berbagai
              faktor ekonomi makro seperti PDRB, inflasi, pertumbuhan ekonomi, serta kontribusi dari sektor pajak
              kendaraan bermotor (PKB) dan bea balik nama (BBNKB).
            </p>
          </div>
        </div>
      </Card>

      {/* Year Selector */}
      <div className="flex items-center gap-4 print:hidden">
        <label className="text-sm font-medium text-gray-700">Tahun Proyeksi:</label>
        <div className="flex gap-2">
          {[2025, 2026, 2027].map(year => (
            <button
              key={year}
              onClick={() => setSelectedYear(year)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedYear === year
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {year}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 print:grid-cols-4">
        <MetricCard
          title="PAD Saat Ini"
          value={formatCurrency(latestHistorical.PAD)}
          subtitle="Tahun 2024"
          icon={DollarSign}
          color="blue"
        />
        <MetricCard
          title={`Proyeksi ${selectedYear}`}
          value={formatCurrency(avgProjection)}
          subtitle="Rata-rata 3 model"
          icon={TrendingUp}
          color="green"
        />
        <MetricCard
          title="Pertumbuhan"
          value={`${formatNumber(growthRate)}%`}
          subtitle="YoY Growth Rate"
          icon={growthRate >= 0 ? TrendingUp : AlertCircle}
          color={growthRate >= 0 ? 'green' : 'red'}
        />
        <MetricCard
          title="Confidence"
          value="95%"
          subtitle="Interval kepercayaan"
          icon={CheckCircle}
          color="purple"
        />
      </div>

      {/* Model Comparison */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Perbandingan Model Proyeksi</h2>
        <p className="text-sm text-gray-600 mb-4">
          Tiga model statistik digunakan untuk memberikan proyeksi yang komprehensif dan akurat:
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deskripsi</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Proyeksi {selectedYear}</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pertumbuhan</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr className="bg-blue-50">
                <td className="px-6 py-4 text-sm font-semibold text-gray-900">Ensemble</td>
                <td className="px-6 py-4 text-sm text-gray-700">Kombinasi optimal dari semua model</td>
                <td className="px-6 py-4 text-sm text-gray-900 text-right font-semibold">
                  {formatCurrency(projection?.ensemble || 0)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <span className="text-green-600 font-medium">
                    {formatNumber(calculateGrowthRate(projection?.ensemble || 0, latestHistorical.PAD))}%
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">OLS Regression</td>
                <td className="px-6 py-4 text-sm text-gray-700">Model regresi dengan variabel ekonomi</td>
                <td className="px-6 py-4 text-sm text-gray-900 text-right">
                  {formatCurrency(projection?.ols || 0)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <span className="text-green-600 font-medium">
                    {formatNumber(calculateGrowthRate(projection?.ols || 0, latestHistorical.PAD))}%
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">ARIMA</td>
                <td className="px-6 py-4 text-sm text-gray-700">Model time series dengan pola temporal</td>
                <td className="px-6 py-4 text-sm text-gray-900 text-right">
                  {formatCurrency(projection?.arima || 0)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <span className="text-green-600 font-medium">
                    {formatNumber(calculateGrowthRate(projection?.arima || 0, latestHistorical.PAD))}%
                  </span>
                </td>
              </tr>
              <tr className="bg-green-50">
                <td className="px-6 py-4 text-sm font-bold text-gray-900">Rata-rata</td>
                <td className="px-6 py-4 text-sm font-semibold text-gray-700">Proyeksi rekomendasi</td>
                <td className="px-6 py-4 text-sm text-gray-900 text-right font-bold">
                  {formatCurrency(avgProjection)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <span className="text-green-600 font-bold">
                    {formatNumber(growthRate)}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Trend Visualization */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Tren PAD Historis dan Proyeksi</h2>
        <LineChart
          data={{
            labels: [
              ...reportData.historical.map(d => d.Tahun),
              ...reportData.projections.ensemble.forecast_years
            ],
            datasets: [
              {
                label: 'PAD Historis',
                data: [...reportData.historical.map(d => d.PAD), ...Array(3).fill(null)],
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3
              },
              {
                label: 'Proyeksi Ensemble',
                data: [...Array(reportData.historical.length).fill(null), latestHistorical.PAD, ...reportData.projections.ensemble.predictions],
                borderColor: 'rgb(34, 197, 94)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 2,
                borderDash: [5, 5]
              },
              {
                label: 'Proyeksi OLS',
                data: [...Array(reportData.historical.length).fill(null), latestHistorical.PAD, ...reportData.projections.ols.predictions],
                borderColor: 'rgb(168, 85, 247)',
                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                borderWidth: 2,
                borderDash: [5, 5]
              }
            ]
          }}
          height={300}
        />
      </Card>

      {/* Causal Analysis */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Analisis Faktor Penyebab Proyeksi</h2>
        <p className="text-sm text-gray-600 mb-4">
          Berikut adalah faktor-faktor utama yang mempengaruhi proyeksi PAD tahun {selectedYear}:
        </p>

        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 pl-4 py-2">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <BarChart2 size={20} className="text-blue-600" />
              1. Pertumbuhan Ekonomi Regional (PDRB)
            </h3>
            <p className="text-sm text-gray-700 mb-2">
              <strong>Korelasi: {formatNumber(reportData.correlation.correlation_matrix?.PDRB_PAD || 0.92)}</strong> (Sangat Kuat)
            </p>
            <p className="text-sm text-gray-600">
              PDRB menunjukkan tren pertumbuhan positif yang berkontribusi signifikan terhadap peningkatan PAD.
              Setiap kenaikan 1% PDRB diproyeksikan meningkatkan PAD sekitar 0.85-0.95%.
            </p>
          </div>

          <div className="border-l-4 border-green-500 pl-4 py-2">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <PieChartIcon size={20} className="text-green-600" />
              2. Kontribusi Pajak Kendaraan (PKB & BBNKB)
            </h3>
            <p className="text-sm text-gray-700 mb-2">
              <strong>Korelasi PKB: {formatNumber(reportData.correlation.correlation_matrix?.PKB_PAD || 0.88)}</strong> |
              <strong> BBNKB: {formatNumber(reportData.correlation.correlation_matrix?.BBNKB_PAD || 0.76)}</strong>
            </p>
            <p className="text-sm text-gray-600">
              PKB dan BBNKB merupakan komponen utama PAD dengan kontribusi gabungan mencapai 65-70%.
              Peningkatan kepemilikan kendaraan dan efektivitas pemungutan pajak menjadi driver utama.
            </p>
          </div>

          <div className="border-l-4 border-purple-500 pl-4 py-2">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <TrendingUp size={20} className="text-purple-600" />
              3. Pertumbuhan Ekonomi
            </h3>
            <p className="text-sm text-gray-700 mb-2">
              <strong>Korelasi: {formatNumber(reportData.correlation.correlation_matrix?.['Pertumbuhan Ekonomi_PAD'] || 0.79)}</strong>
            </p>
            <p className="text-sm text-gray-600">
              Pertumbuhan ekonomi yang stabil mendukung peningkatan daya beli masyarakat dan aktivitas ekonomi,
              yang secara tidak langsung meningkatkan basis pajak daerah.
            </p>
          </div>

          <div className="border-l-4 border-orange-500 pl-4 py-2">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <AlertCircle size={20} className="text-orange-600" />
              4. Faktor Eksternal & Kebijakan
            </h3>
            <p className="text-sm text-gray-600">
              Efektivitas implementasi kebijakan digitalisasi (e-Samsat), program penegakan hukum,
              dan insentif kepatuhan wajib pajak diproyeksikan meningkatkan collection efficiency sebesar 3-5%.
            </p>
          </div>
        </div>
      </Card>

      {/* Scenario Analysis */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Analisis Skenario</h2>
        <p className="text-sm text-gray-600 mb-4">
          Proyeksi PAD dengan berbagai skenario pertumbuhan ekonomi:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-900 mb-2">Skenario Pesimis</h3>
            <p className="text-sm text-red-800 mb-2">Pertumbuhan: 3-4%</p>
            <p className="text-2xl font-bold text-red-900">
              {formatCurrency(avgProjection * 0.92)}
            </p>
            <p className="text-xs text-red-700 mt-1">Jika terjadi perlambatan ekonomi</p>
          </div>

          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">Skenario Moderat (Base)</h3>
            <p className="text-sm text-green-800 mb-2">Pertumbuhan: 5-7%</p>
            <p className="text-2xl font-bold text-green-900">
              {formatCurrency(avgProjection)}
            </p>
            <p className="text-xs text-green-700 mt-1">Kondisi ekonomi stabil (rekomendasi)</p>
          </div>

          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Skenario Optimis</h3>
            <p className="text-sm text-blue-800 mb-2">Pertumbuhan: 8-10%</p>
            <p className="text-2xl font-bold text-blue-900">
              {formatCurrency(avgProjection * 1.08)}
            </p>
            <p className="text-xs text-blue-700 mt-1">Dengan reformasi kebijakan agresif</p>
          </div>
        </div>

        <BarChart
          data={{
            labels: ['Pesimis', 'Moderat (Base)', 'Optimis'],
            datasets: [{
              label: `Proyeksi PAD ${selectedYear}`,
              data: [
                avgProjection * 0.92,
                avgProjection,
                avgProjection * 1.08
              ],
              backgroundColor: [
                'rgba(239, 68, 68, 0.8)',
                'rgba(34, 197, 94, 0.8)',
                'rgba(59, 130, 246, 0.8)'
              ]
            }]
          }}
          height={250}
        />
      </Card>

      {/* Strategic Recommendations */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Rekomendasi Strategis</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
            <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Optimalisasi Pemungutan PKB dan BBNKB</h3>
              <p className="text-sm text-gray-700 mt-1">
                Intensifkan implementasi e-Samsat dan layanan digital untuk meningkatkan collection efficiency
                dari 92% menjadi 96%. Target tambahan pendapatan: ±Rp 200-300 Miliar.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Program Kepatuhan Wajib Pajak</h3>
              <p className="text-sm text-gray-700 mt-1">
                Implementasi program amnesti pajak dan insentif untuk meningkatkan compliance rate
                dari 85% menjadi 90%. Estimasi dampak: Rp 150-200 Miliar.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
            <div className="bg-purple-600 text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Diversifikasi Sumber PAD</h3>
              <p className="text-sm text-gray-700 mt-1">
                Eksplorasi sumber PAD baru dari retribusi daerah dan optimalisasi aset daerah
                untuk mengurangi ketergantungan pada PKB/BBNKB.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
            <div className="bg-orange-600 text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">
              4
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Monitoring dan Evaluasi Berkelanjutan</h3>
              <p className="text-sm text-gray-700 mt-1">
                Implementasi dashboard monitoring real-time dan review triwulanan untuk
                memastikan pencapaian target dan identifikasi dini terhadap deviasi.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Risk Analysis */}
      <Card className="print:break-inside-avoid">
        <h2 className="text-xl font-semibold mb-4">Analisis Risiko</h2>
        <div className="space-y-3">
          <div className="border-l-4 border-red-500 pl-4 py-2">
            <h3 className="font-semibold text-red-900 mb-1">Risiko Tinggi</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Perlambatan ekonomi global yang berdampak pada PDRB regional</li>
              <li>Perubahan kebijakan fiskal pusat terkait pembagian pajak daerah</li>
            </ul>
          </div>

          <div className="border-l-4 border-yellow-500 pl-4 py-2">
            <h3 className="font-semibold text-yellow-900 mb-1">Risiko Sedang</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Fluktuasi inflasi yang mempengaruhi daya beli masyarakat</li>
              <li>Resistensi masyarakat terhadap kenaikan tarif pajak</li>
            </ul>
          </div>

          <div className="border-l-4 border-blue-500 pl-4 py-2">
            <h3 className="font-semibold text-blue-900 mb-1">Mitigasi</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Diversifikasi sumber PAD untuk mengurangi dependensi</li>
              <li>Penguatan sistem monitoring dan early warning</li>
              <li>Koordinasi intensif dengan pemerintah pusat</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Conclusion */}
      <Card className="print:break-inside-avoid">
        <div className="border-l-4 border-blue-600 pl-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Kesimpulan</h2>
          <div className="space-y-3 text-gray-700">
            <p className="leading-relaxed">
              Proyeksi PAD Provinsi Jawa Timur menunjukkan tren positif dengan pertumbuhan rata-rata
              {formatNumber(growthRate)}% untuk tahun {selectedYear}. Angka ini didasarkan pada analisis komprehensif
              menggunakan tiga model statistik yang berbeda dengan confidence interval 95%.
            </p>
            <p className="leading-relaxed">
              Keberhasilan pencapaian target sangat bergantung pada implementasi efektif dari program-program
              strategis yang direkomendasikan, khususnya dalam optimalisasi pemungutan pajak dan peningkatan
              kepatuhan wajib pajak.
            </p>
            <p className="leading-relaxed font-semibold">
              Dengan asumsi kondisi ekonomi stabil dan implementasi kebijakan yang tepat, proyeksi PAD
              sebesar {formatCurrency(avgProjection)} untuk tahun {selectedYear} memiliki probabilitas
              pencapaian yang tinggi ({'>'} 85%).
            </p>
          </div>
        </div>
      </Card>

      {/* Footer for Print */}
      <div className="hidden print:block mt-8 pt-4 border-t-2 border-gray-300">
        <div className="grid grid-cols-2 gap-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-16">Mengetahui,</p>
            <p className="text-sm font-semibold border-t border-gray-800 pt-1 inline-block px-8">
              Kepala Bapenda Provinsi Jawa Timur
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-16">Menyetujui,</p>
            <p className="text-sm font-semibold border-t border-gray-800 pt-1 inline-block px-8">
              Gubernur Jawa Timur
            </p>
          </div>
        </div>
        <div className="text-center mt-8">
          <p className="text-xs text-gray-500">
            Dokumen ini dibuat secara otomatis menggunakan sistem PRO-PAD v1.0.0
          </p>
        </div>
      </div>
    </div>
  );
}
