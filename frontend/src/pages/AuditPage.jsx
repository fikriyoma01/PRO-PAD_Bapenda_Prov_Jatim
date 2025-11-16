import { useState, useEffect } from 'react';
import { Activity, Download, Search } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { auditAPI } from '../services/api';

export default function AuditPage() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const response = await auditAPI.getAuditTrail({ limit: 50 });
      setAuditLogs(response.data.data || []);
    } catch (err) {
      console.error('Error:', err);
      setAuditLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (isoString) => {
    if (!isoString) return '-';
    return new Date(isoString).toLocaleString('id-ID');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity size={32} className="text-purple-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
            <p className="text-gray-600 mt-2">Log aktivitas dan perubahan sistem</p>
          </div>
        </div>
        <Button onClick={loadAuditLogs}>
          <Download size={16} className="mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        {loading ? (
          <p className="text-center text-gray-500 py-8">Loading...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Module</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {auditLogs.map((log, idx) => (
                  <tr key={log.id || idx}>
                    <td className="px-6 py-4 text-sm">{formatDateTime(log.timestamp)}</td>
                    <td className="px-6 py-4 text-sm">{log.user || '-'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        {log.action || '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">{log.module || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {auditLogs.length === 0 && <p className="text-center text-gray-500 py-8">No logs found</p>}
          </div>
        )}
      </Card>
    </div>
  );
}
