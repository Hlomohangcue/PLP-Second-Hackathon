# AI Study Buddy - Flashcard Generator

## 🎯 Project Overview

AI Study Buddy is a web application that transforms study notes into interactive flashcards using AI-powered question generation. Built for students who want to quickly create engaging study materials from their existing notes.

## 🌟 Real-World Impact

- **Educational Accessibility**: Makes quality study tools available to all students
- **Time Efficiency**: Converts hours of manual flashcard creation into minutes
- **Learning Enhancement**: AI-generated questions improve comprehension and retention
- **Cost-Effective**: Free alternative to premium flashcard services

## 🚀 Tech Stack

### Frontend
- **HTML5**: Semantic structure for flashcards
- **CSS3**: Animations and responsive design
- **JavaScript**: Interactive card flipping and state management

### Backend
- **Python Flask**: RESTful API server
- **MySQL**: Persistent storage for flashcards and user data

### AI Integration
- **Hugging Face API**: Question-answering model for content generation

## ✨ Key Features

- Paste study notes and generate 5 quiz questions instantly
- Interactive flip-card interface
- Save flashcards for future study sessions
- Simple, beginner-friendly architecture
- Real-time AI processing

## 🎯 Hackathon Goals (5 Days)

This project is designed for a **Minimum Viable Product (MVP)** approach:

- **Day 1-2**: Setup environment, basic UI, database design
- **Day 3**: AI integration and question generation
- **Day 4**: Frontend interactivity and flashcard system
- **Day 5**: Testing, deployment, and documentation

## 🏗️ Project Structure

```
ai-study-buddy/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── routes.py           # API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main application page
│   ├── css/
│   │   └── styles.css      # Styling and animations
│   └── js/
│       └── main.js         # Frontend logic
├── docs/                   # Documentation files
└── README.md
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-study-buddy
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Setup Database**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

4. **Configure Environment**
   - Set up Hugging Face API key
   - Configure MySQL connection
   - Update environment variables

5. **Launch Frontend**
   - Open `frontend/index.html` in browser
   - Or serve via local server for development

## 🎯 Target Users

- **Primary**: Students (high school, college)
- **Secondary**: Educators creating study materials
- **Tertiary**: Self-learners and professionals

## 💡 Why This Project?

### Perfect for Hackathon Beginners:
- **Simple UI**: No complex frameworks required
- **Clear Learning Path**: Covers frontend, backend, database, and AI
- **Immediate Value**: Solves real student problems
- **Scalable**: Can be enhanced post-hackathon

### Business Potential:
- Freemium model with advanced features
- Educational institution licensing
- API service for other educational apps
- Premium AI models and analytics

## 🔗 Related Documentation

- [Requirements](docs/requirements.md) - Detailed project requirements
- [Developer Tasks](docs/developer_tasks.md) - Task breakdown and timeline
- [System Design](docs/system_design.md) - Architecture and data flow
- [User Management](docs/user_management.md) - User stories and workflows

## 🤝 Contributing

This is a hackathon project designed for rapid development. Focus on MVP features first, then iterate based on user feedback.

## 📝 License

Open source - feel free to use, modify, and distribute.

---

**Built with ❤️ for students, by developers who care about education.**