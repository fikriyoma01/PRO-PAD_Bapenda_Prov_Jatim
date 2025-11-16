import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { formatRupiah } from '../../lib/utils';

export default function PieChart({ data, height = 400, formatValue = 'number' }) {
  // Handle both Recharts format and Chart.js-like format
  const isChartJsFormat = data && data.labels && data.datasets;

  let chartData = [];
  let colors = [];

  if (isChartJsFormat) {
    // Convert Chart.js format to Recharts format
    const dataset = data.datasets[0];
    chartData = data.labels.map((label, index) => ({
      name: label,
      value: dataset.data[index],
    }));
    colors = dataset.backgroundColor || [];
  } else {
    // Already in Recharts format
    chartData = data;
  }

  const formatTooltip = (value) => {
    if (formatValue === 'currency') {
      return formatRupiah(value);
    } else if (formatValue === 'percentage') {
      return `${value.toFixed(2)}%`;
    }
    return value.toLocaleString();
  };

  const COLORS = colors.length > 0 ? colors : [
    '#0891b2',
    '#06b6d4',
    '#22d3ee',
    '#67e8f9',
    '#a5f3fc',
    '#cffafe',
  ];

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(entry) => entry.name}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px',
            }}
            formatter={formatTooltip}
          />
          <Legend />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
}
