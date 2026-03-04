# Vega-Lite Reference

Vega-Lite is a high-level grammar of interactive graphics using declarative JSON specifications.

## CDN Links

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
```

## Basic Structure

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Chart Title",
  "data": { "values": [...] },
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Embedding

```javascript
vegaEmbed('#vis', spec).then(result => {
  // Access the Vega view instance
  const view = result.view;
}).catch(console.error);

// With options
vegaEmbed('#vis', spec, {
  theme: 'dark',
  actions: { source: false, editor: true }
});
```

## Data Types

| Type | Description | Examples |
|------|-------------|----------|
| `quantitative` | Continuous numbers | temperature, price |
| `nominal` | Unordered categories | country, product type |
| `ordinal` | Ordered categories | size (S,M,L), rating |
| `temporal` | Date/time | date, timestamp |

## Mark Types

### Basic Marks
- `bar` - Bar charts (horizontal/vertical)
- `line` - Line charts
- `point` - Scatter plots
- `area` - Area charts
- `rect` - Heatmaps, 2D histograms
- `circle` - Circle marks (like point)
- `square` - Square marks
- `tick` - Tick marks (strip plots)
- `rule` - Reference lines
- `text` - Text labels
- `arc` - Pie/donut charts

### Mark Properties
```json
{
  "mark": {
    "type": "bar",
    "color": "#4c78a8",
    "opacity": 0.8,
    "cornerRadius": 5
  }
}
```

## Encoding Channels

### Position Channels
```json
{
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "value", "type": "quantitative"},
    "x2": {"field": "end_date"},
    "y2": {"field": "high_value"}
  }
}
```

### Color & Style
```json
{
  "encoding": {
    "color": {"field": "category", "type": "nominal"},
    "opacity": {"field": "confidence", "type": "quantitative"},
    "size": {"field": "population", "type": "quantitative"},
    "shape": {"field": "symbol", "type": "nominal"},
    "strokeWidth": {"value": 2}
  }
}
```

### Text & Tooltips
```json
{
  "encoding": {
    "text": {"field": "label"},
    "tooltip": [
      {"field": "name", "type": "nominal"},
      {"field": "value", "type": "quantitative", "format": ".2f"}
    ]
  }
}
```

## Chart Examples

### Bar Chart
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [
    {"category": "A", "value": 28},
    {"category": "B", "value": 55},
    {"category": "C", "value": 43}
  ]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

### Line Chart
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [
    {"date": "2024-01", "value": 28},
    {"date": "2024-02", "value": 55},
    {"date": "2024-03", "value": 43}
  ]},
  "mark": {"type": "line", "point": true},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

### Scatter Plot
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"},
    "size": {"field": "Weight_in_lbs", "type": "quantitative"}
  }
}
```

### Area Chart
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [...]},
  "mark": {"type": "area", "opacity": 0.7},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

### Pie/Donut Chart
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [
    {"category": "A", "value": 4},
    {"category": "B", "value": 6},
    {"category": "C", "value": 10}
  ]},
  "mark": {"type": "arc", "innerRadius": 50},
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Heatmap
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"values": [
    {"x": "A", "y": "1", "value": 28},
    {"x": "B", "y": "1", "value": 55}
  ]},
  "mark": "rect",
  "encoding": {
    "x": {"field": "x", "type": "nominal"},
    "y": {"field": "y", "type": "nominal"},
    "color": {"field": "value", "type": "quantitative"}
  }
}
```

### Histogram
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "data/movies.json"},
  "mark": "bar",
  "encoding": {
    "x": {"bin": true, "field": "IMDB_Rating"},
    "y": {"aggregate": "count"}
  }
}
```

## Transforms

### Aggregation
```json
{
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"aggregate": "mean", "field": "value", "type": "quantitative"}
  }
}
```

### Binning
```json
{
  "encoding": {
    "x": {"bin": {"maxbins": 20}, "field": "value", "type": "quantitative"},
    "y": {"aggregate": "count"}
  }
}
```

### Filtering
```json
{
  "transform": [
    {"filter": "datum.value > 50"},
    {"filter": {"field": "category", "oneOf": ["A", "B"]}}
  ]
}
```

### Calculate (Computed Fields)
```json
{
  "transform": [
    {"calculate": "datum.price * datum.quantity", "as": "total"},
    {"calculate": "year(datum.date)", "as": "year"}
  ]
}
```

### Fold (Reshape)
```json
{
  "transform": [
    {"fold": ["gold", "silver", "bronze"], "as": ["medal", "count"]}
  ]
}
```

## Multi-View Compositions

### Layering
```json
{
  "layer": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "line", "encoding": {...}}
  ]
}
```

### Concatenation (Side by Side)
```json
{
  "hconcat": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "line", "encoding": {...}}
  ]
}
```

### Vertical Concat
```json
{
  "vconcat": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "line", "encoding": {...}}
  ]
}
```

### Faceting (Small Multiples)
```json
{
  "facet": {"column": {"field": "category", "type": "nominal"}},
  "spec": {
    "mark": "bar",
    "encoding": {...}
  }
}
```

### Repeat
```json
{
  "repeat": {"column": ["temp_max", "precipitation", "wind"]},
  "spec": {
    "mark": "line",
    "encoding": {
      "x": {"field": "date", "type": "temporal"},
      "y": {"field": {"repeat": "column"}, "type": "quantitative"}
    }
  }
}
```

## Interactivity

### Selection Parameters
```json
{
  "params": [
    {"name": "highlight", "select": {"type": "point", "on": "mouseover"}}
  ],
  "mark": {"type": "bar", "cursor": "pointer"},
  "encoding": {
    "opacity": {
      "condition": {"param": "highlight", "value": 1},
      "value": 0.5
    }
  }
}
```

### Interval Selection (Brushing)
```json
{
  "params": [
    {"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}
  ],
  "mark": "point",
  "encoding": {
    "color": {
      "condition": {"param": "brush", "field": "Origin", "type": "nominal"},
      "value": "grey"
    }
  }
}
```

### Legend Selection
```json
{
  "params": [
    {"name": "legend", "select": {"type": "point", "fields": ["Origin"]}, "bind": "legend"}
  ],
  "encoding": {
    "opacity": {
      "condition": {"param": "legend", "value": 1},
      "value": 0.2
    }
  }
}
```

## Configuration

```json
{
  "config": {
    "view": {"stroke": "transparent"},
    "axis": {"labelFontSize": 12, "titleFontSize": 14},
    "legend": {"labelFontSize": 12},
    "title": {"fontSize": 16},
    "bar": {"color": "#4c78a8"},
    "line": {"strokeWidth": 2}
  }
}
```

## Themes

```javascript
vegaEmbed('#vis', spec, {
  theme: 'dark'  // or 'excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight'
});
```

## External Data

```json
{
  "data": {"url": "https://example.com/data.json"},
  "data": {"url": "data.csv", "format": {"type": "csv"}},
  "data": {"url": "data.tsv", "format": {"type": "tsv"}}
}
```

## Online Resources

- **Editor**: https://vega.github.io/editor/
- **Examples**: https://vega.github.io/vega-lite/examples/
- **Documentation**: https://vega.github.io/vega-lite/docs/
