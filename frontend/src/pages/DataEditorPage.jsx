import { useState, useEffect } from 'react';
import { Database, Download, Upload, Save, Plus } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import DataTable from '../components/DataTable';
import { dataAPI } from '../services/api';

export default function DataEditorPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await dataAPI.loadHistoricalData();
      setData(response.data.data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await dataAPI.exportData('historical', 'excel');
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'pad_historis.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '-';
    return new Intl.NumberFormat('id-ID', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const columns = data.length > 0 ? Object.keys(data[0]).map(key => ({
    key,
    label: key,
    render: (value) => {
      if (key === 'Tahun') return value;
      if (typeof value === 'number') return formatCurrency(value);
      return value;
    }
  })) : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Database size={32} className="text-teal-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Data Editor</h1>
            <p className="text-gray-600 mt-2">Edit dan kelola data historis</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download size={16} className="mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <Upload size={16} className="mr-2" />
            Import
          </Button>
          <Button onClick={() => setEditMode(!editMode)}>
            {editMode ? <Save size={16} className="mr-2" /> : <Plus size={16} className="mr-2" />}
            {editMode ? 'Save' : 'Add Row'}
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            Total Records: <span className="font-semibold">{data.length}</span>
          </p>
        </div>

        {loading ? (
          <p className="text-center text-gray-500 py-8">Loading...</p>
        ) : (
          <DataTable data={data} columns={columns} />
        )}
      </Card>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> Pastikan untuk membackup data sebelum melakukan perubahan.
          Perubahan data akan mempengaruhi semua proyeksi dan analisis.
        </p>
      </div>
    </div>
  );
}
