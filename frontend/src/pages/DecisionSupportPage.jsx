import { CheckSquare } from 'lucide-react';

export default function DecisionSupportPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <CheckSquare size={32} className="text-green-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Decision Support</h1>
          <p className="text-gray-600 mt-2">Dukungan pengambilan keputusan berbasis data</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-12 text-center">
        <CheckSquare size={64} className="text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Decision Support</h2>
        <p className="text-gray-600">
          Fitur decision support akan tersedia segera.
          Executive summary dan rekomendasi strategis.
        </p>
      </div>
    </div>
  );
}
