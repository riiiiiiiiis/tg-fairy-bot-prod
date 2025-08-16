# Product Overview

## Telegram Fairy Bot

A Telegram personality quiz bot that helps users discover their archetype through a comprehensive 19-question interactive quiz with gender-specific content and personalized results.

### Core Features
- **Interactive personality quiz** with 19 carefully crafted questions
- **Gender-based personalization** - separate content for male and female users
- **Multiple choice answers** - users select 3 out of 6 options per question
- **Advanced scoring system** that calculates personality archetypes
- **Detailed results** showing top 3 matching archetypes with descriptions
- **Google Sheets integration** for dynamic content management
- **Media delivery** - PDF reports and video content
- **Payment integration** for premium content
- **Multilingual support** (primarily Russian)
- **Caching system** for optimal performance

### User Journey
1. **Welcome** - `/start` command initiates welcome sequence
2. **Gender Selection** - User chooses male or female for personalized content
3. **Promotional Message** - Engaging call-to-action with quiz preview
4. **Instructions** - Clear guidance on how to complete the quiz
5. **Quiz Flow** - 19 questions with 3-choice selection per question
6. **Results Calculation** - Advanced scoring algorithm determines archetypes
7. **Results Display** - Top 3 matching archetypes with detailed descriptions
8. **Media Delivery** - PDF reports and video content (if configured)
9. **Premium Upsell** - Payment option for extended analysis

### Content Management System
- **Google Sheets backend** - All content stored in structured worksheets
- **Dynamic loading** - Content fetched and cached from sheets
- **A/B testing support** - Easy content modification without code changes
- **Multi-table architecture** - Separate sheets for male/female content
- **Configurable messaging** - All user-facing text managed through Config worksheet

### Worksheets Structure
- **Config** - Bot messages, URLs, and configuration
- **Questions** - Quiz questions with metadata
- **Answers** - Answer options with scoring weights
- **Archetypes** - Personality type descriptions and characteristics

### Technical Features
- **Async architecture** - High-performance async/await implementation
- **State management** - Robust FSM for user session handling
- **Error resilience** - Comprehensive error handling and fallbacks
- **Logging system** - Detailed logging for monitoring and debugging
- **Caching layer** - TTL-based caching for Google Sheets API calls
- **Environment configuration** - Secure credential management

### Business Features
- **Analytics ready** - Comprehensive logging for user behavior analysis
- **Scalable architecture** - Designed to handle high user volumes
- **Content flexibility** - Easy content updates without code deployment
- **Monetization support** - Built-in payment integration
- **Multi-audience support** - Gender-specific content delivery

### User Experience Principles
- **Intuitive interface** - Clear buttons and navigation
- **Engaging content** - Emoji-rich messages and interactive elements
- **Fast responses** - Optimized for quick user interactions
- **Error recovery** - Graceful handling of user mistakes
- **Accessibility** - Clear instructions and user-friendly design