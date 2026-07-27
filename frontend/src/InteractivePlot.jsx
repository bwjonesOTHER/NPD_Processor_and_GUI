import React, { useRef, useImperativeHandle, forwardRef, useState } from 'react';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js-dist-min';

const InteractivePlot = forwardRef(({ plotData, height = '300px', onPlotError }, ref) => {
  const plotRef = useRef(null);
  const [renderError, setRenderError] = useState(null);

  useImperativeHandle(ref, () => ({
    toImage: async () => {
      // Access the internal Plotly object to download image
      if (plotRef.current) {
        try {
          const plotlyObj = Plotly.default || Plotly;
          // In newer react-plotly.js, the ref directly resolves to the graph div
          const graphDiv = plotRef.current.el || plotRef.current;
          const dataUrl = await plotlyObj.toImage(graphDiv, {
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
    return <div style={{ color: '#ef4444', padding: '1rem' }}>Invalid plot data</div>;
  }

  const processedTraces = plotData.traces;

  if (renderError) {
    return (
      <div style={{
        color: '#ef4444',
        padding: '1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: height,
        border: '2px solid #ef4444',
        borderRadius: '8px',
        fontSize: '0.85rem',
        textAlign: 'center'
      }}>
        Plot render failed: {renderError}
      </div>
    );
  }

  const layoutConfig = {
    ...plotData.layout,
    autosize: true,
    margin: { l: 60, r: 40, t: 60, b: 60 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#e0e0e0' },
    xaxis: {
      ...(plotData.layout.xaxis || {}),
      gridcolor: 'rgba(255,255,255,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)'
    },
    yaxis: {
      ...(plotData.layout.yaxis || {}),
      gridcolor: 'rgba(255,255,255,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)'
    }
  };

  if (plotData.layout.yaxis2) {
    layoutConfig.yaxis2 = {
      ...plotData.layout.yaxis2,
      gridcolor: 'rgba(255,255,255,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)'
    };
  }

  return (
    <Plot
      ref={plotRef}
      data={processedTraces}
      layout={layoutConfig}
      config={{
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
      }}
      onError={(err) => {
        console.error('Plotly render error:', err);
        const msg = err?.message || String(err);
        setRenderError(msg);
        if (onPlotError) onPlotError(msg);
      }}
      style={{ width: '100%', height: height, position: 'relative', display: 'inline-block' }}
      useResizeHandler={true}
      className={`plot-container ${plotData.status === 'failed' ? 'plot-fail' : 'plot-pass'}`}
    />
  );
});

export default InteractivePlot;
