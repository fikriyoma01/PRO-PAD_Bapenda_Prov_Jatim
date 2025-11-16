import { BookOpen } from 'lucide-react';

export default function MetodologiPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BookOpen size={32} className="text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Metodologi</h1>
          <p className="text-gray-600 mt-2">Dokumentasi metodologi dan teknis</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-12 text-center">
        <BookOpen size={64} className="text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Metodologi</h2>
        <p className="text-gray-600">
          Dokumentasi metodologi akan tersedia segera.
          Penjelasan lengkap model dan metode statistik.
        </p>
      </div>
    </div>
  );
}
