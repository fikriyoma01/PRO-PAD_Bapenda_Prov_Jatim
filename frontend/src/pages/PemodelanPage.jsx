import { LineChart as LineChartIcon } from 'lucide-react';

export default function PemodelanPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <LineChartIcon size={32} className="text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pemodelan Statistik</h1>
          <p className="text-gray-600 mt-2">OLS Regression, ARIMA, dan Exponential Smoothing</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-12 text-center">
        <LineChartIcon size={64} className="text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Pemodelan</h2>
        <p className="text-gray-600">
          Fitur pemodelan statistik akan tersedia segera.
          Model OLS, ARIMA, dan Exponential Smoothing untuk proyeksi PAD.
        </p>
      </div>
    </div>
  );
}
