# Slack Translation Bot

## Overview

Slack Translation Bot is an automated translation service that provides real-time message translation in Slack channels. The bot automatically detects the language of incoming messages and translates them according to the following rules:

- Korean messages → English and Thai translations
- English messages → Korean and Thai translations
- Thai messages → Korean and English translations

### Key Features

- **Real-time Translation**: Automatically translates messages as they appear in channels
- **Smart Detection**: Automatically detects the source language of messages
- **Thread Support**: Maintains conversation context by posting translations in message threads
- **Efficient Processing**: Prevents duplicate translations and ignores bot messages
- **URL and Command Handling**: Intelligently skips URLs and Slack commands

### Technical Stack

- Python 3.13.2
- Slack Bolt Framework for event handling
- Async architecture for efficient processing
- Type-safe implementation with comprehensive type hints
- Quality assurance through Black, Flake8, and MyPy

### Architecture

The bot is designed with a clean, modular architecture:

- **Slack Client**: Handles Slack event processing and message routing
- **Translation Core**: Manages language detection and translation logic
- **API Client**: Handles communication with the translation service
- **Configuration Management**: Provides type-safe configuration handling

This modular design ensures maintainability, testability, and ease of future enhancements.

## Development Guide

### Code Quality Tools

This project uses several tools to maintain code quality:

- `black`: Code formatter
- `flake8`: Style guide enforcement
- `mypy`: Static type checker

### Running Quality Checks

You can run the quality checks using Make commands.

Using Invoke:
```bash
# Run all checks
make check

# Run individual checks
make format  # Run black formatter
make lint    # Run flake8 linter
make type-check  # Run mypy type checker
```
