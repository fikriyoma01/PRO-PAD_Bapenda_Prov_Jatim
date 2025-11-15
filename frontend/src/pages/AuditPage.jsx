import { Activity } from 'lucide-react';

export default function AuditPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Activity size={32} className="text-purple-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-gray-600 mt-2">Log aktivitas dan perubahan sistem</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-12 text-center">
        <Activity size={64} className="text-purple-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Audit Trail</h2>
        <p className="text-gray-600">
          Fitur audit trail akan tersedia segera.
          Pelacakan lengkap aktivitas pengguna.
        </p>
      </div>
    </div>
  );
}
