<div align="center">

# 🎓 Intelliplan - Your Smart Study Companion

[![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003b57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![HTML5](https://img.shields.io/badge/HTML5-e34f26?style=for-the-badge&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572b6?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)
[![JavaScript](https://img.shields.io/badge/JavaScript-f7df1e?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)


**A comprehensive Flask-based web application that helps students organize their study plans using advanced algorithms and data structures. Intelliplan combines modern web technologies with computer science algorithms to optimize study schedules and enhance learning efficiency.**

</div>

---

## ✨ Features

<table>
<tr>
<td>

### 📚 Core Study Management
- **📋 Study Plans**: Create and manage personalized study plans for different subjects
- **🎯 Topic Organization**: Add topics with dependencies, difficulty levels, and time estimates
- **📊 Progress Tracking**: Monitor completion status and study progress across subjects
- **🤖 Smart Algorithms**: Three optimization algorithms for different study scenarios

</td>
<td>

### 🧮 Algorithm-Powered Optimization
1. **🔄 Topological Sort**: Orders topics based on prerequisites and dependencies
2. **⚡ Study Break Optimization (TSP)**: Minimizes break time between topic transitions using Traveling Salesman Problem algorithms
3. **🎒 Revision Priority (Knapsack)**: Optimizes topic selection for revision based on available time and importance

</td>
</tr>
<tr>
<td>

### 🛠️ Productivity Tools
- **🍅 Pomodoro Timer**: Built-in timer with session tracking and statistics
- **📝 Note Taking**: Create, edit, and manage study notes with timestamps
- **🗺️ Mind Maps**: Visual representation of subjects and topics
- **📈 Progress Analytics**: Detailed statistics on study sessions and topic completion

</td>
<td>

### 👥 Collaborative Features
- **👥 Study Groups**: Create and join study groups with unique codes
- **💬 Real-time Chat**: WebSocket-powered group messaging
- **📱 Cross-device Support**: Ngrok integration for multi-device access

### 🔐 User Management
- **🔒 Authentication**: Secure user registration and login with Flask-Login
- **🔑 Password Recovery**: Email-based password reset functionality
- **⏰ Session Persistence**: Remember login sessions for up to 7 days
- **⚙️ User Settings**: Customizable preferences and profile management

</td>
</tr>
</table>

## 🏗️ Tech Stack

<div align="center">

### Backend Technologies
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-d71f00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003b57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Python](https://img.shields.io/badge/Python-3776ab?style=flat&logo=python&logoColor=white)](https://python.org)

### Frontend Technologies  
[![HTML5](https://img.shields.io/badge/HTML5-e34f26?style=flat&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572b6?style=flat&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)
[![JavaScript](https://img.shields.io/badge/JavaScript-f7df1e?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=flat&logo=socketdotio&logoColor=white)](https://websockets.spec.whatwg.org/)

### Libraries & Extensions
[![Flask-Login](https://img.shields.io/badge/Flask--Login-000000?style=flat&logo=flask&logoColor=white)](https://flask-login.readthedocs.io/)
[![Flask-SocketIO](https://img.shields.io/badge/Flask--SocketIO-000000?style=flat&logo=socketdotio&logoColor=white)](https://flask-socketio.readthedocs.io/)
[![Flask-Mail](https://img.shields.io/badge/Flask--Mail-000000?style=flat&logo=gmail&logoColor=white)](https://pythonhosted.org/Flask-Mail/)
[![Flask-CORS](https://img.shields.io/badge/Flask--CORS-000000?style=flat&logo=flask&logoColor=white)](https://flask-cors.readthedocs.io/)

</div>

### 🧮 Algorithms & Data Structures
- **🔄 Graph Algorithms**: Topological sorting for dependency resolution
- **⚡ Optimization**: TSP and Knapsack algorithms for study optimization  
- **📊 Data Structures**: Graphs, queues, and hash maps for efficient processing

## 📋 Prerequisites

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)
![pip](https://img.shields.io/badge/pip-latest-green?style=flat-square&logo=pypi&logoColor=white)
![Browser](https://img.shields.io/badge/Browser-Modern-orange?style=flat-square&logo=googlechrome&logoColor=white)
![ngrok](https://img.shields.io/badge/ngrok-optional-lightgrey?style=flat-square&logo=ngrok&logoColor=white)

</div>

- ✅ **Python 3.8 or higher**
- ✅ **pip** (Python package manager)
- ✅ **Modern web browser**
- ✅ **ngrok** (optional, for cross-device access)

## � Quick Start

<div align="center">

[![Get Started](https://img.shields.io/badge/Get%20Started-Click%20Here-success?style=for-the-badge&logo=rocket)](http://localhost:5000)

</div>

### 📥 Installation

1. **📂 Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelliplan.git
   cd intelliplan
   ```

2. **🐍 Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **📦 Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **🗄️ Initialize the database**
   ```bash
   python -c "from intelliplan import db; db.create_all()"
   ```

5. **▶️ Run the application**
   ```bash
   python intelliplan.py
   ```

6. **🌐 Access the application**
   Open your browser and navigate to **`http://localhost:5000`**

<div align="center">

**🎉 You're all set! Happy studying! 📚✨**

</div>

## � Usage Guide

<div align="center">

![Getting Started](https://img.shields.io/badge/Step%201-Register-blue?style=flat-square&logo=user-plus)
![Create Subjects](https://img.shields.io/badge/Step%202-Create%20Subjects-green?style=flat-square&logo=book)
![Add Topics](https://img.shields.io/badge/Step%203-Add%20Topics-orange?style=flat-square&logo=list)
![Study Plans](https://img.shields.io/badge/Step%204-Study%20Plans-purple?style=flat-square&logo=calendar)
![Optimize](https://img.shields.io/badge/Step%205-Run%20Algorithms-red?style=flat-square&logo=cpu)

</div>

### 🎯 Getting Started
1. **👤 Register** a new account or **🔑 login** with existing credentials
2. **📚 Create subjects** in the Settings page
3. **📝 Add topics** with dependencies, difficulty, and time estimates
4. **📋 Create study plans** by selecting subjects
5. **🚀 Run algorithms** to optimize your study schedule

### 🧮 Algorithm Usage

<table>
<tr>
<td>

#### 🔄 Topological Sort
- **🎯 Purpose**: Orders topics based on prerequisites
- **💡 Use Case**: Determine the correct learning sequence
- **📥 Input**: All topics with their dependencies
- **📤 Output**: Ordered list respecting all prerequisites

</td>
<td>

#### ⚡ Study Break Optimization (TSP)
- **🎯 Purpose**: Minimizes transition time between topics
- **💡 Use Case**: Optimize study session order to reduce break time
- **📥 Input**: Uncompleted topics with break time data
- **📤 Output**: Optimal topic sequence with minimal total break time

</td>
</tr>
<tr>
<td colspan="2">

#### 🎒 Revision Priority (Knapsack)
- **🎯 Purpose**: Maximizes learning value within time constraints
- **💡 Use Case**: Select topics for revision before exams
- **📥 Input**: Completed topics with time and importance ratings
- **📤 Output**: Prioritized revision list optimized for available time

</td>
</tr>
</table>

### 🛠️ Productivity Features
- Use the **🍅 Pomodoro Timer** for focused study sessions
- Take **📝 Notes** during study sessions
- Track **📊 Progress** across all subjects
- Join **👥 Study Groups** for collaborative learning

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

<div align="center">

![Database](https://img.shields.io/badge/Database-SQLite-blue?style=flat-square&logo=sqlite&logoColor=white)
![Models](https://img.shields.io/badge/Models-10+-green?style=flat-square&logo=database&logoColor=white)

</div>

<table>
<tr>
<td>

### 🔐 Core Models
- **👤 User**: User accounts and authentication
- **📚 Subject**: Study subjects/courses
- **📝 Topic**: Individual study topics with metadata
- **📋 StudyPlan**: Collections of subjects for organized studying
- **📄 Note**: User-created study notes
- **🍅 PomodoroSession**: Timer session tracking

</td>
<td>

### 👥 Collaborative Models
- **👥 StudyGroup**: Group collaboration spaces
- **🏷️ GroupMember**: Group membership tracking
- **💬 GroupMessage**: Group chat messages

### ⚡ Algorithm Support
- **⏱️ BreakTime**: Stores transition times between topics for TSP optimization

</td>
</tr>
</table>

## 🎯 Key Algorithms

<div align="center">

![Algorithms](https://img.shields.io/badge/Algorithms-3%20Core-blue?style=flat-square&logo=cpu&logoColor=white)
![Complexity](https://img.shields.io/badge/Complexity-Optimized-green?style=flat-square&logo=graph&logoColor=white)

</div>

<table>
<tr>
<td>

### 1. 🔄 Topological Sort (Kahn's Algorithm)
```python
def get_study_order(self):
    # Calculate in-degrees for all nodes
    # Process nodes with zero in-degree
    # Update in-degrees as nodes are processed
    # Return topologically sorted order
```
**⏱️ Time Complexity**: O(V + E)

</td>
<td>

### 2. ⚡ Asymmetric TSP (Exact + Heuristic)
```python
def optimize_schedule(self):
    # Build break time matrix
    # For small problems: try all permutations
    # For large problems: use greedy nearest neighbor
    # Return optimal path with minimal break time
```
**⏱️ Time Complexity**: O(n!) exact, O(n²) heuristic

</td>
</tr>
<tr>
<td colspan="2">

### 3. 🎒 Fractional Knapsack
```python
def knapsack_optimize(self):
    # Calculate value-to-weight ratios
    # Sort by ratio in descending order
    # Greedily select items until capacity is reached
    # Return selected topics for revision
```
**⏱️ Time Complexity**: O(n log n)

</td>
</tr>
</table>

## ⚙️ Configuration

<div align="center">

![Configuration](https://img.shields.io/badge/Config-Easy%20Setup-blue?style=flat-square&logo=gear&logoColor=white)
![Email](https://img.shields.io/badge/Email-Optional-yellow?style=flat-square&logo=email&logoColor=white)
![Database](https://img.shields.io/badge/Database-Auto%20Created-green?style=flat-square&logo=database&logoColor=white)

</div>

### 📧 Email Settings (Optional)
Update the email configuration in `intelliplan.py` for password recovery:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

### 🗄️ Database Configuration
The application uses SQLite by default. The database file is created automatically at:
```
📁 instance/intelliplan.db
```

### 📱 Cross-Device Access
Use the ngrok scripts in the `NGROK/` folder to enable access from other devices on your network.

---

## 🤝 Contributing

<div align="center">

[![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen?style=for-the-badge&logo=github)](https://github.com/yourusername/intelliplan/contribute)

</div>

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **💾 Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **📤 Push** to the branch (`git push origin feature/amazing-feature`)
5. **🔄 Open** a Pull Request

---

## 📧 Contact & Support

<div align="center">

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-red?style=for-the-badge&logo=github)](https://github.com/yourusername/intelliplan/issues)
[![Email](https://img.shields.io/badge/Email-Contact-blue?style=for-the-badge&logo=gmail)](mailto:your-email@example.com)

For questions, suggestions, or support, please open an issue on GitHub or contact the maintainer.

</div>

---

<div align="center">

## 🎉 Happy Studying! 📚✨

[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)](https://github.com/yourusername/intelliplan)

</div>
