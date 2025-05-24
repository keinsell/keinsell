package main

import (
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

func TestModelInitialization(t *testing.T) {
	m := model{}
	
	// Test Init
	cmd := m.Init()
	if cmd == nil {
		t.Error("Init() should return a command")
	}
	
	// Test Update with window size
	msg := tea.WindowSizeMsg{Width: 120, Height: 40}
	newModel, _ := m.Update(msg)
	
	updatedModel := newModel.(model)
	if updatedModel.width != 120 {
		t.Errorf("Expected width 120, got %d", updatedModel.width)
	}
	if updatedModel.height != 40 {
		t.Errorf("Expected height 40, got %d", updatedModel.height)
	}
}

func TestModelUpdate(t *testing.T) {
	m := model{width: 120, height: 40}
	
	// Initialize charts first
	msg := tea.WindowSizeMsg{Width: 120, Height: 40}
	newModel, _ := m.Update(msg)
	m = newModel.(model)
	
	// Test data update
	m.dataTime = 1.0
	m.updateCharts()
	
	// Test that charts are populated (basic smoke test)
	view := m.View()
	if view == "Initializing dashboard..." {
		t.Error("Dashboard should be initialized after setting dimensions")
	}
	
	if len(view) == 0 {
		t.Error("View should return content")
	}
}

func TestQuitCommand(t *testing.T) {
	m := model{}
	
	// Test quit with 'q'
	quitMsg := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'q'}}
	_, cmd := m.Update(quitMsg)
	
	if cmd == nil {
		t.Error("Quit command should be returned")
	}
	
	// Test quit with Ctrl+C
	ctrlCMsg := tea.KeyMsg{Type: tea.KeyCtrlC}
	_, cmd = m.Update(ctrlCMsg)
	
	if cmd == nil {
		t.Error("Quit command should be returned for Ctrl+C")
	}
}