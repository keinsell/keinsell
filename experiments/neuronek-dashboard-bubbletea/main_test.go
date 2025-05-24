package main

import (
	"testing"
	"time"
)

func TestSubstanceIntensityCalculation(t *testing.T) {
	m := initialModel()
	
	// Add a test dosage
	testSubstance := m.substances[0] // Caffeine
	m.dosages = append(m.dosages, Dosage{
		Substance: testSubstance,
		Amount:    200, // 200mg
		Time:      time.Now().Add(-2 * time.Hour), // 2 hours ago
	})
	
	// Calculate intensity now
	intensity := m.calculateIntensity(testSubstance, time.Now())
	
	// After 2 hours with 5-hour half-life, should have ~75% remaining
	// 200mg * 0.5^(2/5) ≈ 200mg * 0.758 ≈ 151.6mg
	// Normalized to 0-1 scale: 151.6/100 = 1.516, capped at 1.0
	expectedIntensity := 1.0
	
	if intensity != expectedIntensity {
		t.Errorf("Expected intensity %f, got %f", expectedIntensity, intensity)
	}
}

func TestFormatDuration(t *testing.T) {
	tests := []struct {
		duration time.Duration
		expected string
	}{
		{30 * time.Second, "30s"},
		{5 * time.Minute, "5m"},
		{2*time.Hour + 30*time.Minute, "2h 30m"},
		{25 * time.Hour, "1d 1h"},
	}
	
	for _, test := range tests {
		result := formatDuration(test.duration)
		if result != test.expected {
			t.Errorf("formatDuration(%v) = %s, expected %s", test.duration, result, test.expected)
		}
	}
}

func TestParseAmount(t *testing.T) {
	tests := []struct {
		input    string
		expected float64
	}{
		{"100", 100.0},
		{"50.5", 50.5},
		{"", 0.0},
		{"abc", 0.0},
	}
	
	for _, test := range tests {
		result := parseAmount(test.input)
		if result != test.expected {
			t.Errorf("parseAmount(%s) = %f, expected %f", test.input, result, test.expected)
		}
	}
}