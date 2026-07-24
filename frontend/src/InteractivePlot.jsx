import React, { useRef, useImperativeHandle, forwardRef } from 'react';
import Plot from 'react-plotly.js';

const InteractivePlot = forwardRef(({ plotData, height = '300px' }, ref) => {
  const plotRef = useRef(null);

  useImperativeHandle(ref, () => ({
    toImage: async () => {
      // Access the internal Plotly object to download image
      if (plotRef.current && plotRef.current.el) {
        try {
          const dataUrl = await window.Plotly.toImage(plotRef.current.el, {
            format: 'png',
            width: 1200,
            height: 600,
          });
          return {
            filename: plotData.filename,
            data: dataUrl
          };
        } catch (e) {
          console.error("Failed to generate image:", e);
          return null;
        }
      }
      return null;
    }
  }));

  if (!plotData || !plotData.traces || !plotData.layout) {
    return <div>Invalid plot data</div>;
  }

  return (
    <Plot
      ref={plotRef}
      data={plotData.traces}
      layout={{
        ...plotData.layout,
        autosize: true,
        margin: { l: 60, r: 40, t: 60, b: 60 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: 'var(--text-color, #e0e0e0)' },
        xaxis: {
          ...(plotData.layout.xaxis || {}),
          gridcolor: 'rgba(255,255,255,0.1)',
          zerolinecolor: 'rgba(255,255,255,0.2)'
        },
        yaxis: {
          ...(plotData.layout.yaxis || {}),
          gridcolor: 'rgba(255,255,255,0.1)',
          zerolinecolor: 'rgba(255,255,255,0.2)'
        },
        yaxis2: plotData.layout.yaxis2 ? {
          ...plotData.layout.yaxis2,
          gridcolor: 'rgba(255,255,255,0.1)',
          zerolinecolor: 'rgba(255,255,255,0.2)'
        } : undefined
      }}
      config={{
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
      }}
      style={{ width: '100%', height: height }}
      useResizeHandler={true}
      className={`plot-container ${plotData.status === 'failed' ? 'plot-fail' : 'plot-pass'}`}
    />
  );
});

export default InteractivePlot;
