---
name: data-viz
description: Create interactive data visualizations using JavaScript charting libraries. Use this skill when asked to create charts, graphs, dashboards, or data visualizations. Supports ECharts (recommended for most use cases), Vega-Lite (declarative grammar), Chart.js (simple charts), Plotly (scientific/3D), and D3.js (custom visualizations). Triggers include requests for bar charts, line charts, pie charts, scatter plots, heatmaps, treemaps, geographic maps, dashboards, or any visual representation of data.
---

# Data Visualization Skill

Create professional data visualizations using modern JavaScript charting libraries.

## Library Selection

Choose the right library based on use case:

| Use Case | Recommended Library |
|----------|-------------------|
| Most projects, dashboards, enterprise | **ECharts** |
| Quick prototypes, simple charts | **Chart.js** |
| Declarative specs, academic, exploratory | **Vega-Lite** |
| Scientific, 3D, statistical | **Plotly** |
| Highly custom, novel visualizations | **D3.js** |
| React applications | **Recharts** or **ECharts** |

**Default to ECharts** unless specific requirements suggest otherwise. It offers the best balance of features, performance, and ease of use.

## Quick Start Templates

### ECharts (Recommended)

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body>
  <div id="chart" style="width: 800px; height: 500px;"></div>
  <script>
    const chart = echarts.init(document.getElementById('chart'));
    const option = {
      title: { text: 'Chart Title' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['Series A'] },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [{ name: 'Series A', type: 'bar', data: [120, 200, 150, 80, 70] }]
    };
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
  </script>
</body>
</html>
```

### Vega-Lite

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <div id="vis"></div>
  <script>
    const spec = {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "data": { "values": [
        {"category": "A", "value": 28}, {"category": "B", "value": 55},
        {"category": "C", "value": 43}
      ]},
      "mark": "bar",
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    };
    vegaEmbed('#vis', spec);
  </script>
</body>
</html>
```

### Chart.js

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <canvas id="chart" width="800" height="400"></canvas>
  <script>
    new Chart(document.getElementById('chart'), {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{ label: 'Sales', data: [12, 19, 3, 5, 2], backgroundColor: 'rgba(54, 162, 235, 0.5)' }]
      },
      options: { responsive: true }
    });
  </script>
</body>
</html>
```

## Detailed Library Guides

For comprehensive documentation on each library:

- **ECharts**: See [references/echarts.md](references/echarts.md) for chart types, configuration, and examples
- **Vega-Lite**: See [references/vega-lite.md](references/vega-lite.md) for grammar, marks, and encodings
- **Library Comparison**: See [references/comparison.md](references/comparison.md) for detailed selection criteria

## Common Chart Types

| Chart Type | ECharts | Vega-Lite | Chart.js | Best For |
|------------|---------|-----------|----------|----------|
| Bar/Column | `type: 'bar'` | `mark: 'bar'` | `type: 'bar'` | Comparisons |
| Line | `type: 'line'` | `mark: 'line'` | `type: 'line'` | Trends |
| Pie/Donut | `type: 'pie'` | `mark: 'arc'` | `type: 'pie'` | Parts of whole |
| Scatter | `type: 'scatter'` | `mark: 'point'` | `type: 'scatter'` | Correlations |
| Area | `type: 'line', areaStyle: {}` | `mark: 'area'` | `type: 'line', fill: true` | Volume trends |
| Heatmap | `type: 'heatmap'` | `mark: 'rect'` | via plugin | Density |
| Treemap | `type: 'treemap'` | N/A | via plugin | Hierarchies |
| Map | `type: 'map'` | via geo | via plugin | Geographic |

## Best Practices

1. **Responsive Design**: Always handle window resize events
2. **Accessibility**: Include aria labels and color-blind friendly palettes
3. **Performance**: For >10k data points, use ECharts with Canvas renderer or sampling
4. **Tooltips**: Always enable for data exploration
5. **Loading States**: Show spinner while fetching data
6. **Error Handling**: Display friendly messages when data fails to load

## Data Formats

### Array of Objects (Most Common)
```javascript
const data = [
  { date: '2024-01', value: 100, category: 'A' },
  { date: '2024-02', value: 150, category: 'A' }
];
```

### ECharts Dataset Format
```javascript
const option = {
  dataset: {
    source: [
      ['product', '2015', '2016', '2017'],
      ['Matcha', 43.3, 85.8, 93.7],
      ['Milk Tea', 83.1, 73.4, 55.1]
    ]
  }
};
```

### Vega-Lite Inline Data
```json
{
  "data": {
    "values": [{"x": 1, "y": 2}, {"x": 2, "y": 4}]
  }
}
```

## Color Palettes

### Professional Defaults
```javascript
// ECharts categorical
const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272'];

// Sequential (for heatmaps, gradients)
const sequential = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];
```

## React Integration

For React projects, use the appropriate wrapper:

```jsx
// ECharts with echarts-for-react
import ReactECharts from 'echarts-for-react';

function Chart({ data }) {
  const option = {
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: data.values }]
  };
  return <ReactECharts option={option} style={{ height: 400 }} />;
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chart not rendering | Ensure container has explicit width/height |
| Resize not working | Call `chart.resize()` on window resize |
| Data not showing | Check data format matches expected structure |
| Performance lag | Reduce data points, use Canvas renderer, enable sampling |
| Tooltip cut off | Set `tooltip.confine: true` (ECharts) |
