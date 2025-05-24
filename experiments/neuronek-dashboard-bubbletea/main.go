package main

import (
	"log"
	"math"
	"time"

	"github.com/NimbleMarkets/ntcharts/linechart"
	"github.com/NimbleMarkets/ntcharts/canvas"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FAFAFA")).
			Background(lipgloss.Color("#7D56F4")).
			Padding(0, 1)

	borderStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("#874BFD")).
			Padding(1)

	chartStyle = lipgloss.NewStyle().
			Border(lipgloss.NormalBorder()).
			BorderForeground(lipgloss.Color("#04B575")).
			Padding(1)
)

type tickMsg time.Time

type model struct {
	chart1   linechart.Model
	chart2   linechart.Model
	chart3   linechart.Model
	dataTime float64
	width    int
	height   int
}

func (m model) Init() tea.Cmd {
	return tickCmd()
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		
		chartWidth := (msg.Width - 6) / 3
		chartHeight := (msg.Height - 8) / 2
		
		m.chart1 = linechart.New(chartWidth, chartHeight, 0.0, 10.0, -1.5, 1.5)
		m.chart2 = linechart.New(chartWidth, chartHeight, 0.0, 10.0, -1.0, 1.0)
		m.chart3 = linechart.New(chartWidth, chartHeight, 0.0, 10.0, -0.5, 1.0)
		
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		}

	case tickMsg:
		m.dataTime += 0.1
		m.updateCharts()
		return m, tickCmd()
	}

	return m, nil
}

func (m *model) updateCharts() {
	if m.width == 0 {
		return
	}

	// Clear previous data
	m.chart1.Clear()
	m.chart2.Clear()
	m.chart3.Clear()

	// Generate data for multiple lines
	var points1, points2, points3 []canvas.Float64Point
	
	for i := 0; i < 50; i++ {
		x := float64(i) * 0.2
		
		// Chart 1: Sine waves
		y1 := math.Sin(x + m.dataTime)
		y2 := math.Sin(x + m.dataTime + math.Pi/2)
		y3 := math.Sin(x + m.dataTime + math.Pi)
		
		points1 = append(points1, canvas.Float64Point{X: x, Y: y1})
		points1 = append(points1, canvas.Float64Point{X: x, Y: y2})
		points1 = append(points1, canvas.Float64Point{X: x, Y: y3})

		// Chart 2: Exponential decay
		decay1 := math.Exp(-x/5) * math.Sin(x + m.dataTime)
		decay2 := math.Exp(-x/3) * math.Cos(x + m.dataTime)
		
		points2 = append(points2, canvas.Float64Point{X: x, Y: decay1})
		points2 = append(points2, canvas.Float64Point{X: x, Y: decay2})

		// Chart 3: Linear trends with noise
		trend1 := x*0.1 + 0.2*math.Sin(x*2+m.dataTime)
		trend2 := -x*0.05 + 0.3*math.Cos(x*1.5+m.dataTime)
		trend3 := x*0.08 + 0.1*math.Sin(x*3+m.dataTime)
		
		points3 = append(points3, canvas.Float64Point{X: x, Y: trend1})
		points3 = append(points3, canvas.Float64Point{X: x, Y: trend2})
		points3 = append(points3, canvas.Float64Point{X: x, Y: trend3})
	}
	
	// Draw lines connecting points
	for i := 0; i < len(points1)-1; i++ {
		m.chart1.DrawBrailleLine(points1[i], points1[i+1])
	}
	
	for i := 0; i < len(points2)-1; i++ {
		m.chart2.DrawBrailleLine(points2[i], points2[i+1])
	}
	
	for i := 0; i < len(points3)-1; i++ {
		m.chart3.DrawBrailleLine(points3[i], points3[i+1])
	}
}

func (m model) View() string {
	if m.width == 0 {
		return "Initializing dashboard..."
	}

	title := titleStyle.Render("Neuronek Dashboard - Real-time Analytics")
	
	// First row of charts
	chart1View := chartStyle.Render(
		lipgloss.JoinVertical(lipgloss.Left,
			lipgloss.NewStyle().Bold(true).Render("Sine Wave Patterns"),
			m.chart1.View(),
		),
	)
	
	chart2View := chartStyle.Render(
		lipgloss.JoinVertical(lipgloss.Left,
			lipgloss.NewStyle().Bold(true).Render("Exponential Decay"),
			m.chart2.View(),
		),
	)
	
	chart3View := chartStyle.Render(
		lipgloss.JoinVertical(lipgloss.Left,
			lipgloss.NewStyle().Bold(true).Render("Linear Trends"),
			m.chart3.View(),
		),
	)
	
	// Arrange charts in a row
	chartsRow := lipgloss.JoinHorizontal(lipgloss.Top, chart1View, chart2View, chart3View)
	
	// Status bar
	statusBar := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Render("Press 'q' or 'ctrl+c' to quit • Real-time data simulation")
	
	// Main layout
	content := lipgloss.JoinVertical(lipgloss.Left,
		title,
		"",
		chartsRow,
		"",
		statusBar,
	)
	
	return borderStyle.Render(content)
}

func tickCmd() tea.Cmd {
	return tea.Tick(time.Millisecond*100, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func main() {
	p := tea.NewProgram(
		model{},
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)

	if _, err := p.Run(); err != nil {
		log.Fatal(err)
	}
}