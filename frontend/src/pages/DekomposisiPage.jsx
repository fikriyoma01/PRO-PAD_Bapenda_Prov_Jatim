import { BarChart3 } from 'lucide-react';

export default function DekomposisiPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BarChart3 size={32} className="text-green-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dekomposisi PAD</h1>
          <p className="text-gray-600 mt-2">Analisis faktor-faktor kontribusi PAD</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-12 text-center">
        <BarChart3 size={64} className="text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Dekomposisi</h2>
        <p className="text-gray-600">
          Fitur dekomposisi akan tersedia segera.
          Waterfall charts dan analisis komponen PAD.
        </p>
      </div>
    </div>
  );
}
