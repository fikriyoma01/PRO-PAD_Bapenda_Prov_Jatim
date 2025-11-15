import { Edit } from 'lucide-react';

export default function VariableManagerPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Edit size={32} className="text-orange-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Variable Manager</h1>
          <p className="text-gray-600 mt-2">Kelola variabel model</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-12 text-center">
        <Edit size={64} className="text-orange-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Variable Manager</h2>
        <p className="text-gray-600">
          Fitur variable manager akan tersedia segera.
          Konfigurasi variabel prediktor dan response.
        </p>
      </div>
    </div>
  );
}
