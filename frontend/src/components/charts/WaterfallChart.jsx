import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import { formatCompactNumber, formatRupiah } from '../../lib/utils';

export default function WaterfallChart({
  data,
  dataKey = 'value',
  nameKey = 'name',
  height = 400,
  title,
}) {
  // Transform data for waterfall
  const waterfallData = data.map((item, index) => {
    const isBase = item.type === 'base';
    const isTotal = item.type === 'total';
    const isIncrease = item.type === 'increase' || item.value > 0;

    return {
      ...item,
      displayValue: item.value,
      start: item.start || 0,
      end: item.end || item.value,
      color: isBase ? '#3b82f6' : isTotal ? '#10b981' : isIncrease ? '#22c55e' : '#ef4444',
    };
  });

  const formatTooltip = (value) => formatRupiah(value);

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={waterfallData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey={nameKey}
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            tickFormatter={(value) => formatCompactNumber(value)}
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
          <Legend />

          {/* Invisible bar for positioning */}
          <Bar dataKey="start" stackId="a" fill="transparent" />

          {/* Visible bar */}
          <Bar dataKey={dataKey} stackId="a" radius={[4, 4, 0, 0]}>
            {waterfallData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>

          <ReferenceLine y={0} stroke="#000" strokeDasharray="3 3" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
