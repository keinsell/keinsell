# Neuronek Dashboard - Substance Tracker

A professional terminal-based substance dosage tracker built with Bubble Tea and the Bubbles component library. Track caffeine, supplements, and other substances with real-time intensity visualization.

## Features

- **Built with Bubbles Components**: Uses production-ready components from the Bubbles library
  - List component for substance selection
  - Table component for dosage history
  - Viewport for scrollable chart
  - TextInput for amount entry
  - Help system with key bindings
- **Split-Screen Layout**: 3/4 screen for intensity chart, 1/4 for dosage table
- **Real-time Visualization**: 24-hour substance intensity chart with automatic updates
- **Half-life Calculations**: Accurate pharmacokinetic modeling
- **Clean Architecture**: State-based UI with proper component separation

## Components Used

- **List**: Interactive substance selection with descriptions
- **Table**: Formatted dosage history with columns for substance, amount, time, and elapsed duration
- **Viewport**: Scrollable chart area with proper rendering
- **TextInput**: Validated numeric input for dosage amounts
- **Help**: Context-aware keyboard shortcuts
- **Lipgloss**: Professional styling with consistent theme

## Installation

1. Install Go (1.21 or later)
2. Clone this repository
3. Install dependencies:
   ```bash
   go mod download
   ```

## Usage

Run the application:
```bash
go run main.go
```

### Controls

- **a** - Add new dose (opens substance selector)
- **↑/k, ↓/j** - Navigate lists and tables
- **Enter** - Select/confirm
- **Esc** - Go back/cancel
- **?** - Toggle help
- **q** - Quit

### Workflow

1. Press 'a' to add a dose
2. Select substance from the list using arrow keys
3. Press Enter to proceed
4. Enter dosage amount in milligrams
5. Press Enter to confirm

## Architecture

The application follows Bubble Tea's Model-Update-View pattern with proper state management:

- **States**: Main dashboard, substance selection, amount input
- **Components**: All UI elements use Bubbles library components
- **Styling**: Consistent Lipgloss styling throughout

## Substances

Pre-configured with:
- **Caffeine** (5-hour half-life) - Red
- **L-Theanine** (3-hour half-life) - Teal
- **Modafinil** (12-hour half-life) - Blue
- **Nicotine** (2-hour half-life) - Yellow

## Customization

Modify substances in `main.go`:
```go
substances := []Substance{
    {Name: "Caffeine", HalfLife: 5 * time.Hour, Color: "#FF6B6B"},
    // Add more substances here
}
```