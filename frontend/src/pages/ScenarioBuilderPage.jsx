import { Layers } from 'lucide-react';

export default function ScenarioBuilderPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Layers size={32} className="text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scenario Builder</h1>
          <p className="text-gray-600 mt-2">Analisis what-if interaktif</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-12 text-center">
        <Layers size={64} className="text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Halaman Scenario Builder</h2>
        <p className="text-gray-600">
          Fitur scenario builder akan tersedia segera.
          Simulasi berbagai skenario ekonomi dan kebijakan.
        </p>
      </div>
    </div>
  );
}
