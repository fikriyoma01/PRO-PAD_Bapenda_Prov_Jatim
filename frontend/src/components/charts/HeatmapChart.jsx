import React from 'react';

export default function HeatmapChart({
  data,
  variables,
  height = 400,
  title,
}) {
  // Find min and max values for color scaling
  const values = data.map(d => d.correlation);
  const min = Math.min(...values);
  const max = Math.max(...values);

  // Color scale function
  const getColor = (value) => {
    // Normalize value between 0 and 1
    const normalized = (value - min) / (max - min);

    // Color from red (negative) through white (zero) to blue (positive)
    if (value < 0) {
      const intensity = Math.abs(value);
      const r = 239;
      const g = Math.round(68 + (255 - 68) * (1 - intensity));
      const b = Math.round(68 + (255 - 68) * (1 - intensity));
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      const intensity = value;
      const r = Math.round(59 + (255 - 59) * (1 - intensity));
      const g = Math.round(130 + (255 - 130) * (1 - intensity));
      const b = Math.round(246 + (255 - 246) * (1 - intensity));
      return `rgb(${r}, ${g}, ${b})`;
    }
  };

  // Create grid
  const cellSize = Math.min(60, 400 / variables.length);

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}

      <div className="overflow-x-auto">
        <div style={{ minWidth: `${cellSize * variables.length}px` }}>
          {/* Headers */}
          <div className="flex">
            <div style={{ width: `${cellSize}px` }} className="flex-shrink-0"></div>
            {variables.map((var1, i) => (
              <div
                key={i}
                style={{ width: `${cellSize}px`, height: `${cellSize}px` }}
                className="flex items-center justify-center flex-shrink-0"
              >
                <span
                  className="text-xs font-medium text-gray-700 transform -rotate-45"
                  style={{ whiteSpace: 'nowrap' }}
                >
                  {var1}
                </span>
              </div>
            ))}
          </div>

          {/* Grid */}
          {variables.map((var1, i) => (
            <div key={i} className="flex">
              {/* Row label */}
              <div
                style={{ width: `${cellSize}px`, height: `${cellSize}px` }}
                className="flex items-center justify-end pr-2 flex-shrink-0"
              >
                <span className="text-xs font-medium text-gray-700">{var1}</span>
              </div>

              {/* Cells */}
              {variables.map((var2, j) => {
                const dataPoint = data.find(
                  (d) => d.var1 === var1 && d.var2 === var2
                );
                const value = dataPoint ? dataPoint.correlation : 0;
                const color = getColor(value);

                return (
                  <div
                    key={j}
                    style={{
                      width: `${cellSize}px`,
                      height: `${cellSize}px`,
                      backgroundColor: color,
                    }}
                    className="flex items-center justify-center border border-gray-200 relative group cursor-pointer flex-shrink-0"
                    title={`${var1} vs ${var2}: ${value.toFixed(3)}`}
                  >
                    <span className="text-xs font-semibold text-gray-800">
                      {value.toFixed(2)}
                    </span>

                    {/* Tooltip on hover */}
                    <div className="absolute invisible group-hover:visible bg-gray-900 text-white text-xs rounded py-1 px-2 -top-10 left-1/2 transform -translate-x-1/2 whitespace-nowrap z-10">
                      {var1} vs {var2}: {value.toFixed(3)}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Color legend */}
      <div className="flex items-center justify-center gap-4 mt-6">
        <span className="text-sm text-gray-600">-1.0</span>
        <div className="flex h-6 w-64">
          {Array.from({ length: 20 }).map((_, i) => {
            const value = -1 + (i / 19) * 2; // -1 to 1
            return (
              <div
                key={i}
                style={{
                  backgroundColor: getColor(value),
                  width: `${100 / 20}%`,
                }}
              />
            );
          })}
        </div>
        <span className="text-sm text-gray-600">+1.0</span>
      </div>

      <div className="text-center mt-2">
        <span className="text-xs text-gray-500">Correlation Coefficient</span>
      </div>
    </div>
  );
}
