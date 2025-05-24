package main

import (
	"fmt"
	"math"
	"strconv"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/key"
	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Data structures
type Substance struct {
	Name     string
	HalfLife time.Duration
	Color    string
	Symbol   string
}

type Dosage struct {
	Substance Substance
	Amount    float64
	Time      time.Time
}

// List item for substance selection
type substanceItem struct {
	substance Substance
}

func (i substanceItem) FilterValue() string { return i.substance.Name }
func (i substanceItem) Title() string       { return i.substance.Name }
func (i substanceItem) Description() string { return fmt.Sprintf("Half-life: %v", i.substance.HalfLife) }

// Application states
type appState int

const (
	stateChart appState = iota
	stateAddDose
	stateEnterAmount
)

// Model
type model struct {
	state         appState
	substances    []Substance
	dosages       []Dosage
	width         int
	height        int
	
	// Components
	substanceList list.Model
	amountInput   textinput.Model
	help          help.Model
	
	// State
	selectedSubstance *Substance
	keys              keyMap
}

// Key bindings
type keyMap struct {
	Add   key.Binding
	Quit  key.Binding
	Back  key.Binding
	Enter key.Binding
	Help  key.Binding
}

func (k keyMap) ShortHelp() []key.Binding {
	return []key.Binding{k.Add, k.Help, k.Quit}
}

func (k keyMap) FullHelp() [][]key.Binding {
	return [][]key.Binding{
		{k.Add, k.Back},
		{k.Help, k.Quit},
	}
}

var keys = keyMap{
	Add: key.NewBinding(
		key.WithKeys("a"),
		key.WithHelp("a", "add dose"),
	),
	Quit: key.NewBinding(
		key.WithKeys("q", "ctrl+c"),
		key.WithHelp("q", "quit"),
	),
	Back: key.NewBinding(
		key.WithKeys("esc"),
		key.WithHelp("esc", "back"),
	),
	Enter: key.NewBinding(
		key.WithKeys("enter"),
		key.WithHelp("enter", "confirm"),
	),
	Help: key.NewBinding(
		key.WithKeys("?"),
		key.WithHelp("?", "help"),
	),
}

// Styles
var (
	// Base styles
	baseStyle = lipgloss.NewStyle().
		Background(lipgloss.Color("#1a1b26")).
		Foreground(lipgloss.Color("#a9b1d6"))
	
	// Chart styles
	chartTitleStyle = lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7aa2f7")).
		MarginBottom(1)
	
	axisStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#565f89"))
	
	labelStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#565f89")).
		Faint(true)
	
	// Input styles
	inputBoxStyle = lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("#7aa2f7")).
		Padding(1, 2).
		Background(lipgloss.Color("#1a1b26"))
	
	selectedStyle = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#7aa2f7")).
		Bold(true)
)

func initialModel() model {
	// Define substances with colors from Tokyo Night palette
	substances := []Substance{
		{Name: "Caffeine", HalfLife: 5 * time.Hour, Color: "#f7768e", Symbol: "C"},
		{Name: "L-Theanine", HalfLife: 3 * time.Hour, Color: "#9ece6a", Symbol: "T"},
		{Name: "Modafinil", HalfLife: 12 * time.Hour, Color: "#7aa2f7", Symbol: "M"},
		{Name: "Nicotine", HalfLife: 2 * time.Hour, Color: "#e0af68", Symbol: "N"},
	}
	
	// Create substance list
	items := make([]list.Item, len(substances))
	for i, s := range substances {
		items[i] = substanceItem{substance: s}
	}
	
	l := list.New(items, list.NewDefaultDelegate(), 30, 10)
	l.Title = "Select Substance"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.SetShowHelp(false)
	l.Styles.Title = chartTitleStyle
	
	// Create text input
	ti := textinput.New()
	ti.Placeholder = "200"
	ti.CharLimit = 6
	ti.Width = 20
	
	// Create help
	h := help.New()
	
	return model{
		state:         stateChart,
		substances:    substances,
		dosages:       []Dosage{},
		substanceList: l,
		amountInput:   ti,
		help:          h,
		keys:          keys,
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(
		tea.Tick(time.Minute, func(t time.Time) tea.Msg {
			return tickMsg(t)
		}),
		textinput.Blink,
	)
}

type tickMsg time.Time

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd
	
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.help.Width = msg.Width
		
	case tea.KeyMsg:
		switch m.state {
		case stateChart:
			switch {
			case key.Matches(msg, m.keys.Quit):
				return m, tea.Quit
			case key.Matches(msg, m.keys.Add):
				m.state = stateAddDose
				return m, nil
			case key.Matches(msg, m.keys.Help):
				m.help.ShowAll = !m.help.ShowAll
			}
			
		case stateAddDose:
			switch {
			case key.Matches(msg, m.keys.Back):
				m.state = stateChart
				return m, nil
			case key.Matches(msg, m.keys.Enter):
				selected := m.substanceList.SelectedItem()
				if item, ok := selected.(substanceItem); ok {
					m.selectedSubstance = &item.substance
					m.state = stateEnterAmount
					m.amountInput.Reset()
					m.amountInput.Focus()
					return m, textinput.Blink
				}
			}
			
			// Update list
			newList, cmd := m.substanceList.Update(msg)
			m.substanceList = newList
			cmds = append(cmds, cmd)
			
		case stateEnterAmount:
			switch {
			case key.Matches(msg, m.keys.Back):
				m.state = stateAddDose
				m.amountInput.Blur()
				return m, nil
			case key.Matches(msg, m.keys.Enter):
				if amount, err := strconv.ParseFloat(m.amountInput.Value(), 64); err == nil && amount > 0 {
					m.dosages = append(m.dosages, Dosage{
						Substance: *m.selectedSubstance,
						Amount:    amount,
						Time:      time.Now(),
					})
				}
				m.state = stateChart
				m.amountInput.Blur()
				m.selectedSubstance = nil
				return m, nil
			}
			
			// Update text input
			newInput, cmd := m.amountInput.Update(msg)
			m.amountInput = newInput
			cmds = append(cmds, cmd)
		}
		
	case tickMsg:
		// Refresh chart every minute
		return m, tea.Tick(time.Minute, func(t time.Time) tea.Msg {
			return tickMsg(t)
		})
	}
	
	return m, tea.Batch(cmds...)
}

func (m model) View() string {
	if m.width == 0 || m.height == 0 {
		return "Loading..."
	}
	
	switch m.state {
	case stateChart:
		return m.renderChart()
		
	case stateAddDose:
		// Overlay substance selection on chart
		chart := m.renderChart()
		listBox := inputBoxStyle.Render(m.substanceList.View())
		
		overlay := lipgloss.Place(m.width, m.height,
			lipgloss.Center, lipgloss.Center,
			listBox)
		
		return lipgloss.JoinVertical(lipgloss.Left, chart, overlay)
		
	case stateEnterAmount:
		// Overlay amount input on chart
		chart := m.renderChart()
		
		if m.selectedSubstance != nil {
			inputContent := lipgloss.JoinVertical(lipgloss.Left,
				chartTitleStyle.Render("Add Dose"),
				"",
				fmt.Sprintf("Substance: %s", m.selectedSubstance.Name),
				"",
				"Amount (mg):",
				m.amountInput.View(),
				"",
				labelStyle.Render("Press Enter to confirm, Esc to go back"),
			)
			
			inputBox := inputBoxStyle.Width(40).Render(inputContent)
			overlay := lipgloss.Place(m.width, m.height,
				lipgloss.Center, lipgloss.Center,
				inputBox)
			
			return lipgloss.JoinVertical(lipgloss.Left, chart, overlay)
		}
	}
	
	return "Error"
}

func (m model) renderChart() string {
	// Use full terminal space
	padding := 4
	chartWidth := m.width - padding
	chartHeight := m.height - 6 // Leave room for help
	
	if chartWidth < 40 || chartHeight < 10 {
		return baseStyle.Width(m.width).Height(m.height).Render("Terminal too small")
	}
	
	// Create chart buffer
	chart := make([][]rune, chartHeight)
	for i := range chart {
		chart[i] = make([]rune, chartWidth)
		for j := range chart[i] {
			chart[i][j] = ' '
		}
	}
	
	// Draw grid lines
	gridStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("#3b4261"))
	
	// Horizontal grid lines
	for y := 0; y < chartHeight-3; y += 5 {
		for x := 1; x < chartWidth-1; x++ {
			chart[y][x] = '·'
		}
	}
	
	// Draw axes
	for x := 0; x < chartWidth; x++ {
		chart[chartHeight-3][x] = '─'
	}
	for y := 0; y < chartHeight-3; y++ {
		chart[y][0] = '│'
	}
	chart[chartHeight-3][0] = '└'
	
	// Time calculations
	now := time.Now()
	timeWindow := 24 * time.Hour
	
	// Plot substances
	for _, substance := range m.substances {
		// Create smooth curve using more points
		prevY := -1
		for x := 1; x < chartWidth-1; x++ {
			progress := float64(x-1) / float64(chartWidth-2)
			timePoint := now.Add(-timeWindow + timeWindow*time.Duration(progress))
			intensity := m.calculateIntensity(substance, timePoint)
			
			if intensity > 0.01 {
				y := chartHeight - 4 - int(intensity*float64(chartHeight-4))
				if y >= 0 && y < chartHeight-3 {
					// Draw vertical lines to connect points
					if prevY != -1 && prevY != y {
						step := 1
						if prevY > y {
							step = -1
						}
						for cy := prevY; cy != y; cy += step {
							if cy >= 0 && cy < chartHeight-3 {
								chart[cy][x-1] = '│'
							}
						}
					}
					chart[y][x] = '●'
					prevY = y
				}
			} else {
				prevY = -1
			}
		}
	}
	
	// Render chart with colors
	var b strings.Builder
	
	// Title
	title := chartTitleStyle.Render("NEURONEK // Substance Intensity Monitor")
	b.WriteString(lipgloss.PlaceHorizontal(m.width, lipgloss.Center, title))
	b.WriteString("\n\n")
	
	// Y-axis labels
	b.WriteString(labelStyle.Render("100% "))
	
	// Render chart content
	for y := 0; y < chartHeight-3; y++ {
		if y > 0 {
			if y == (chartHeight-3)/2 {
				b.WriteString(labelStyle.Render(" 50% "))
			} else {
				b.WriteString("     ")
			}
		}
		
		for x := 0; x < chartWidth; x++ {
			char := chart[y][x]
			
			// Color based on content
			switch char {
			case '●':
				// Find which substance this belongs to
				colored := false
				for _, sub := range m.substances {
					if m.hasSubstanceAtPoint(sub, x, y, chartWidth, chartHeight) {
						style := lipgloss.NewStyle().Foreground(lipgloss.Color(sub.Color)).Bold(true)
						b.WriteString(style.Render("●"))
						colored = true
						break
					}
				}
				if !colored {
					b.WriteString(string(char))
				}
			case '│', '─', '└':
				b.WriteString(axisStyle.Render(string(char)))
			case '·':
				b.WriteString(gridStyle.Render(string(char)))
			default:
				b.WriteString(string(char))
			}
		}
		b.WriteString("\n")
	}
	
	// X-axis labels
	b.WriteString(labelStyle.Render("  0% "))
	for i := 0; i < chartWidth; i++ {
		b.WriteString(axisStyle.Render("─"))
	}
	b.WriteString("\n")
	
	// Time labels
	b.WriteString("     ")
	b.WriteString(labelStyle.Render("24h"))
	spaces := chartWidth - 10
	b.WriteString(strings.Repeat(" ", spaces/2))
	b.WriteString(labelStyle.Render("12h"))
	b.WriteString(strings.Repeat(" ", spaces/2))
	b.WriteString(labelStyle.Render("now"))
	b.WriteString("\n\n")
	
	// Legend with recent doses
	legend := m.renderLegend()
	b.WriteString(legend)
	
	// Help at bottom
	if m.state == stateChart {
		b.WriteString("\n")
		helpView := m.help.View(m.keys)
		b.WriteString(helpView)
	}
	
	return baseStyle.Width(m.width).Height(m.height).Render(b.String())
}

func (m model) hasSubstanceAtPoint(substance Substance, x, y, width, height int) bool {
	progress := float64(x-1) / float64(width-2)
	timePoint := time.Now().Add(-24*time.Hour + 24*time.Hour*time.Duration(progress))
	intensity := m.calculateIntensity(substance, timePoint)
	
	if intensity > 0.01 {
		expectedY := height - 4 - int(intensity*float64(height-4))
		return y == expectedY
	}
	return false
}

func (m model) renderLegend() string {
	var b strings.Builder
	
	// Substance legend
	for i, s := range m.substances {
		style := lipgloss.NewStyle().Foreground(lipgloss.Color(s.Color)).Bold(true)
		b.WriteString(style.Render(fmt.Sprintf("● %s", s.Name)))
		if i < len(m.substances)-1 {
			b.WriteString("  ")
		}
	}
	
	// Recent doses on the right
	if len(m.dosages) > 0 {
		b.WriteString("    ")
		b.WriteString(labelStyle.Render("Recent: "))
		
		shown := 0
		for i := len(m.dosages) - 1; i >= 0 && shown < 3; i-- {
			d := m.dosages[i]
			elapsed := time.Since(d.Time)
			
			doseStyle := lipgloss.NewStyle().Foreground(lipgloss.Color(d.Substance.Color))
			doseInfo := fmt.Sprintf("%s %.0fmg (%s)",
				d.Substance.Symbol,
				d.Amount,
				formatDuration(elapsed))
			
			b.WriteString(doseStyle.Render(doseInfo))
			if shown < 2 && i > 0 {
				b.WriteString(" · ")
			}
			shown++
		}
	}
	
	return b.String()
}

func (m model) calculateIntensity(substance Substance, t time.Time) float64 {
	totalIntensity := 0.0
	
	for _, dosage := range m.dosages {
		if dosage.Substance.Name == substance.Name && dosage.Time.Before(t) {
			elapsed := t.Sub(dosage.Time)
			halfLives := elapsed.Seconds() / substance.HalfLife.Seconds()
			remaining := dosage.Amount * math.Pow(0.5, halfLives)
			
			// Normalize based on typical doses
			normalizedDose := remaining / 200.0
			if normalizedDose > 0.01 {
				totalIntensity += normalizedDose
			}
		}
	}
	
	if totalIntensity > 1.0 {
		totalIntensity = 1.0
	}
	
	return totalIntensity
}

func formatDuration(d time.Duration) string {
	if d < time.Minute {
		return "now"
	} else if d < time.Hour {
		return fmt.Sprintf("%dm", int(d.Minutes()))
	} else if d < 24*time.Hour {
		return fmt.Sprintf("%dh", int(d.Hours()))
	}
	return fmt.Sprintf("%dd", int(d.Hours())/24)
}

func main() {
	p := tea.NewProgram(
		initialModel(),
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}