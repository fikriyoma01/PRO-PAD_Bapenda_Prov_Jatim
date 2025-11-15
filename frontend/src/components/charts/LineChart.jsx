import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { formatCompactNumber, formatRupiah } from '../../lib/utils';

export default function LineChart({
  data,
  lines = [],
  xKey = 'x',
  height = 400,
  showGrid = true,
  showLegend = true,
  formatY = 'number',
  title,
}) {
  const formatYAxis = (value) => {
    if (formatY === 'currency') {
      return formatCompactNumber(value);
    } else if (formatY === 'percentage') {
      return `${value}%`;
    }
    return formatCompactNumber(value);
  };

  const formatTooltip = (value) => {
    if (formatY === 'currency') {
      return formatRupiah(value);
    } else if (formatY === 'percentage') {
      return `${value.toFixed(2)}%`;
    }
    return value.toLocaleString();
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
          <XAxis
            dataKey={xKey}
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            tickFormatter={formatYAxis}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px',
            }}
            formatter={formatTooltip}
          />
          {showLegend && <Legend />}
          {lines.map((line, index) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name || line.dataKey}
              stroke={line.color || `hsl(${index * 60}, 70%, 50%)`}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}
