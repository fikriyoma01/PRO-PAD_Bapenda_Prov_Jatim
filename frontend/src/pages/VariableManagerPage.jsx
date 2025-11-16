import { useState, useEffect } from 'react';
import { Edit, Plus, Trash2, Save, Download, Upload, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const DEFAULT_VARIABLES = [
  {
    id: 1,
    name: 'PAD',
    label: 'Pendapatan Asli Daerah',
    type: 'response',
    unit: 'Miliar Rp',
    enabled: true,
    editable: false
  },
  {
    id: 2,
    name: 'PDRB',
    label: 'Produk Domestik Regional Bruto',
    type: 'predictor',
    unit: 'Triliun Rp',
    enabled: true,
    importance: 'high',
    editable: true
  },
  {
    id: 3,
    name: 'Rasio Gini',
    label: 'Rasio Gini (Ketimpangan)',
    type: 'predictor',
    unit: 'Index',
    enabled: true,
    importance: 'medium',
    editable: true
  },
  {
    id: 4,
    name: 'Inflasi',
    label: 'Tingkat Inflasi',
    type: 'predictor',
    unit: '%',
    enabled: true,
    importance: 'medium',
    editable: true
  },
  {
    id: 5,
    name: 'PKB',
    label: 'Pajak Kendaraan Bermotor',
    type: 'predictor',
    unit: 'Miliar Rp',
    enabled: true,
    importance: 'high',
    editable: true
  },
  {
    id: 6,
    name: 'BBNKB',
    label: 'Bea Balik Nama Kendaraan Bermotor',
    type: 'predictor',
    unit: 'Miliar Rp',
    enabled: true,
    importance: 'high',
    editable: true
  },
  {
    id: 7,
    name: 'Pertumbuhan Ekonomi',
    label: 'Pertumbuhan Ekonomi',
    type: 'predictor',
    unit: '%',
    enabled: true,
    importance: 'high',
    editable: true
  }
];

export default function VariableManagerPage() {
  const [variables, setVariables] = useState(DEFAULT_VARIABLES);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVariable, setNewVariable] = useState({
    name: '',
    label: '',
    type: 'predictor',
    unit: '',
    enabled: true,
    importance: 'medium'
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    loadVariables();
  }, []);

  const loadVariables = () => {
    const saved = localStorage.getItem('model_variables');
    if (saved) {
      setVariables(JSON.parse(saved));
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem('model_variables', JSON.stringify(variables));
      setSaveStatus('success');
      setHasChanges(false);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error('Error saving:', err);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(variables, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'model_variables.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target.result);
          setVariables(imported);
          setHasChanges(true);
        } catch (err) {
          console.error('Error importing:', err);
          alert('Error importing file. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleToggleEnabled = (id) => {
    setVariables(prev => prev.map(v =>
      v.id === id ? { ...v, enabled: !v.enabled } : v
    ));
    setHasChanges(true);
  };

  const handleStartEdit = (variable) => {
    setEditingId(variable.id);
    setEditForm(variable);
  };

  const handleSaveEdit = () => {
    setVariables(prev => prev.map(v =>
      v.id === editingId ? editForm : v
    ));
    setEditingId(null);
    setEditForm({});
    setHasChanges(true);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const handleDelete = (id) => {
    if (confirm('Apakah Anda yakin ingin menghapus variabel ini?')) {
      setVariables(prev => prev.filter(v => v.id !== id));
      setHasChanges(true);
    }
  };

  const handleAddVariable = () => {
    const newId = Math.max(...variables.map(v => v.id), 0) + 1;
    setVariables(prev => [...prev, { ...newVariable, id: newId, editable: true }]);
    setNewVariable({
      name: '',
      label: '',
      type: 'predictor',
      unit: '',
      enabled: true,
      importance: 'medium'
    });
    setShowAddForm(false);
    setHasChanges(true);
  };

  const predictorCount = variables.filter(v => v.type === 'predictor' && v.enabled).length;
  const responseCount = variables.filter(v => v.type === 'response' && v.enabled).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Edit size={32} className="text-orange-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Variable Manager</h1>
            <p className="text-gray-600 mt-2">Kelola variabel model dan konfigurasi</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download size={16} className="mr-2" />
            Export
          </Button>
          <label>
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
            <Button variant="outline" as="span">
              <Upload size={16} className="mr-2" />
              Import
            </Button>
          </label>
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save size={16} className="mr-2" />
            {saveStatus === 'success' ? 'Saved!' : 'Save'}
          </Button>
        </div>
      </div>

      {/* Status Banners */}
      {saveStatus === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="text-green-600" size={24} />
          <p className="text-green-800 font-medium">Konfigurasi variabel berhasil disimpan!</p>
        </div>
      )}

      {hasChanges && !saveStatus && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="text-yellow-600" size={24} />
          <p className="text-yellow-800 font-medium">Ada perubahan yang belum disimpan</p>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <TrendingUp className="text-blue-600" size={32} />
            <div>
              <p className="text-sm text-gray-600">Total Variables</p>
              <p className="text-2xl font-bold text-gray-900">{variables.length}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-600" size={32} />
            <div>
              <p className="text-sm text-gray-600">Active Predictors</p>
              <p className="text-2xl font-bold text-gray-900">{predictorCount}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <AlertCircle className="text-orange-600" size={32} />
            <div>
              <p className="text-sm text-gray-600">Response Variables</p>
              <p className="text-2xl font-bold text-gray-900">{responseCount}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Variables Table */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Daftar Variabel</h2>
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            <Plus size={16} className="mr-2" />
            Add Variable
          </Button>
        </div>

        {/* Add Form */}
        {showAddForm && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold mb-3">Tambah Variabel Baru</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newVariable.name}
                  onChange={(e) => setNewVariable(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., Population"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Label</label>
                <input
                  type="text"
                  value={newVariable.label}
                  onChange={(e) => setNewVariable(prev => ({ ...prev, label: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., Jumlah Penduduk"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={newVariable.type}
                  onChange={(e) => setNewVariable(prev => ({ ...prev, type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="predictor">Predictor</option>
                  <option value="response">Response</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                <input
                  type="text"
                  value={newVariable.unit}
                  onChange={(e) => setNewVariable(prev => ({ ...prev, unit: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., Juta Orang"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Importance</label>
                <select
                  value={newVariable.importance}
                  onChange={(e) => setNewVariable(prev => ({ ...prev, importance: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              <Button onClick={handleAddVariable}>Add Variable</Button>
              <Button variant="outline" onClick={() => setShowAddForm(false)}>Cancel</Button>
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Label</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Importance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {variables.map((variable) => (
                <tr key={variable.id} className={!variable.enabled ? 'opacity-50' : ''}>
                  {editingId === variable.id ? (
                    <>
                      <td className="px-6 py-4">
                        <input
                          type="text"
                          value={editForm.name}
                          onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="text"
                          value={editForm.label}
                          onChange={(e) => setEditForm(prev => ({ ...prev, label: e.target.value }))}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={editForm.type}
                          onChange={(e) => setEditForm(prev => ({ ...prev, type: e.target.value }))}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                        >
                          <option value="predictor">Predictor</option>
                          <option value="response">Response</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="text"
                          value={editForm.unit}
                          onChange={(e) => setEditForm(prev => ({ ...prev, unit: e.target.value }))}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={editForm.importance}
                          onChange={(e) => setEditForm(prev => ({ ...prev, importance: e.target.value }))}
                          className="w-full px-2 py-1 border border-gray-300 rounded"
                        >
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={editForm.enabled}
                            onChange={(e) => setEditForm(prev => ({ ...prev, enabled: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-600"></div>
                        </label>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={handleSaveEdit}
                            className="text-green-600 hover:text-green-800"
                          >
                            <CheckCircle size={18} />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="text-gray-600 hover:text-gray-800"
                          >
                            <AlertCircle size={18} />
                          </button>
                        </div>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{variable.name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{variable.label}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          variable.type === 'response'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {variable.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{variable.unit}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          variable.importance === 'high'
                            ? 'bg-red-100 text-red-800'
                            : variable.importance === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {variable.importance || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={variable.enabled}
                            onChange={() => handleToggleEnabled(variable.id)}
                            className="sr-only peer"
                          />
                          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-600"></div>
                        </label>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex gap-2 justify-end">
                          {variable.editable && (
                            <>
                              <button
                                onClick={() => handleStartEdit(variable)}
                                className="text-orange-600 hover:text-orange-800"
                              >
                                <Edit size={18} />
                              </button>
                              <button
                                onClick={() => handleDelete(variable.id)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <Trash2 size={18} />
                              </button>
                            </>
                          )}
                          {!variable.editable && (
                            <span className="text-xs text-gray-400">System</span>
                          )}
                        </div>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Info */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Informasi</h2>
        <div className="space-y-3 text-sm text-gray-600">
          <p><strong>Predictor Variables:</strong> Variabel independen yang digunakan untuk memprediksi response variable.</p>
          <p><strong>Response Variables:</strong> Variabel dependen yang menjadi target prediksi (biasanya PAD).</p>
          <p><strong>Importance:</strong> Tingkat kepentingan variabel dalam model (High = sangat penting, Medium = penting, Low = opsional).</p>
          <p><strong>Status:</strong> Toggle untuk mengaktifkan/menonaktifkan variabel dalam model tanpa menghapusnya.</p>
        </div>
      </Card>
    </div>
  );
}
