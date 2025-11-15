import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export default function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  iconColor = 'text-blue-600',
  iconBgColor = 'bg-blue-100',
  className
}) {
  const isPositive = change >= 0;

  return (
    <div className={cn('metric-card', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-2">{value}</p>

          {change !== undefined && (
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  'flex items-center gap-1 text-sm font-medium',
                  isPositive ? 'text-green-600' : 'text-red-600'
                )}
              >
                {isPositive ? (
                  <TrendingUp size={16} />
                ) : (
                  <TrendingDown size={16} />
                )}
                <span>{Math.abs(change).toFixed(2)}%</span>
              </div>
              {changeLabel && (
                <span className="text-sm text-gray-500">{changeLabel}</span>
              )}
            </div>
          )}
        </div>

        {Icon && (
          <div className={cn('p-3 rounded-lg', iconBgColor)}>
            <Icon size={24} className={iconColor} />
          </div>
        )}
      </div>
    </div>
  );
}
