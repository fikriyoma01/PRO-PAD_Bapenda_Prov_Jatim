import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import { formatCompactNumber } from '../../lib/utils';

export default function TornadoChart({
  data,
  variableKey = 'variable',
  positiveKey = 'impact_positive',
  negativeKey = 'impact_negative',
  height = 400,
  title,
}) {
  // Transform data for tornado (sorted by total impact)
  const tornadoData = data.map((item) => ({
    ...item,
    [positiveKey]: Math.abs(item[positiveKey]),
    [negativeKey]: -Math.abs(item[negativeKey]),
  }));

  const formatTooltip = (value) => {
    const absValue = Math.abs(value);
    return formatCompactNumber(absValue);
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={tornadoData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            type="number"
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            tickFormatter={(value) => formatCompactNumber(Math.abs(value))}
          />
          <YAxis
            type="category"
            dataKey={variableKey}
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            width={90}
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

          {/* Reference line at zero */}
          <ReferenceLine x={0} stroke="#000" strokeWidth={2} />

          {/* Negative impact (left side) */}
          <Bar dataKey={negativeKey} name="Negative Impact" fill="#ef4444" radius={[4, 0, 0, 4]} />

          {/* Positive impact (right side) */}
          <Bar dataKey={positiveKey} name="Positive Impact" fill="#22c55e" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-sm text-gray-600">Negative Impact (-10%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-sm text-gray-600">Positive Impact (+10%)</span>
        </div>
      </div>
    </div>
  );
}
