# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`zkk` is a personal knowledge base management tool written in Python. This is a minimal project in early development stages.

## Development Commands

- **Run the tool**: `python main.py`
- **Install dependencies**: `pip install -e .` (when dependencies are added)

## Project Structure

- `main.py` - Main entry point with basic CLI functionality
- `pyproject.toml` - Python project configuration using modern packaging standards
- Currently requires Python >=3.12

## Architecture Notes

This is a minimal single-file Python application. Future development should consider:
- Adding proper CLI argument parsing
- Implementing knowledge base functionality
- Adding dependencies to pyproject.toml as needed