# Intelliplan - Your Smart Study Companion 

A comprehensive Flask-based web application that helps students organize their study plans using advanced algorithms and data structures. Intelliplan combines modern web technologies with computer science algorithms to optimize study schedules and enhance learning efficiency.

## 🚀 Features

### Core Study Management
- **Study Plans**: Create and manage personalized study plans for different subjects
- **Topic Organization**: Add topics with dependencies, difficulty levels, and time estimates
- **Progress Tracking**: Monitor completion status and study progress across subjects
- **Smart Algorithms**: Three optimization algorithms for different study scenarios

### Algorithm-Powered Optimization
1. **Topological Sort**: Orders topics based on prerequisites and dependencies
2. **Study Break Optimization (TSP)**: Minimizes break time between topic transitions using Traveling Salesman Problem algorithms
3. **Revision Priority (Knapsack)**: Optimizes topic selection for revision based on available time and importance

### Productivity Tools
- **Pomodoro Timer**: Built-in timer with session tracking and statistics
- **Note Taking**: Create, edit, and manage study notes with timestamps
- **Mind Maps**: Visual representation of subjects and topics
- **Progress Analytics**: Detailed statistics on study sessions and topic completion

### Collaborative Features
- **Study Groups**: Create and join study groups with unique codes
- **Real-time Chat**: WebSocket-powered group messaging
- **Cross-device Support**: Ngrok integration for multi-device access

### User Management
- **Authentication**: Secure user registration and login with Flask-Login
- **Password Recovery**: Email-based password reset functionality
- **Session Persistence**: Remember login sessions for up to 7 days
- **User Settings**: Customizable preferences and profile management

## 🛠️ Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database for data persistence
- **Flask-Login**: User session management
- **Flask-SocketIO**: Real-time communication
- **Flask-Mail**: Email functionality
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Interactive user interface
- **WebSocket**: Real-time features

### Algorithms & Data Structures
- **Graph Algorithms**: Topological sorting for dependency resolution
- **Optimization**: TSP and Knapsack algorithms for study optimization
- **Data Structures**: Graphs, queues, and hash maps for efficient processing

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser
- ngrok (optional, for cross-device access)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelliplan.git
   cd intelliplan
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from intelliplan import db; db.create_all()"
   ```

5. **Run the application**
   ```bash
   python intelliplan.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🚀 Usage

### Getting Started
1. **Register** a new account or **login** with existing credentials
2. **Create subjects** in the Settings page
3. **Add topics** with dependencies, difficulty, and time estimates
4. **Create study plans** by selecting subjects
5. **Run algorithms** to optimize your study schedule

### Algorithm Usage

#### Topological Sort
- **Purpose**: Orders topics based on prerequisites
- **Use Case**: Determine the correct learning sequence
- **Input**: All topics with their dependencies
- **Output**: Ordered list respecting all prerequisites

#### Study Break Optimization (TSP)
- **Purpose**: Minimizes transition time between topics
- **Use Case**: Optimize study session order to reduce break time
- **Input**: Uncompleted topics with break time data
- **Output**: Optimal topic sequence with minimal total break time

#### Revision Priority (Knapsack)
- **Purpose**: Maximizes learning value within time constraints
- **Use Case**: Select topics for revision before exams
- **Input**: Completed topics with time and importance ratings
- **Output**: Prioritized revision list optimized for available time

### Productivity Features
- Use the **Pomodoro Timer** for focused study sessions
- Take **Notes** during study sessions
- Track **Progress** across all subjects
- Join **Study Groups** for collaborative learning

## 📁 Project Structure

```
intelliplan/
├── intelliplan.py          # Main Flask application
├── instance/
│   └── intelliplan.db     # SQLite database
├── static/
│   ├── css/
│   │   ├── style.css      # Main stylesheet
│   │   └── mindmap.css    # Mind map styles
│   └── js/
│       ├── main.js        # Core JavaScript
│       └── mindmap.js     # Mind map functionality
├── templates/
│   ├── base.html          # Base template
│   ├── dashboard.html     # Main dashboard
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── study_plans.html   # Study plans management
│   ├── plan_detail.html   # Plan details and algorithms
│   ├── settings.html      # Subject/topic management
│   ├── notes.html         # Note taking interface
│   ├── pomodoro.html      # Pomodoro timer
│   ├── progress.html      # Progress tracking
│   ├── mindmap.html       # Mind map visualization
│   └── groups.html        # Study groups
├── NGROK/
│   └── *.py              # Cross-device setup scripts
└── README.md             # This file
```

## 🗄️ Database Schema

### Core Models
- **User**: User accounts and authentication
- **Subject**: Study subjects/courses
- **Topic**: Individual study topics with metadata
- **StudyPlan**: Collections of subjects for organized studying
- **Note**: User-created study notes
- **PomodoroSession**: Timer session tracking

### Collaborative Models
- **StudyGroup**: Group collaboration spaces
- **GroupMember**: Group membership tracking
- **GroupMessage**: Group chat messages

### Algorithm Support
- **BreakTime**: Stores transition times between topics for TSP optimization

## 🎯 Key Algorithms

### 1. Topological Sort (Kahn's Algorithm)
```python
def get_study_order(self):
    # Calculate in-degrees for all nodes
    # Process nodes with zero in-degree
    # Update in-degrees as nodes are processed
    # Return topologically sorted order
```

### 2. Asymmetric TSP (Exact + Heuristic)
```python
def optimize_schedule(self):
    # Build break time matrix
    # For small problems: try all permutations
    # For large problems: use greedy nearest neighbor
    # Return optimal path with minimal break time
```

### 3. Fractional Knapsack
```python
def knapsack_optimize(self):
    # Calculate value-to-weight ratios
    # Sort by ratio in descending order
    # Greedily select items until capacity is reached
    # Return selected topics for revision
```

## 🔧 Configuration

### Email Settings (Optional)
Update the email configuration in `intelliplan.py` for password recovery:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

### Database Configuration
The application uses SQLite by default. The database file is created automatically at:
```
instance/intelliplan.db
```

### Cross-Device Access
Use the ngrok scripts in the `NGROK/` folder to enable access from other devices on your network.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions, suggestions, or support, please open an issue on GitHub or contact the maintainer.

---

**Happy Studying! 📚✨**
