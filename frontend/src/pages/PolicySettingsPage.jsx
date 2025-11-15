import { Users } from 'lucide-react';

export default function PolicySettingsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Users size={32} className="text-red-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Policy Settings</h1>
          <p className="text-gray-600 mt-2">Pengaturan kebijakan dan target</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-lg p-12 text-center">
        <Users size={64} className="text-red-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Policy Settings</h2>
        <p className="text-gray-600">
          Fitur policy settings akan tersedia segera.
          Target PAD dan parameter kebijakan.
        </p>
      </div>
    </div>
  );
}
