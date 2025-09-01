# System Design - AI Study Buddy

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  External APIs  │
│                 │    │                 │    │                 │
│  HTML/CSS/JS    │◄──►│  Flask Server   │◄──►│  Hugging Face   │
│                 │    │                 │    │     API         │
│  - User Input   │    │  - API Routes   │    │                 │
│  - Flashcards   │    │  - AI Service   │    │                 │
│  - Animations   │    │  - Database     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                                ▼