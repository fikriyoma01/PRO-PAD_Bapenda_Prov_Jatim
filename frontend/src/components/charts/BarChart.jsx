import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { formatCompactNumber, formatRupiah } from '../../lib/utils';

export default function BarChart({
  data,
  bars = [],
  xKey = 'x',
  height = 400,
  showGrid = true,
  showLegend = true,
  formatY = 'number',
  title,
  layout = 'vertical',
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
        <RechartsBarChart
          data={data}
          layout={layout}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}

          {layout === 'vertical' ? (
            <>
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
            </>
          ) : (
            <>
              <XAxis
                type="number"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                tickFormatter={formatYAxis}
              />
              <YAxis
                type="category"
                dataKey={xKey}
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
              />
            </>
          )}

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
          {bars.map((bar, index) => (
            <Bar
              key={bar.dataKey}
              dataKey={bar.dataKey}
              name={bar.name || bar.dataKey}
              fill={bar.color || `hsl(${index * 60}, 70%, 50%)`}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}
