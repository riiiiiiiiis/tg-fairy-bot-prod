# Product Overview

## Telegram Fairy Bot

A Telegram personality quiz bot that helps users discover their archetype through a 19-question interactive quiz.

### Core Features
- Interactive personality quiz with 19 questions
- Multiple choice answers (users select 3 out of 6 options per question)
- Scoring system that calculates personality archetypes
- Results display showing top 3 matching archetypes
- Google Sheets integration for content management
- Multilingual support (primarily Russian)

### User Flow
1. `/start` command initiates welcome sequence
2. Promotional message with call-to-action
3. Instructions and quiz start
4. 19 questions with 3-choice selection per question
5. Final results showing primary, secondary, and tertiary archetypes

### Content Management
- All quiz content (questions, answers, results) stored in Google Sheets
- Dynamic content loading with caching
- Configurable text messages through Google Sheets Config worksheet