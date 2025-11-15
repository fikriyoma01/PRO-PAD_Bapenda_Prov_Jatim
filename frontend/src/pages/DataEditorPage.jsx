import { Database } from 'lucide-react';

export default function DataEditorPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Database size={32} className="text-teal-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Editor</h1>
          <p className="text-gray-600 mt-2">Edit dan kelola data historis</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-teal-50 to-teal-100 border border-teal-200 rounded-lg p-12 text-center">
        <Database size={64} className="text-teal-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Data Editor</h2>
        <p className="text-gray-600">
          Fitur data editor akan tersedia segera.
          CRUD operations untuk data historis.
        </p>
      </div>
    </div>
  );
}
