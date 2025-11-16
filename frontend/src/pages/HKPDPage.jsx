import { FileText } from 'lucide-react';

export default function HKPDPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FileText size={32} className="text-indigo-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">HKPD</h1>
          <p className="text-gray-600 mt-2">Implementasi skenario HKPD</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-lg p-12 text-center">
        <FileText size={64} className="text-indigo-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman HKPD</h2>
        <p className="text-gray-600">
          Fitur HKPD akan tersedia segera.
        </p>
      </div>
    </div>
  );
}
