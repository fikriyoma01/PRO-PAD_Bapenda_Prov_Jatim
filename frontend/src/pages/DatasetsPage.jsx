import { useState, useEffect } from 'react';
import { Database, Download, FileSpreadsheet } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import DataTable from '../components/ui/DataTable';
import Button from '../components/ui/Button';
import LineChart from '../components/charts/LineChart';
import { formatRupiah } from '../lib/utils';

export default function DatasetsPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    // Mock data for now
    const mockData = [
      {
        Tahun: 2018,
        PKB: 4000000000000,
        BBNKB: 2000000000000,
        PDRB: 2160000000000000,
        Gini: 0.379,
        IPM: 70.77,
        TPT: 3.99,
        Kemiskinan: 10.85,
        Inflasi: 3.20,
        SukuBunga: 6.00,
      },
      {
        Tahun: 2019,
        PKB: 4500000000000,
        BBNKB: 2300000000000,
        PDRB: 2280000000000000,
        Gini: 0.382,
        IPM: 71.5,
        TPT: 3.82,
        Kemiskinan: 10.37,
        Inflasi: 3.03,
        SukuBunga: 5.00,
      },
      {
        Tahun: 2020,
        PKB: 5000000000000,
        BBNKB: 2600000000000,
        PDRB: 2260000000000000,
        Gini: 0.384,
        IPM: 72.18,
        TPT: 5.82,
        Kemiskinan: 11.13,
        Inflasi: 1.68,
        SukuBunga: 3.75,
      },
      {
        Tahun: 2021,
        PKB: 5500000000000,
        BBNKB: 2900000000000,
        PDRB: 2340000000000000,
        Gini: 0.381,
        IPM: 72.22,
        TPT: 5.46,
        Kemiskinan: 10.68,
        Inflasi: 1.87,
        SukuBunga: 3.50,
      },
      {
        Tahun: 2022,
        PKB: 6000000000000,
        BBNKB: 3200000000000,
        PDRB: 2470000000000000,
        Gini: 0.375,
        IPM: 73.14,
        TPT: 4.93,
        Kemiskinan: 10.13,
        Inflasi: 5.51,
        SukuBunga: 5.50,
      },
      {
        Tahun: 2023,
        PKB: 6500000000000,
        BBNKB: 3500000000000,
        PDRB: 2610000000000000,
        Gini: 0.373,
        IPM: 73.52,
        TPT: 4.51,
        Kemiskinan: 9.78,
        Inflasi: 2.61,
        SukuBunga: 6.00,
      },
      {
        Tahun: 2024,
        PKB: 7000000000000,
        BBNKB: 3800000000000,
        PDRB: 2750000000000000,
        Gini: 0.370,
        IPM: 73.90,
        TPT: 4.20,
        Kemiskinan: 9.45,
        Inflasi: 2.84,
        SukuBunga: 6.25,
      },
    ];

    setData(mockData);
    setLoading(false);
  };

  const columns = [
    {
      accessorKey: 'Tahun',
      header: 'Tahun',
      cell: ({ getValue }) => getValue(),
    },
    {
      accessorKey: 'PKB',
      header: 'PKB (Rp)',
      cell: ({ getValue }) => formatRupiah(getValue()),
    },
    {
      accessorKey: 'BBNKB',
      header: 'BBNKB (Rp)',
      cell: ({ getValue }) => formatRupiah(getValue()),
    },
    {
      accessorKey: 'PDRB',
      header: 'PDRB (Rp)',
      cell: ({ getValue }) => formatRupiah(getValue()),
    },
    {
      accessorKey: 'Gini',
      header: 'Rasio Gini',
      cell: ({ getValue }) => getValue().toFixed(3),
    },
    {
      accessorKey: 'IPM',
      header: 'IPM',
      cell: ({ getValue }) => getValue().toFixed(2),
    },
    {
      accessorKey: 'TPT',
      header: 'TPT (%)',
      cell: ({ getValue }) => getValue().toFixed(2),
    },
    {
      accessorKey: 'Kemiskinan',
      header: 'Kemiskinan (%)',
      cell: ({ getValue }) => getValue().toFixed(2),
    },
    {
      accessorKey: 'Inflasi',
      header: 'Inflasi (%)',
      cell: ({ getValue }) => getValue().toFixed(2),
    },
    {
      accessorKey: 'SukuBunga',
      header: 'Suku Bunga (%)',
      cell: ({ getValue }) => getValue().toFixed(2),
    },
  ];

  // Prepare chart data
  const chartData = data.map(item => ({
    year: item.Tahun.toString(),
    PKB: item.PKB / 1e9,
    BBNKB: item.BBNKB / 1e9,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database size={32} />
            Dataset PAD Historis
          </h1>
          <p className="text-gray-600 mt-2">
            Data historis PAD Jawa Timur periode 2018-2024
          </p>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" icon={Download}>
            Export CSV
          </Button>
          <Button variant="outline" icon={FileSpreadsheet}>
            Export Excel
          </Button>
        </div>
      </div>

      {/* Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Tren PAD</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={chartData}
              lines={[
                { dataKey: 'PKB', name: 'PKB', color: '#3b82f6' },
                { dataKey: 'BBNKB', name: 'BBNKB', color: '#8b5cf6' },
              ]}
              xKey="year"
              formatY="currency"
              height={300}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistik Deskriptif</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <StatRow
                label="Jumlah Data"
                value={`${data.length} tahun`}
              />
              <StatRow
                label="Periode"
                value={`${data[0].Tahun} - ${data[data.length - 1].Tahun}`}
              />
              <StatRow
                label="PKB Rata-rata"
                value={formatRupiah(data.reduce((sum, d) => sum + d.PKB, 0) / data.length)}
              />
              <StatRow
                label="BBNKB Rata-rata"
                value={formatRupiah(data.reduce((sum, d) => sum + d.BBNKB, 0) / data.length)}
              />
              <StatRow
                label="Total PAD 2024"
                value={formatRupiah(data[data.length - 1].PKB + data[data.length - 1].BBNKB)}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Data Lengkap</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            data={data}
            columns={columns}
            pageSize={10}
          />
        </CardContent>
      </Card>
    </div>
  );
}

function StatRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      <span className="text-sm font-semibold text-gray-900">{value}</span>
    </div>
  );
}
