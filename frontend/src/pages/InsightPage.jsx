import { Lightbulb } from 'lucide-react';

export default function InsightPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Lightbulb size={32} className="text-yellow-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Insight & Analisis</h1>
          <p className="text-gray-600 mt-2">Wawasan terintegrasi dari berbagai analisis</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-12 text-center">
        <Lightbulb size={64} className="text-yellow-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Insight</h2>
        <p className="text-gray-600">
          Fitur insight akan tersedia segera.
          Analisis terintegrasi dan rekomendasi strategis.
        </p>
      </div>
    </div>
  );
}
