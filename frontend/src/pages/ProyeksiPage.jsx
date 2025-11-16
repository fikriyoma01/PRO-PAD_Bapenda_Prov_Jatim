import { TrendingUp } from 'lucide-react';

export default function ProyeksiPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <TrendingUp size={32} className="text-purple-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Proyeksi PAD</h1>
          <p className="text-gray-600 mt-2">Proyeksi multi-tahun dengan confidence intervals</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-12 text-center">
        <TrendingUp size={64} className="text-purple-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Proyeksi</h2>
        <p className="text-gray-600">
          Fitur proyeksi PAD akan tersedia segera.
          Proyeksi 2025-2026 dengan berbagai skenario.
        </p>
      </div>
    </div>
  );
}
