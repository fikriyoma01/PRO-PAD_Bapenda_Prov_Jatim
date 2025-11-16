import { BookOpen, TrendingUp, BarChart3, Activity, FileText, AlertCircle } from 'lucide-react';
import Card from '../components/ui/Card';

export default function MetodologiPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BookOpen size={32} className="text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Metodologi</h1>
          <p className="text-gray-600 mt-2">Dokumentasi metodologi dan teknis sistem PRO-PAD</p>
        </div>
      </div>

      {/* Overview */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <FileText size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Ringkasan Sistem</h2>
        </div>
        <div className="space-y-3 text-gray-700">
          <p>
            <strong>PRO-PAD (Proyeksi Pendapatan Asli Daerah)</strong> adalah sistem analitik berbasis web
            yang dirancang untuk membantu Badan Pendapatan Daerah (Bapenda) Provinsi Jawa Timur dalam
            memprediksi dan menganalisis Pendapatan Asli Daerah (PAD).
          </p>
          <p>
            Sistem ini menggunakan kombinasi metode statistik dan machine learning untuk menghasilkan
            proyeksi PAD yang akurat, serta menyediakan berbagai tools analisis untuk mendukung
            pengambilan keputusan strategis.
          </p>
        </div>
      </Card>

      {/* Data Sources */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <BarChart3 size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Sumber Data</h2>
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Data Historis PAD</h3>
            <p className="text-gray-700 mb-2">
              Data time series PAD dan komponennya (PKB, BBNKB) dari tahun 2015-2024.
              Data bersumber dari:
            </p>
            <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
              <li>Laporan Realisasi Anggaran (LRA) Bapenda Provinsi Jawa Timur</li>
              <li>Sistem Informasi Pajak Daerah (SIPD)</li>
              <li>Database SAMSAT provinsi</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Variabel Prediktor</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variabel</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sumber</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Update</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-4 py-3 text-sm text-gray-900">PDRB</td>
                    <td className="px-4 py-3 text-sm text-gray-700">BPS Jawa Timur</td>
                    <td className="px-4 py-3 text-sm text-gray-700">Tahunan</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-sm text-gray-900">Inflasi</td>
                    <td className="px-4 py-3 text-sm text-gray-700">BPS / Bank Indonesia</td>
                    <td className="px-4 py-3 text-sm text-gray-700">Bulanan</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-sm text-gray-900">Rasio Gini</td>
                    <td className="px-4 py-3 text-sm text-gray-700">BPS Jawa Timur</td>
                    <td className="px-4 py-3 text-sm text-gray-700">Tahunan</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-sm text-gray-900">Pertumbuhan Ekonomi</td>
                    <td className="px-4 py-3 text-sm text-gray-700">BPS Jawa Timur</td>
                    <td className="px-4 py-3 text-sm text-gray-700">Triwulanan</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Card>

      {/* Statistical Models */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Model Statistik</h2>
        </div>

        <div className="space-y-6">
          {/* OLS Regression */}
          <div className="border-l-4 border-blue-500 pl-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">1. OLS Regression (Ordinary Least Squares)</h3>
            <p className="text-gray-700 mb-3">
              Model regresi linear yang memodelkan hubungan antara PAD dengan variabel prediktor.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mb-3">
              <code className="text-sm text-gray-800">
                PAD<sub>t</sub> = β<sub>0</sub> + β<sub>1</sub>×PDRB<sub>t</sub> + β<sub>2</sub>×Inflasi<sub>t</sub> + β<sub>3</sub>×Gini<sub>t</sub> + ... + ε<sub>t</sub>
              </code>
            </div>
            <div>
              <p className="font-semibold text-gray-900 mb-1">Keunggulan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Interpretasi yang mudah dan intuitif</li>
                <li>Dapat mengidentifikasi pengaruh masing-masing variabel</li>
                <li>Cocok untuk analisis kausal</li>
              </ul>
              <p className="font-semibold text-gray-900 mt-3 mb-1">Keterbatasan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Asumsi linearitas yang ketat</li>
                <li>Rentan terhadap multikolinearitas</li>
                <li>Tidak menangkap pola temporal kompleks</li>
              </ul>
            </div>
          </div>

          {/* ARIMA */}
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">2. ARIMA (AutoRegressive Integrated Moving Average)</h3>
            <p className="text-gray-700 mb-3">
              Model time series yang menangkap pola autoregressive dan moving average dalam data.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mb-3">
              <code className="text-sm text-gray-800">
                ARIMA(p, d, q) dimana p=order AR, d=differencing, q=order MA
              </code>
            </div>
            <div>
              <p className="font-semibold text-gray-900 mb-1">Keunggulan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Menangkap pola temporal dan seasonality</li>
                <li>Tidak memerlukan variabel eksternal</li>
                <li>Robust untuk data non-stasioner</li>
              </ul>
              <p className="font-semibold text-gray-900 mt-3 mb-1">Keterbatasan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Memerlukan data time series yang panjang</li>
                <li>Tidak bisa memasukkan variabel eksternal dengan mudah</li>
                <li>Parameter tuning yang kompleks</li>
              </ul>
            </div>
          </div>

          {/* Exponential Smoothing */}
          <div className="border-l-4 border-purple-500 pl-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">3. Exponential Smoothing</h3>
            <p className="text-gray-700 mb-3">
              Model yang memberikan bobot lebih besar pada observasi yang lebih baru.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mb-3">
              <code className="text-sm text-gray-800">
                ŷ<sub>t+1</sub> = α×y<sub>t</sub> + (1-α)×ŷ<sub>t</sub>
              </code>
            </div>
            <div>
              <p className="font-semibold text-gray-900 mb-1">Keunggulan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Sederhana dan cepat dalam komputasi</li>
                <li>Adaptif terhadap perubahan trend</li>
                <li>Cocok untuk short-term forecasting</li>
              </ul>
              <p className="font-semibold text-gray-900 mt-3 mb-1">Keterbatasan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Terbatas untuk pola yang sederhana</li>
                <li>Tidak menangkap hubungan kausal</li>
                <li>Kurang akurat untuk long-term forecast</li>
              </ul>
            </div>
          </div>

          {/* Ensemble */}
          <div className="border-l-4 border-orange-500 pl-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">4. Ensemble Model</h3>
            <p className="text-gray-700 mb-3">
              Kombinasi dari ketiga model di atas untuk meningkatkan akurasi prediksi.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mb-3">
              <code className="text-sm text-gray-800">
                Forecast = w<sub>1</sub>×OLS + w<sub>2</sub>×ARIMA + w<sub>3</sub>×ExpSmooth
              </code>
            </div>
            <div>
              <p className="font-semibold text-gray-900 mb-1">Keunggulan:</p>
              <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
                <li>Menggabungkan kekuatan masing-masing model</li>
                <li>Lebih robust terhadap outlier dan perubahan pola</li>
                <li>Umumnya memberikan akurasi tertinggi</li>
              </ul>
              <p className="font-semibold text-gray-900 mt-3 mb-1">Implementasi:</p>
              <p className="text-gray-700 ml-4">
                Sistem menggunakan rata-rata tertimbang (weighted average) dengan bobot yang ditentukan
                berdasarkan performa historis masing-masing model (inverse RMSE).
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Model Evaluation */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Activity size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Evaluasi Model</h2>
        </div>

        <div className="space-y-4">
          <p className="text-gray-700">
            Sistem menggunakan beberapa metrik untuk mengevaluasi akurasi model:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">RMSE (Root Mean Squared Error)</h4>
              <div className="bg-white rounded p-2 mb-2">
                <code className="text-sm text-gray-800">RMSE = √(Σ(y<sub>i</sub> - ŷ<sub>i</sub>)<sup>2</sup> / n)</code>
              </div>
              <p className="text-sm text-blue-800">
                Mengukur rata-rata kesalahan prediksi dalam satuan yang sama dengan data asli.
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2">MAPE (Mean Absolute Percentage Error)</h4>
              <div className="bg-white rounded p-2 mb-2">
                <code className="text-sm text-gray-800">MAPE = (100/n) × Σ|y<sub>i</sub> - ŷ<sub>i</sub>| / y<sub>i</sub></code>
              </div>
              <p className="text-sm text-green-800">
                Mengukur kesalahan dalam bentuk persentase, memudahkan interpretasi.
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <h4 className="font-semibold text-purple-900 mb-2">R² (Coefficient of Determination)</h4>
              <div className="bg-white rounded p-2 mb-2">
                <code className="text-sm text-gray-800">R² = 1 - (SS<sub>res</sub> / SS<sub>tot</sub>)</code>
              </div>
              <p className="text-sm text-purple-800">
                Menunjukkan seberapa baik model menjelaskan variasi dalam data (0-1).
              </p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg">
              <h4 className="font-semibold text-orange-900 mb-2">MAE (Mean Absolute Error)</h4>
              <div className="bg-white rounded p-2 mb-2">
                <code className="text-sm text-gray-800">MAE = (1/n) × Σ|y<sub>i</sub> - ŷ<sub>i</sub>|</code>
              </div>
              <p className="text-sm text-orange-800">
                Mengukur rata-rata kesalahan absolut, lebih robust terhadap outlier.
              </p>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
            <p className="text-sm text-yellow-800">
              <strong>Validasi:</strong> Sistem menggunakan time series cross-validation dengan rolling window
              untuk memastikan model tidak overfitting dan dapat generalisasi dengan baik pada data baru.
            </p>
          </div>
        </div>
      </Card>

      {/* Assumptions & Limitations */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Asumsi dan Keterbatasan</h2>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Asumsi Model</h3>
            <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
              <li>Hubungan historis antara variabel prediktor dan PAD tetap konsisten</li>
              <li>Tidak ada perubahan struktural besar dalam sistem perpajakan</li>
              <li>Data input akurat dan representatif</li>
              <li>Kondisi makroekonomi relatif stabil</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Keterbatasan</h3>
            <ul className="list-disc list-inside text-gray-700 ml-4 space-y-1">
              <li>Model tidak dapat memprediksi shock eksternal (pandemi, krisis ekonomi, dll)</li>
              <li>Akurasi menurun untuk proyeksi jangka panjang (&gt;3 tahun)</li>
              <li>Perubahan kebijakan pajak yang signifikan memerlukan rekalibrasi model</li>
              <li>Data historis terbatas (10 tahun) dapat mempengaruhi akurasi model</li>
            </ul>
          </div>

          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <p className="text-sm text-red-800">
              <strong>Penting:</strong> Hasil proyeksi harus digunakan sebagai salah satu input dalam
              pengambilan keputusan, bukan satu-satunya penentu. Pertimbangan expert judgment dan
              faktor kualitatif tetap diperlukan.
            </p>
          </div>
        </div>
      </Card>

      {/* Technical Implementation */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <BookOpen size={24} className="text-blue-600" />
          <h2 className="text-2xl font-semibold">Implementasi Teknis</h2>
        </div>

        <div className="space-y-3 text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Stack Teknologi</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-900">Frontend</p>
                <p className="text-sm text-gray-600">React 19, Vite, TailwindCSS, Recharts</p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-900">Backend</p>
                <p className="text-sm text-gray-600">FastAPI, Python 3.11+</p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-900">Statistical Libraries</p>
                <p className="text-sm text-gray-600">Statsmodels, Scikit-learn, Pandas, NumPy</p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <p className="font-medium text-gray-900">Data Storage</p>
                <p className="text-sm text-gray-600">CSV files, JSON, LocalStorage</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-2">API Endpoints</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-gray-500">Endpoint</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500">Method</th>
                    <th className="px-4 py-2 text-left font-medium text-gray-500">Deskripsi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr>
                    <td className="px-4 py-2 font-mono text-xs">/api/projection/generate</td>
                    <td className="px-4 py-2">POST</td>
                    <td className="px-4 py-2">Generate PAD projection</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono text-xs">/api/data/historical</td>
                    <td className="px-4 py-2">GET</td>
                    <td className="px-4 py-2">Load historical data</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono text-xs">/api/analysis/correlation</td>
                    <td className="px-4 py-2">POST</td>
                    <td className="px-4 py-2">Correlation analysis</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2 font-mono text-xs">/api/audit/trail</td>
                    <td className="px-4 py-2">GET</td>
                    <td className="px-4 py-2">Audit trail logs</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Card>

      {/* References */}
      <Card>
        <h2 className="text-2xl font-semibold mb-4">Referensi</h2>
        <div className="space-y-2 text-sm text-gray-700">
          <p>1. Box, G. E. P., & Jenkins, G. M. (2015). Time Series Analysis: Forecasting and Control. Wiley.</p>
          <p>2. Hyndman, R. J., & Athanasopoulos, G. (2021). Forecasting: Principles and Practice (3rd ed.).</p>
          <p>3. James, G., Witten, D., Hastie, T., & Tibshirani, R. (2021). An Introduction to Statistical Learning.</p>
          <p>4. Statsmodels Development Team. (2024). Statsmodels Documentation. https://www.statsmodels.org</p>
          <p>5. Badan Pusat Statistik Jawa Timur. (2024). Produk Domestik Regional Bruto.</p>
        </div>
      </Card>

      {/* Version Info */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <p className="text-sm text-gray-600">
          PRO-PAD System v1.0.0 | Bapenda Provinsi Jawa Timur | 2024
        </p>
      </div>
    </div>
  );
}
