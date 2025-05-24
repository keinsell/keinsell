# Neuronek Dashboard - Bubble Tea TUI

A terminal-based dashboard built with the Bubble Tea ecosystem for displaying real-time line charts.

## Features

- **Real-time animated line charts** with multiple data series
- **Responsive terminal UI** that adapts to window resizing
- **Three dashboard panels** showing different data patterns:
  - Sine wave patterns (3 overlapping waves)
  - Exponential decay functions
  - Linear trends with noise
- **Smooth animations** with 100ms update intervals
- **Clean, styled interface** using Lip Gloss for styling

## Technologies

- **[Bubble Tea](https://github.com/charmbracelet/bubbletea)** - TUI framework using The Elm Architecture
- **[Lip Gloss](https://github.com/charmbracelet/lipgloss)** - CSS-like styling for terminal layouts
- **[ntcharts](https://github.com/NimbleMarkets/ntcharts)** - Terminal charts with Braille line drawing
- **Go 1.24+** - Modern Go with latest features

## Usage

```bash
# Build the application
go build -o neuronek-dashboard .

# Run the dashboard
./neuronek-dashboard
```

### Controls

- `q` or `Ctrl+C` - Quit the application
- Terminal window resizing is automatically handled

## Architecture

The application follows the Bubble Tea Model-Update-View pattern:

- **Model**: Holds chart states, dimensions, and animation data
- **Update**: Handles user input, window resizing, and animation ticks
- **View**: Renders the styled dashboard layout with live charts

## Development

```bash
# Run tests
go test -v

# Check dependencies
go mod tidy
```

## Chart Data

The dashboard displays three types of mathematical functions:

1. **Sine Waves**: `sin(x + t)`, `sin(x + t + π/2)`, `sin(x + t + π)`
2. **Exponential Decay**: `e^(-x/5) * sin(x + t)`, `e^(-x/3) * cos(x + t)`
3. **Linear Trends**: Various linear functions with sinusoidal noise

All data updates in real-time with smooth animations.