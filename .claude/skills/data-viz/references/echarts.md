# ECharts Reference

Apache ECharts is a powerful charting library optimized for both desktop and mobile.

## CDN Links

```html
<!-- Full build -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>

<!-- Or specific version -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
```

## Initialization

```javascript
// Basic init
const chart = echarts.init(document.getElementById('container'));

// With theme
const chart = echarts.init(document.getElementById('container'), 'dark');

// With renderer (canvas is default, svg for smaller datasets)
const chart = echarts.init(document.getElementById('container'), null, { renderer: 'svg' });

// Set options
chart.setOption(option);

// Handle resize
window.addEventListener('resize', () => chart.resize());

// Dispose when done
chart.dispose();
```

## Chart Types

### Line Chart
```javascript
{
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: [150, 230, 224, 218, 135],
    smooth: true,  // curved line
    areaStyle: {}  // fill area below
  }]
}
```

### Bar Chart
```javascript
{
  xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [120, 200, 150, 80, 70],
    barWidth: '60%',
    itemStyle: { borderRadius: [5, 5, 0, 0] }
  }]
}
```

### Pie Chart
```javascript
{
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],  // donut chart
    data: [
      { value: 1048, name: 'Search' },
      { value: 735, name: 'Direct' },
      { value: 580, name: 'Email' }
    ],
    emphasis: {
      itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' }
    }
  }]
}
```

### Scatter Plot
```javascript
{
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    type: 'scatter',
    symbolSize: 20,
    data: [[10.0, 8.04], [8.07, 6.95], [13.0, 7.58], [9.05, 8.81]]
  }]
}
```

### Heatmap
```javascript
{
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  yAxis: { type: 'category', data: ['Morning', 'Afternoon', 'Evening'] },
  visualMap: { min: 0, max: 10, calculable: true },
  series: [{
    type: 'heatmap',
    data: [[0, 0, 5], [0, 1, 1], [0, 2, 0], [1, 0, 7], [1, 1, 2]],
    label: { show: true }
  }]
}
```

### Treemap
```javascript
{
  series: [{
    type: 'treemap',
    data: [
      { name: 'Category A', value: 10, children: [
        { name: 'A1', value: 4 },
        { name: 'A2', value: 6 }
      ]},
      { name: 'Category B', value: 20 }
    ]
  }]
}
```

### Candlestick (Financial)
```javascript
{
  xAxis: { type: 'category', data: ['2024-01', '2024-02', '2024-03'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'candlestick',
    data: [
      [20, 34, 10, 38],  // [open, close, low, high]
      [40, 35, 30, 50],
      [31, 38, 33, 44]
    ]
  }]
}
```

### Radar Chart
```javascript
{
  radar: {
    indicator: [
      { name: 'Sales', max: 6500 },
      { name: 'Admin', max: 16000 },
      { name: 'Tech', max: 30000 },
      { name: 'Support', max: 38000 },
      { name: 'Dev', max: 52000 }
    ]
  },
  series: [{
    type: 'radar',
    data: [{ value: [4200, 3000, 20000, 35000, 50000], name: 'Budget' }]
  }]
}
```

### Gauge
```javascript
{
  series: [{
    type: 'gauge',
    progress: { show: true },
    detail: { formatter: '{value}%' },
    data: [{ value: 70, name: 'Score' }]
  }]
}
```

### Sankey Diagram
```javascript
{
  series: [{
    type: 'sankey',
    data: [
      { name: 'a' }, { name: 'b' }, { name: 'c' }
    ],
    links: [
      { source: 'a', target: 'b', value: 5 },
      { source: 'b', target: 'c', value: 3 }
    ]
  }]
}
```

### Graph (Network)
```javascript
{
  series: [{
    type: 'graph',
    layout: 'force',
    data: [
      { name: 'Node 1', symbolSize: 50 },
      { name: 'Node 2', symbolSize: 30 }
    ],
    links: [
      { source: 'Node 1', target: 'Node 2' }
    ],
    force: { repulsion: 100 }
  }]
}
```

## Common Components

### Title
```javascript
title: {
  text: 'Main Title',
  subtext: 'Subtitle',
  left: 'center'
}
```

### Legend
```javascript
legend: {
  data: ['Series A', 'Series B'],
  orient: 'vertical',
  right: 10,
  top: 'center'
}
```

### Tooltip
```javascript
tooltip: {
  trigger: 'axis',  // or 'item' for pie/scatter
  axisPointer: { type: 'cross' },
  formatter: '{b}: {c}'
}
```

### Toolbox
```javascript
toolbox: {
  feature: {
    saveAsImage: {},
    dataZoom: {},
    restore: {},
    dataView: {}
  }
}
```

### Data Zoom
```javascript
dataZoom: [
  { type: 'inside', start: 0, end: 100 },  // scroll/pinch zoom
  { type: 'slider', start: 0, end: 100 }   // slider control
]
```

### Visual Map (Color Encoding)
```javascript
visualMap: {
  min: 0,
  max: 100,
  calculable: true,
  inRange: { color: ['#50a3ba', '#eac736', '#d94e5d'] }
}
```

## Dataset (Data Management)

```javascript
{
  dataset: {
    source: [
      ['product', '2015', '2016', '2017'],
      ['Matcha', 43.3, 85.8, 93.7],
      ['Milk Tea', 83.1, 73.4, 55.1],
      ['Cheese', 86.4, 65.2, 82.5]
    ]
  },
  xAxis: { type: 'category' },
  yAxis: {},
  series: [
    { type: 'bar' },
    { type: 'bar' },
    { type: 'bar' }
  ]
}
```

## Multiple Series

```javascript
{
  legend: { data: ['Email', 'Video', 'Direct'] },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Email', type: 'line', data: [120, 132, 101] },
    { name: 'Video', type: 'line', data: [220, 182, 191] },
    { name: 'Direct', type: 'bar', data: [320, 302, 341] }
  ]
}
```

## Themes

```javascript
// Built-in themes
echarts.init(dom, 'dark');

// Register custom theme
echarts.registerTheme('myTheme', {
  color: ['#c23531', '#2f4554', '#61a0a8'],
  backgroundColor: '#f4f4f4'
});
echarts.init(dom, 'myTheme');
```

## Events

```javascript
chart.on('click', (params) => {
  console.log(params.name, params.value);
});

chart.on('legendselectchanged', (params) => {
  console.log(params.selected);
});

chart.on('datazoom', (params) => {
  console.log(params.start, params.end);
});
```

## Dynamic Updates

```javascript
// Update data
chart.setOption({
  series: [{ data: newData }]
});

// Full replacement (useful for complete reconfiguration)
chart.setOption(newOption, true);

// Loading state
chart.showLoading();
chart.hideLoading();
```

## Performance Tips

1. **Large datasets (>10k points)**: Use `large: true` and `largeThreshold: 2000`
2. **Use Canvas renderer** (default) for large datasets, SVG for small interactive charts
3. **Enable sampling**: `sampling: 'average'` or `'max'`
4. **Disable animations** for real-time data: `animation: false`
5. **Use `appendData()`** for incremental updates
