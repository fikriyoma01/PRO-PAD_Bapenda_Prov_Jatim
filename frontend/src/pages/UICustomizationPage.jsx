import { Settings } from 'lucide-react';

export default function UICustomizationPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Settings size={32} className="text-purple-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">UI Customization</h1>
          <p className="text-gray-600 mt-2">Kustomisasi tampilan dashboard</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-12 text-center">
        <Settings size={64} className="text-purple-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman UI Customization</h2>
        <p className="text-gray-600">
          Fitur kustomisasi UI akan tersedia segera.
          Theme, colors, dan typography settings.
        </p>
      </div>
    </div>
  );
}
