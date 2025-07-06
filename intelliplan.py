# Intelliplan - Study Companion Application
# Flask backend with integrated DSA algorithms

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user,
    current_user
)
from flask_mail import Mail
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import secrets
import logging
import os
import datetime
from collections import defaultdict, deque
import datetime
import hashlib
import os
import logging
import itertools
import traceback

app = Flask(__name__)

# Configure CORS for ngrok and cross-device compatibility
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
        "supports_credentials": True
    }
})

# Configure logging to reduce verbosity
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app.config['SECRET_KEY'] = secrets.token_hex(16)
# Use absolute path to instance folder for database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "intelliplan.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration for Flask-Login persistence
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)  # Sessions last 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Email configuration (for password recovery)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Configure SocketIO with basic settings for maximum compatibility
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subjects = db.relationship('Subject', backref='user', lazy=True)
    study_plans = db.relationship('StudyPlan', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)
    pomodoro_sessions = db.relationship(
        'PomodoroSession', backref='user', lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topics = db.relationship(
        'Topic', backref='subject', lazy=True, cascade='all, delete-orphan'
    )


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    subject_id = db.Column(
        db.Integer, db.ForeignKey('subject.id'), nullable=False
    )
    dependencies = db.Column(db.Text)  # JSON string of topic dependencies
    difficulty = db.Column(db.Integer, nullable=True)  # 1-5 scale, set by user
    estimated_hours = db.Column(db.Float, nullable=True)  # Set by user
    importance = db.Column(db.Integer, nullable=True)  # For knapsack algorithm, set by user
    pages = db.Column(db.Integer, nullable=True)  # Weight for knapsack, set by user


class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subjects_data = db.Column(db.Text)  # JSON string of selected subjects


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class PomodoroSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Integer, default=25)  # minutes
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    description = db.Column(db.Text, default='')
    subject = db.Column(db.String(100), default='General')
    is_private = db.Column(db.Boolean, default=False)
    code = db.Column(db.String(20), unique=True)
    members = db.relationship('GroupMember', backref='group', lazy=True)
    messages = db.relationship('GroupMessage', backref='group', lazy=True)


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(
        db.Integer, db.ForeignKey('study_group.id'), nullable=False
    )
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(
        db.Integer, db.ForeignKey('study_group.id'), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class BreakTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    from_topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    to_topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    break_minutes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Unique constraint to prevent duplicate break time entries
    __table_args__ = (db.UniqueConstraint('subject_id', 'from_topic_id', 'to_topic_id', name='unique_break_time'),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Algorithm Classes
class TopologicalSort:
    def __init__(self, topics_data):
        self.graph = defaultdict(list)
        self.topics = {}
        self.build_graph(topics_data)
        
    def build_graph(self, topics_data):
        # Create a set of available topic IDs for quick lookup
        available_topic_ids = {topic['id'] for topic in topics_data}
        
        for topic in topics_data:
            self.topics[topic['id']] = topic
            if topic.get('dependencies'):
                deps_str = topic['dependencies']
                if isinstance(deps_str, str):
                    deps = json.loads(deps_str)
                else:
                    deps = deps_str
                for dep in deps:
                    # Only add dependencies if they are in the available topics
                    # (this handles dependencies on completed topics that were filtered out)
                    if dep in available_topic_ids:
                        self.graph[dep].append(topic['id'])
                        
    def get_study_order(self):
        in_degree = defaultdict(int)
        # Initialize in-degree for all topics
        for node in self.topics:
            if node not in in_degree:
                in_degree[node] = 0

        # Calculate in-degrees based on dependencies
        for node in self.graph:
            for neighbor in self.graph[node]:
                in_degree[neighbor] += 1

        # Start with nodes that have no dependencies (in-degree = 0)
        # No sorting by difficulty - just use order based on prerequisites
        available_nodes = [node for node in in_degree if in_degree[node] == 0]
        result = []

        while available_nodes:
            # Take the next available node without considering difficulty
            # This ensures ordering is based purely on prerequisites
            current_node = available_nodes.pop(0)
            result.append(self.topics[current_node])

            # Process topics that depend on the current topic
            for neighbor in self.graph[current_node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    available_nodes.append(neighbor)

        return result


class StudyBreakOptimizer:
    def __init__(self, topics_data, total_study_time=8, break_time=15, stored_break_times=None):
        self.topics = topics_data
        self.total_study_time = total_study_time  # in hours
        self.break_time = break_time  # in minutes (fallback)
        self.stored_break_times = stored_break_times or {}  # Stored break times from session

    def optimize_schedule(self):
        try:
            print(f"DEBUG StudyBreakOptimizer: Starting Open Asymmetric TSP optimization")
            print(f"  - Number of topics: {len(self.topics)}")
            print(f"  - Stored break times: {self.stored_break_times}")
            
            if not self.topics:
                print("DEBUG: No topics provided, returning empty result")
                return [], 0

            n = len(self.topics)
            print(f"DEBUG: Creating break time matrix for {n} topics")
            
            # Create break time matrix (asymmetric)
            break_time_matrix = [[0] * n for _ in range(n)]
            
            for i in range(n):
                for j in range(n):
                    if i == j:
                        break_time_matrix[i][j] = 0
                    else:
                        # Get directional break time
                        topic_i_id = self.topics[i].get('id')
                        topic_j_id = self.topics[j].get('id')
                        
                        if topic_i_id is None or topic_j_id is None:
                            print(f"WARNING: Missing topic ID for index {i} or {j}")
                            continue
                            
                        break_key = f'{topic_i_id}_{topic_j_id}'
                        
                        if break_key in self.stored_break_times:
                            break_weight = self.stored_break_times[break_key]
                            print(f"DEBUG: Break time {break_key}: {break_weight}")
                        else:
                            # Fallback to standard break time
                            break_weight = self.break_time
                            print(f"DEBUG: Using default break time {break_key}: {break_weight}")
                        
                        break_time_matrix[i][j] = break_weight

            # Print break time matrix for debugging
            print("DEBUG: Break time matrix:")
            for i in range(n):
                row_str = []
                for j in range(n):
                    row_str.append(f"{break_time_matrix[i][j]:4.1f}")
                print(f"  [{i}]: {' '.join(row_str)}")

            # Solve Open Asymmetric TSP - try all starting points
            best_path = None
            best_total_break_time = float('inf')
            best_start = 0

            print(f"DEBUG: Solving Open Asymmetric TSP...")
            
            if n <= 8:  # Use exact algorithm for small problems
                print(f"DEBUG: Using exact algorithm (n={n} <= 8)")
                
                for start in range(n):
                    print(f"DEBUG: Trying starting node {start} ({self.topics[start]['name']})")
                    
                    # Get all other nodes
                    remaining_nodes = [i for i in range(n) if i != start]
                    
                    # Try all permutations of remaining nodes
                    best_perm_cost = float('inf')
                    best_perm = None
                    
                    for perm in itertools.permutations(remaining_nodes):
                        # Calculate total break time for this path
                        path = [start] + list(perm)
                        total_break_time = 0
                        
                        for k in range(len(path) - 1):
                            from_node = path[k]
                            to_node = path[k + 1]
                            total_break_time += break_time_matrix[from_node][to_node]
                        
                        if total_break_time < best_perm_cost:
                            best_perm_cost = total_break_time
                            best_perm = path
                    
                    print(f"DEBUG:   Best for start {start}: cost={best_perm_cost}, path={best_perm}")
                    
                    if best_perm_cost < best_total_break_time:
                        best_total_break_time = best_perm_cost
                        best_path = best_perm
                        best_start = start
            
            else:  # Use heuristic for larger problems
                print(f"DEBUG: Using heuristic algorithm (n={n} > 8)")
                
                for start in range(n):
                    print(f"DEBUG: Trying starting node {start} ({self.topics[start]['name']})")
                    
                    # Greedy nearest neighbor from this start
                    visited = set([start])
                    current = start
                    path = [current]
                    total_break_time = 0
                    
                    while len(visited) < n:
                        best_next = -1
                        best_break_time = float('inf')
                        
                        for next_node in range(n):
                            if next_node not in visited:
                                break_time = break_time_matrix[current][next_node]
                                if break_time < best_break_time:
                                    best_break_time = break_time
                                    best_next = next_node
                        
                        if best_next != -1:
                            total_break_time += best_break_time
                            visited.add(best_next)
                            path.append(best_next)
                            current = best_next
                        else:
                            break                    
                    print(f"DEBUG:   Greedy for start {start}: cost={total_break_time}, path={path}")
                    
                    if total_break_time < best_total_break_time:
                        best_total_break_time = total_break_time
                        best_path = path
                        best_start = start

            print(f"DEBUG: OPTIMAL SOLUTION FOUND:")
            print(f"  - Best starting node: {best_start} ({self.topics[best_start]['name']})")
            print(f"  - Optimal path indices: {best_path}")
            print(f"  - Total break time: {best_total_break_time}")
            
            # Create readable path string
            path_names = " → ".join([self.topics[i]['name'] for i in best_path])
            print(f"  - Path: {path_names}")
            
            # Calculate individual break times for the optimal path
            individual_break_times = []
            for k in range(len(best_path) - 1):
                from_node = best_path[k]
                to_node = best_path[k + 1]
                break_time = break_time_matrix[from_node][to_node]
                individual_break_times.append(break_time)
            
            print(f"  - Individual break times: {individual_break_times}")            
            # Return topics in optimal order
            result = [self.topics[i] for i in best_path]
            
            print(f"DEBUG: Returning {len(result)} topics with total break time {best_total_break_time}")
            return result, round(best_total_break_time, 1), individual_break_times
            
        except Exception as e:
            print(f"ERROR in StudyBreakOptimizer.optimize_schedule: {str(e)}")
            traceback.print_exc()
            # Fallback: return topics in original order
            return self.topics, 0, []


class RevisionOptimizer:
    def __init__(self, topics_data, available_time):
        self.topics = topics_data
        self.available_time = available_time
        
    def knapsack_optimize(self):
        if not self.topics or self.available_time <= 0:
            return []

        # Fractional Knapsack Algorithm for Revision
        # Calculate value-to-weight ratio for each topic
        topic_ratios = []
        
        print(f"DEBUG KNAPSACK: Available time = {self.available_time}")
        print(f"DEBUG KNAPSACK: Number of topics = {len(self.topics)}")
        
        for i, topic in enumerate(self.topics):
            estimated_hours = topic.get('estimated_hours')
            importance = topic.get('importance')
            
            # Skip topics with missing values (difficulty not needed for fractional knapsack)
            if not estimated_hours or not importance:
                print(f"DEBUG KNAPSACK: Skipping topic '{topic.get('name')}' - missing values: hours={estimated_hours}, importance={importance}")
                continue
            
            # Value is simply the importance (no difficulty involved)
            value = importance
            
            # Calculate value-to-weight ratio
            ratio = value / estimated_hours if estimated_hours > 0 else 0
            
            print(f"DEBUG KNAPSACK: Topic '{topic.get('name')}' - hours: {estimated_hours}, importance: {importance}, value: {value}, ratio: {ratio}")
            
            topic_ratios.append({
                'index': i,
                'topic': topic,
                'value': value,
                'weight': estimated_hours,
                'ratio': ratio
            })
        
        # Sort by value-to-weight ratio in descending order
        topic_ratios.sort(key=lambda x: x['ratio'], reverse=True)
        
        print(f"DEBUG KNAPSACK: Sorted ratios: {[(item['topic'].get('name'), item['ratio']) for item in topic_ratios]}")
        
        selected_topics = []
        remaining_time = self.available_time
        
        # Fractional knapsack: take items with highest ratio first
        for item in topic_ratios:
            if remaining_time <= 0:
                break
                
            topic = item['topic'].copy()  # Create a copy to avoid modifying original
            weight = item['weight']
            
            print(f"DEBUG KNAPSACK: Processing '{topic.get('name')}' - weight: {weight}, remaining_time: {remaining_time}")
            
            if weight <= remaining_time:
                # Take the entire topic
                print(f"DEBUG KNAPSACK: Taking entire topic '{topic.get('name')}'")
                selected_topics.append(topic)
                remaining_time -= weight
            else:
                # Take a fraction of the topic
                fraction = remaining_time / weight
                topic['estimated_hours'] = remaining_time  # Update to fractional time
                topic['name'] = f"{topic['name']} (Partial: {fraction:.1%})"
                print(f"DEBUG KNAPSACK: Taking partial topic '{topic.get('name')}' - fraction: {fraction:.1%}")
                selected_topics.append(topic)
                remaining_time = 0
        
        print(f"DEBUG KNAPSACK: Final selected topics: {[t.get('name') for t in selected_topics]}")
        return selected_topics


# Generate a unique code for each group
def generate_group_code():
    code = secrets.token_urlsafe(8)
    while StudyGroup.query.filter_by(code=code).first():
        code = secrets.token_urlsafe(8)
    return code


# Helper function to save break times to the database
def save_break_time_to_db(subject_id, from_topic_id, to_topic_id, break_minutes):
    """Save or update a break time in the database."""
    try:
        # Check if this break time already exists
        existing_break_time = BreakTime.query.filter_by(
            subject_id=subject_id,
            from_topic_id=from_topic_id,
            to_topic_id=to_topic_id
        ).first()
        
        if existing_break_time:
            # Update existing record
            existing_break_time.break_minutes = break_minutes
            existing_break_time.updated_at = datetime.datetime.utcnow()
        else:
            # Create new record
            new_break_time = BreakTime(
                subject_id=subject_id,
                from_topic_id=from_topic_id,
                to_topic_id=to_topic_id,
                break_minutes=break_minutes
            )
            db.session.add(new_break_time)
        
        db.session.commit()
        app.logger.info(f'Saved break time: {from_topic_id} → {to_topic_id} = {break_minutes} minutes')
        return True
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error saving break time: {str(e)}')
        return False


# Routes
@app.route('/')
def splash():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('splash.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Enable persistent sessions (remember me)
            login_user(user, remember=True, duration=datetime.timedelta(days=7))
            return redirect(url_for('dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # For demo purposes, we'll just flash a success message
            # In production, you would:
            # 1. Generate a secure reset token
            # 2. Save it to the database with expiration
            # 3. Send email with reset link
            flash('If an account with that email exists, a password reset link has been sent.')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a password reset link has been sent.')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('splash'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    session_query = PomodoroSession.query.filter_by(
        user_id=current_user.id, completed=True
    )
    total_sessions = session_query.count()

    # Calculate total hours
    completed_sessions = session_query.all()
    total_hours = sum([s.duration for s in completed_sessions]) / 60

    completed_topics = 0
    total_topics = 0
    subjects = Subject.query.filter_by(user_id=current_user.id).all()

    for subject in subjects:
        topics = Topic.query.filter_by(subject_id=subject.id).all()
        total_topics += len(topics)
        completed_topics += len([t for t in topics if t.is_completed])

    return render_template(
        'dashboard.html',
        total_sessions=total_sessions,
        total_hours=round(total_hours, 1),
        completed_topics=completed_topics,
        total_topics=total_topics
    )


@app.route('/study-plans')
@login_required
def study_plans():
    plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('study_plans.html', plans=plans, subjects=subjects)


@app.route('/create-plan', methods=['POST'])
@login_required
def create_plan():
    plan_name = request.form['plan_name']
    selected_subject = request.form.get('subjects')  # Single subject instead of list
    
    if not selected_subject:
        flash('Please select a subject for your study plan', 'error')
        return redirect(url_for('study_plans'))

    plan = StudyPlan(
        name=plan_name,
        user_id=current_user.id,
        subjects_data=json.dumps([selected_subject])  # Still store as list for compatibility
    )
    db.session.add(plan)
    db.session.commit()
    
    flash(f'Study plan "{plan_name}" created successfully!', 'success')
    return redirect(url_for('study_plans'))


@app.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        return redirect(url_for('study_plans'))

    subject_ids = json.loads(plan.subjects_data)
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()

    return render_template('plan_detail.html', plan=plan, subjects=subjects)


@app.route('/delete-plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if plan.user_id != current_user.id:
        flash('You are not authorized to delete this study plan', 'error')
        return redirect(url_for('study_plans'))
    
    plan_name = plan.name
    db.session.delete(plan)
    db.session.commit()
    
    flash(f'Study plan "{plan_name}" has been deleted successfully', 'success')
    return redirect(url_for('study_plans'))


@app.route('/api/plan-topics/<int:plan_id>')
@login_required
def get_plan_topics(plan_id):
    """Get all topics for a specific study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'})

    subject_ids = json.loads(plan.subjects_data)
    topics = []

    for subject_id in subject_ids:
        subject_topics = Topic.query.filter_by(subject_id=subject_id).all()
        for topic in subject_topics:
            topics.append({
                'id': topic.id,
                'name': topic.name,
                'difficulty': topic.difficulty,
                'estimated_hours': topic.estimated_hours,
                'importance': topic.importance,
                'pages': topic.pages,
                'is_completed': topic.is_completed,
                'dependencies': topic.dependencies or '[]'
            })

    return jsonify({'topics': topics})


@app.route('/algorithm/<algorithm_type>/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def run_algorithm(algorithm_type, plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'})    
    
    # Get topics data for the plan
    subject_ids = json.loads(plan.subjects_data)
    
    if algorithm_type == 'topology':
        # For topological sort, include all topics (completed and uncompleted)
        topics_data = []
        for subject_id in subject_ids:
            topics = Topic.query.filter_by(subject_id=subject_id).all()
            for topic in topics:
                topics_data.append({
                    'id': topic.id,
                    'name': topic.name,                    'dependencies': topic.dependencies or '[]',
                    'difficulty': topic.difficulty,
                    'estimated_hours': topic.estimated_hours,
                    'importance': topic.importance,
                    'pages': topic.pages,
                    'is_completed': topic.is_completed
                })
    else:        # For TSP, only include uncompleted topics
        # For Knapsack (revision), only include completed topics
        topics_data = []
        for subject_id in subject_ids:
            if algorithm_type == 'knapsack':
                # For revision, only get completed topics
                topics = Topic.query.filter_by(subject_id=subject_id, is_completed=True).all()
                print(f"DEBUG: Algorithm {algorithm_type}, Subject {subject_id}: Found {len(topics)} completed topics for revision")
            else:                # For TSP, get uncompleted topics
                topics = Topic.query.filter_by(subject_id=subject_id, is_completed=False).all()
                print(f"DEBUG: Algorithm {algorithm_type}, Subject {subject_id}: Found {len(topics)} uncompleted topics")
            
            for topic in topics:
                print(f"DEBUG: Adding topic {topic.name}, completed: {topic.is_completed}")
                topics_data.append({
                    'id': topic.id,                    'name': topic.name,
                    'dependencies': topic.dependencies or '[]',
                    'difficulty': topic.difficulty,
                    'estimated_hours': topic.estimated_hours,
                    'importance': topic.importance,                    'pages': topic.pages,
                    'is_completed': topic.is_completed
                })
            
    if algorithm_type == 'topology':
        sorter = TopologicalSort(topics_data)
        result = sorter.get_study_order()
        return jsonify({
            'result': result, 
            'type': 'Topic Dependency Order'
        })
    elif algorithm_type == 'TSP':
        # Validate that we have uncompleted topics for study break optimization
        if not topics_data:
            return jsonify({
                'error': 'No uncompleted topics found for study break optimization. Complete some topics first or add more topics to optimize study breaks.'
            })
          # Extract break times from database for all subjects in the plan
        break_times_data = {}
        for subject_id in subject_ids:
            print(f"DEBUG: Loading break times for subject {subject_id}")
            break_times_records = BreakTime.query.filter_by(subject_id=subject_id).all()
            subject_break_times = {}
            for record in break_times_records:
                key = f"{record.from_topic_id}_{record.to_topic_id}"
                subject_break_times[key] = record.break_minutes
            print(f"DEBUG: Found break times for subject {subject_id}: {subject_break_times}")
            break_times_data.update(subject_break_times)
        
        print(f"DEBUG: All break times data: {break_times_data}")
          # Calculate average break time from stored data, fallback to 15 minutes
        if break_times_data:
            break_time = sum(break_times_data.values()) / len(break_times_data)
        else:
            break_time = 15  # Default fallback
        
        # Pass stored break times to optimizer
        try:
            print(f"DEBUG: Creating StudyBreakOptimizer with:")
            print(f"  - Topics count: {len(topics_data)}")
            print(f"  - Break times data: {break_times_data}")
            print(f"  - Break time fallback: {break_time}")
            
            optimizer = StudyBreakOptimizer(
                topics_data, 
                total_study_time=12,  # Not used anymore since we include all topics
                break_time=break_time, 
                stored_break_times=break_times_data
            )
            result, actual_total_break_time, individual_break_times = optimizer.optimize_schedule()
            
            print(f"DEBUG: Optimization completed successfully")
            print(f"  - Result topics count: {len(result)}")
            print(f"  - Total break time: {actual_total_break_time}")
            
        except Exception as e:
            print(f"ERROR in StudyBreakOptimizer: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': f'An error occurred while running Study Break Optimization: {str(e)}'
            })
          # Return actual calculated total break time and individual break times
        return jsonify({
            'result': result, 
            'type': 'Study Break Optimization',
            'parameters': {
                'totalBreakTime': actual_total_break_time,
                'averageBreakTime': round(break_time, 1),
                'individualBreakTimes': individual_break_times
            }
        })
    elif algorithm_type == 'knapsack':
        # Get time before exam and topic-specific settings for revision
        if request.method == 'POST':
            data = request.get_json()
            time_before_exam = data.get('timeBeforeExam', 24)
            topic_settings = data.get('topicSettings', [])
            
            # Create a dictionary of topic settings for quick lookup
            topic_settings_dict = {}
            for setting in topic_settings:
                topic_settings_dict[setting['id']] = {
                    'estHours': setting['estHours'],
                    'importance': setting['importance']
                }
        else:
            time_before_exam = float(request.args.get('time', 24))
            topic_settings_dict = {}
        
        # Validate that we have completed topics for revision
        if not topics_data:
            return jsonify({
                'error': 'No completed topics found for revision. Complete some topics first before running revision optimization.'
            })        # Apply revision-specific topic settings from the modal
        print(f"DEBUG KNAPSACK ENDPOINT: Time before exam = {time_before_exam}")
        print(f"DEBUG KNAPSACK ENDPOINT: Number of topics = {len(topics_data)}")
        print(f"DEBUG KNAPSACK ENDPOINT: Topic settings provided = {len(topic_settings_dict)}")
        
        for topic in topics_data:
            topic_id = topic['id']
            
            # Use custom revision settings from the modal if provided
            if topic_id in topic_settings_dict:
                topic['estimated_hours'] = topic_settings_dict[topic_id]['estHours']
                topic['importance'] = topic_settings_dict[topic_id]['importance']
                print(f"DEBUG KNAPSACK ENDPOINT: Topic {topic['name']} - Using custom settings: hours={topic['estimated_hours']}, importance={topic['importance']}")
            else:
                # Keep original values from database if no custom settings provided
                print(f"DEBUG KNAPSACK ENDPOINT: Topic {topic['name']} - Using database values: hours={topic['estimated_hours']}, importance={topic['importance']}")
        
        optimizer = RevisionOptimizer(topics_data, time_before_exam)
        result = optimizer.knapsack_optimize()
          # Prepare topic settings for response (show what values were used)
        applied_settings = {}
        for topic in topics_data:
            applied_settings[topic['id']] = {
                'estHours': topic['estimated_hours'],
                'importance': topic['importance']
            }
                
        return jsonify({
            'result': result, 
            'type': 'Revision Priority',
            'parameters': {
                'timeBeforeExam': time_before_exam,
                'appliedSettings': applied_settings
            }
        })

    return jsonify({'error': 'Invalid algorithm type'})


@app.route('/tools')
@login_required
def tools():
    return render_template('tools.html')


@app.route('/pomodoro')
@login_required
def pomodoro():
    return render_template('pomodoro.html')


@app.route('/save-session', methods=['POST'])
@login_required
def save_session():
    duration = request.json.get('duration', 25)
    completed = request.json.get('completed', False)

    pomodoro_session = PomodoroSession(
        user_id=current_user.id,
        duration=duration,
        completed=completed
    )
    db.session.add(pomodoro_session)
    db.session.commit()

    return jsonify({'success': True})


@app.route('/get-user-stats')
@login_required
def get_user_stats():
    # Get all completed sessions (like dashboard does)
    session_query = PomodoroSession.query.filter_by(
        user_id=current_user.id,
        completed=True
    )
    completed_sessions = session_query.all()
    
    # Calculate stats
    completed_count = len(completed_sessions)
    total_time = sum(session.duration for session in completed_sessions)
    
    # Calculate streak (consecutive days with completed sessions)
    # Get unique dates with completed sessions
    today = datetime.datetime.now().date()
    streak = 0
    current_date = today
    
    while True:
        day_start = datetime.datetime.combine(current_date, datetime.time.min)
        day_end = datetime.datetime.combine(current_date, datetime.time.max)
        
        day_sessions = PomodoroSession.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).filter(
            PomodoroSession.created_at >= day_start,
            PomodoroSession.created_at <= day_end
        ).count()
        
        if day_sessions > 0:
            streak += 1
            current_date = current_date - datetime.timedelta(days=1)
        else:
            break
        
        # Prevent infinite loop for very old data
        if streak > 365:
            break
    
    stats = {
        'completedSessions': completed_count,
        'totalStudyTime': total_time,
        'streak': streak
    }
    
    return jsonify({'success': True, 'stats': stats})


@app.route('/notes')
@login_required
def notes():
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(
        Note.created_at.desc()
    ).all()
    return render_template('notes.html', notes=user_notes)


@app.route('/save-note', methods=['POST'])
@login_required
def save_note():
    title = request.form['title']
    content = request.form['content']

    note = Note(
        title=title,
        content=content,
        user_id=current_user.id
    )
    db.session.add(note)
    db.session.commit()

    return redirect(url_for('notes'))


@app.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('notes'))


@app.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Check if user owns this note
    if note.user_id != current_user.id:
        return redirect(url_for('notes'))
    
    if request.method == 'POST':
        # Update the note
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('notes'))
    
    # GET request - return note data as JSON for AJAX requests
    if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({
            'id': note.id,
            'title': note.title,
            'content': note.content
        })
    
    # Regular GET request - render edit form
    return render_template('notes.html', notes=Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all(), edit_note=note)


@app.route('/mindmap')
@login_required
def mindmap():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('mindmap.html', subjects=subjects)


@app.route('/get-topics/<int:subject_id>')
@login_required
def get_topics(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'})
    
    topics = Topic.query.filter_by(subject_id=subject_id).all()
    return jsonify({
        'topics': [{
            'id': topic.id,
            'name': topic.name,
            'is_completed': topic.is_completed
        } for topic in topics]
    })


@app.route('/toggle-topic/<int:topic_id>', methods=['POST'])
@login_required
def toggle_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    subject = Subject.query.get_or_404(topic.subject_id)

    if subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'})

    topic.is_completed = not topic.is_completed
    db.session.commit()

    return jsonify({'success': True, 'completed': topic.is_completed})


@app.route('/progress')
@login_required
def progress():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    progress_data = []

    for subject in subjects:
        topics = Topic.query.filter_by(subject_id=subject.id).all()
        total_topics = len(topics)
        completed_topics = len([t for t in topics if t.is_completed])
        if total_topics > 0:
            percentage = (completed_topics / total_topics * 100)
        else:
            percentage = 0

        progress_data.append({
            'subject': subject.name,
            'percentage': round(percentage, 1),
            'completed': completed_topics,
            'total': total_topics
        })

    # Get study statistics
    session_query = PomodoroSession.query.filter_by(
        user_id=current_user.id, completed=True
    )
    total_sessions = session_query.count()
    completed_sessions = session_query.all()
    total_hours = sum([s.duration for s in completed_sessions]) / 60

    return render_template(
        'progress.html',
        progress_data=progress_data,
        total_sessions=total_sessions,
        total_hours=round(total_hours, 1)
    )


@app.route('/groups')
@login_required
def groups():
    return render_template('groups.html')


@app.route('/create-group', methods=['POST'])
@login_required
def create_group():
    group_name = request.form['group_name']

    # Generate unique code for the group
    group_code = generate_group_code()
    
    group = StudyGroup(
        name=group_name,
        created_by=current_user.id,
        code=group_code,
        description=request.form.get('description', ''),
        subject=request.form.get('subject', 'General'),
        is_private=request.form.get('is_private', False)
    )
    db.session.add(group)
    db.session.flush()  # Get the group ID

    # Add creator as member
    member = GroupMember(
        user_id=current_user.id,
        group_id=group.id
    )
    db.session.add(member)
    db.session.commit()

    return redirect(url_for('groups'))


@app.route('/settings')
@login_required
def settings():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('settings.html', subjects=subjects)


@app.route('/add-subject', methods=['POST'])
@login_required
def add_subject():
    try:
        subject_name = request.form['subject_name'].strip()
        
        if not subject_name:
            flash('Subject name is required', 'error')
            return redirect(url_for('settings'))
        
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(
            name=subject_name, 
            user_id=current_user.id
        ).first()
        if existing_subject:
            flash(f'Subject "{subject_name}" already exists', 'error')
            return redirect(url_for('settings'))

        # Create the subject
        subject = Subject(
            name=subject_name,
            user_id=current_user.id
        )
        db.session.add(subject)
        db.session.commit()
        
        flash(f'Subject "{subject_name}" created successfully! Now you can add topics individually with detailed settings.', 'success')
            
        return redirect(url_for('settings'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding subject: {str(e)}')
        flash(f'Error adding subject: {str(e)}', 'error')
        return redirect(url_for('settings'))


@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id == current_user.id:
        db.session.delete(subject)
        db.session.commit()
    return redirect(url_for('settings'))


@app.route('/add-topic', methods=['POST'])
@login_required
def add_topic():
    try:        # Get form data with validation
        topic_name = request.form.get('topic_name', '').strip()
        subject_id = request.form.get('subject_id')
          # Validate required fields
        if not topic_name:
            flash('Topic name is required', 'error')
            return redirect(url_for('settings') + f'#subject-{subject_id}')
        
        if not subject_id:
            flash('Subject ID is required', 'error')
            return redirect(url_for('settings'))
        
        # No default values - let user configure these in the revision modal
        difficulty = None
        estimated_hours = None
        importance = None
        pages = None
        
        # Handle prerequisites (multi-select)
        prerequisites = request.form.getlist('prerequisites')  # Get list of selected prerequisite topic IDs
        prerequisites_json = json.dumps([int(pid) for pid in prerequisites if pid]) if prerequisites else None
          # Handle individual break times with existing topics (DIRECTIONAL)
        break_times = {}
        existing_topics = Topic.query.filter_by(subject_id=subject_id).all()
        
        for existing_topic in existing_topics:
            # Get break time from NEW topic TO existing topic
            break_time_to_key = f'break_time_to_{existing_topic.id}'
            break_time_to_value = request.form.get(break_time_to_key)
            
            # Get break time from existing topic TO NEW topic
            break_time_from_key = f'break_time_from_{existing_topic.id}'
            break_time_from_value = request.form.get(break_time_from_key)
            
            if break_time_to_value:
                try:
                    break_time_minutes = int(break_time_to_value)
                    if break_time_minutes >= 0:  # Allow 0 for no break
                        break_times[f'to_{existing_topic.id}'] = break_time_minutes
                        app.logger.info(f'Break time from "{topic_name}" TO "{existing_topic.name}": {break_time_minutes} minutes')
                except (ValueError, TypeError):
                    flash(f'Invalid break time value from "{topic_name}" to "{existing_topic.name}"', 'error')
                    return redirect(url_for('settings'))
            
            if break_time_from_value:
                try:
                    break_time_minutes = int(break_time_from_value)
                    if break_time_minutes >= 0:  # Allow 0 for no break
                        break_times[f'from_{existing_topic.id}'] = break_time_minutes
                        app.logger.info(f'Break time from "{existing_topic.name}" TO "{topic_name}": {break_time_minutes} minutes')
                except (ValueError, TypeError):
                    flash(f'Invalid break time value from "{existing_topic.name}" to "{topic_name}"', 'error')
                    return redirect(url_for('settings'))
          # Store break times in session for algorithm use (you can modify this to suit your storage needs)
        if break_times:
            session[f'break_times_{subject_id}'] = session.get(f'break_times_{subject_id}', {})
            # We'll store this after the topic is created so we have the new topic ID

        # Verify subject belongs to user
        subject = Subject.query.get_or_404(subject_id)
        if subject.user_id != current_user.id:
            flash('Access denied: Subject does not belong to you', 'error')
            return redirect(url_for('settings'))

        # Check for duplicate topic names within the same subject
        existing_topic = Topic.query.filter_by(
            subject_id=subject_id, 
            name=topic_name
        ).first()
        if existing_topic:
            flash(f'Topic "{topic_name}" already exists in this subject', 'error')
            return redirect(url_for('settings'))

        # Create new topic
        topic = Topic(
            name=topic_name,
            subject_id=subject_id,
            difficulty=difficulty,
            estimated_hours=estimated_hours,
            importance=importance,
            pages=pages,            dependencies=prerequisites_json  # Store prerequisites as JSON
        )
        
        db.session.add(topic)
        db.session.commit()
          # Store break times in session after topic creation (now we have the topic ID)
        if break_times:
            session[f'break_times_{subject_id}'] = session.get(f'break_times_{subject_id}', {})
            for break_key, break_time_minutes in break_times.items():
                if break_key.startswith('to_'):
                    # Break time from new topic TO existing topic
                    existing_topic_id = break_key.replace('to_', '')
                    session[f'break_times_{subject_id}'][f'{topic.id}_{existing_topic_id}'] = break_time_minutes
                elif break_key.startswith('from_'):
                    # Break time from existing topic TO new topic
                    existing_topic_id = break_key.replace('from_', '')
                    session[f'break_times_{subject_id}'][f'{existing_topic_id}_{topic.id}'] = break_time_minutes
            
            app.logger.info(f'Stored directional break times for topic "{topic_name}" (ID: {topic.id})')        # Create success message with prerequisites info
        success_msg = f'Topic "{topic_name}" added successfully!'
        if prerequisites:
            prereq_count = len([pid for pid in prerequisites if pid])
            success_msg += f' ({prereq_count} prerequisite(s) set)'
        if break_times:
            break_time_count = len(break_times)
            success_msg += f' ({break_time_count} directional break time(s) configured)'
        
        flash(success_msg, 'success')
        return redirect(url_for('settings') + f'#subject-{subject_id}')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding topic: {str(e)}')
        flash(f'Error adding topic: {str(e)}', 'error')
        return redirect(url_for('settings') + f'#subject-{subject_id}')


@app.route('/delete-topic/<int:topic_id>', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    subject = Subject.query.get_or_404(topic.subject_id)
    if subject.user_id == current_user.id:
        db.session.delete(topic)
        db.session.commit()
    return redirect(url_for('settings'))


@app.route('/edit-topic/<int:topic_id>', methods=['POST'])
@login_required
def edit_topic(topic_id):
    try:
        topic = Topic.query.get_or_404(topic_id)
        subject = Subject.query.get_or_404(topic.subject_id)
        
        # Verify topic belongs to current user
        if subject.user_id != current_user.id:
            flash('Access denied: Topic does not belong to you', 'error')
            return redirect(url_for('settings'))
        
        # Get form data with validation
        topic_name = request.form.get('topic_name', '').strip()
        
        if not topic_name:
            flash('Topic name is required', 'error')
            return redirect(url_for('settings'))
          # Keep existing values for the fields that are no longer in the form
        # These will be configurable in the knapsack modal on the view plan page instead
        difficulty = topic.difficulty
        estimated_hours = topic.estimated_hours
        importance = topic.importance  
        pages = topic.pages
        
        # Check for duplicate topic names within the same subject (excluding current topic)
        existing_topic = Topic.query.filter_by(
            subject_id=subject.id, 
            name=topic_name
        ).filter(Topic.id != topic_id).first()
        
        if existing_topic:
            flash(f'Topic "{topic_name}" already exists in this subject', 'error')
            return redirect(url_for('settings'))        # Handle prerequisites (multi-select)
        prerequisites = request.form.getlist('prerequisites')  # Get list of selected prerequisite topic IDs
        prerequisites_json = json.dumps([int(pid) for pid in prerequisites if pid]) if prerequisites else None
        
        # Update topic properties
        old_name = topic.name
        topic.name = topic_name
        topic.difficulty = difficulty
        topic.estimated_hours = estimated_hours
        topic.importance = importance
        topic.pages = pages
        topic.dependencies = prerequisites_json          # Handle individual break times with existing topics (DIRECTIONAL - same as add_topic)
        break_times = {}
        existing_topics = Topic.query.filter_by(subject_id=subject.id).all()
        
        for existing_topic in existing_topics:
            if existing_topic.id != topic_id:  # Don't process break time with itself
                # Get break time from CURRENT topic TO other topic
                break_time_to_key = f'break_time_to_{existing_topic.id}'
                break_time_to_value = request.form.get(break_time_to_key)
                
                # Get break time from other topic TO CURRENT topic
                break_time_from_key = f'break_time_from_{existing_topic.id}'
                break_time_from_value = request.form.get(break_time_from_key)
                
                if break_time_to_value:
                    try:
                        break_time_minutes = int(break_time_to_value)
                        if break_time_minutes >= 0:  # Allow 0 for no break
                            break_times[f'to_{existing_topic.id}'] = break_time_minutes
                            app.logger.info(f'Break time from "{topic_name}" TO "{existing_topic.name}": {break_time_minutes} minutes')
                    except (ValueError, TypeError):
                        flash(f'Invalid break time value from "{topic_name}" to "{existing_topic.name}"', 'error')
                        return redirect(url_for('settings'))
                
                if break_time_from_value:
                    try:
                        break_time_minutes = int(break_time_from_value)
                        if break_time_minutes >= 0:  # Allow 0 for no break
                            break_times[f'from_{existing_topic.id}'] = break_time_minutes
                            app.logger.info(f'Break time from "{existing_topic.name}" TO "{topic_name}": {break_time_minutes} minutes')
                    except (ValueError, TypeError):
                        flash(f'Invalid break time value from "{existing_topic.name}" to "{topic_name}"', 'error')
                        return redirect(url_for('settings'))
          # Store break times in database (if any were provided)
        if break_times:
            # Store directional break times in the database
            for break_key, break_time_minutes in break_times.items():
                if break_key.startswith('to_'):
                    # Break time from current topic TO other topic
                    other_topic_id = int(break_key.replace('to_', ''))
                    save_break_time_to_db(subject.id, topic_id, other_topic_id, break_time_minutes)
                elif break_key.startswith('from_'):
                    # Break time from other topic TO current topic
                    other_topic_id = int(break_key.replace('from_', ''))
                    save_break_time_to_db(subject.id, other_topic_id, topic_id, break_time_minutes)
            
            app.logger.info(f'Stored directional break times for topic {topic_id}: {break_times}')        
        db.session.commit()
        
        flash('Topic updated successfully', 'success')
        app.logger.info(f'Topic "{old_name}" (ID: {topic_id}) updated by user {current_user.username}')
        
        return redirect(url_for('settings'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error editing topic: {str(e)}')
        flash(f'Error updating topic: {str(e)}', 'error')
        return redirect(url_for('settings'))


# API endpoints for user settings and profile management
@app.route('/api/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    """Get user settings and preferences."""
    try:
        # Default settings - could be stored in database if needed
        settings = {
            'pomodoroDuration': '25',
            'breakDuration': '5',
            'difficultyPreference': 'medium',
            'weeklyGoal': '20',
            'autoSave': True,
            'smartReminders': True,
            'theme': 'light',
            'language': 'en',
            'timezone': 'UTC',
            'studyReminders': True,
            'breakReminders': True,
            'goalReminders': False,
            'groupMessages': True,
            'groupInvites': True,
            'memberActivity': False,
            'achievementNotifications': True,
            'progressUpdates': False,
            'browserNotifications': True,
            'emailNotifications': False,
            'profileVisibility': 'friends',
            'statsVisibility': 'friends',
            'allowGroupInvites': True,
            'showOnlineStatus': True,
            'dataCollection': False
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/settings', methods=['PUT'])
@login_required
def update_user_settings():
    """Update user settings and preferences."""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        
        # In a real implementation, you'd save these to a UserSettings table
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """Update user profile information."""
    try:
        data = request.get_json()
        
        if 'email' in data:
            current_user.email = data['email']
        
        # Note: full_name, bio, study_goals would need to be added to User model
        # For now, we'll just update what we can
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/password', methods=['PUT'])
@login_required
def change_user_password():
    """Change user password."""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required'
            }), 400
        
        # Check current password
        if not check_password_hash(current_user.password_hash, current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/export', methods=['GET'])
@login_required
def export_user_data():
    """Export user data as JSON."""
    try:
        # Gather all user data
        user_data = {
            'user_info': {
                'username': current_user.username,
                'email': current_user.email,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            },
            'subjects': [],
            'study_plans': [],
            'notes': [],
            'pomodoro_sessions': []
        }
          # Export subjects and topics
        for subject in current_user.subjects:
            subject_data = {
                'name': subject.name,
                'topics': []
            }
            
            for topic in subject.topics:
                topic_data = {
                    'name': topic.name,
                    'difficulty': topic.difficulty,
                    'estimated_hours': topic.estimated_hours,
                    'importance': topic.importance,
                    'pages': topic.pages,
                    'is_completed': topic.is_completed
                }
                subject_data['topics'].append(topic_data)
            
            user_data['subjects'].append(subject_data)
        
        # Export study plans
        for plan in current_user.study_plans:
            plan_data = {
                'name': plan.name,
                'created_at': plan.created_at.isoformat() if plan.created_at else None,
                'subjects_data': plan.subjects_data
            }
            user_data['study_plans'].append(plan_data)
        
        # Create response
        response = jsonify(user_data)
        response.headers['Content-Disposition'] = f'attachment; filename=intelliplan-data-{current_user.username}.json'
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/import', methods=['POST'])
@login_required
def import_user_data():
    """Import user data from uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Read and parse JSON
        import json
        data = json.loads(file.read().decode('utf-8'))
        
        # Import subjects and topics
        if 'subjects' in data:
            for subject_data in data['subjects']:
                # Check if subject already exists
                existing_subject = Subject.query.filter_by(
                    name=subject_data['name'], 
                    user_id=current_user.id
                ).first()
                
                if not existing_subject:
                    subject = Subject(
                        name=subject_data['name'],
                        user_id=current_user.id
                    )
                    db.session.add(subject)
                    db.session.flush()  # Get subject ID
                    
                    # Import topics
                    if 'topics' in subject_data:
                        for topic_data in subject_data['topics']:
                            topic = Topic(
                                name=topic_data['name'],
                                difficulty=topic_data.get('difficulty', 3),
                                estimated_hours=topic_data.get('estimated_hours', 2),
                                importance=topic_data.get('importance', 3),
                                pages=topic_data.get('pages', 10),
                                is_completed=topic_data.get('is_completed', False),
                                subject_id=subject.id
                            )
                            db.session.add(topic)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Data imported successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/clear-data', methods=['DELETE'])
@login_required
def clear_user_data():
    """Clear all user data except account."""
    try:
        # Delete topics first (foreign key constraint)
        for subject in current_user.subjects:
            Topic.query.filter_by(subject_id=subject.id).delete()
        
        # Delete subjects
        Subject.query.filter_by(user_id=current_user.id).delete()
        
        # Delete study plans
        StudyPlan.query.filter_by(user_id=current_user.id).delete()
        
        # Delete notes if they exist
        # Note.query.filter_by(user_id=current_user.id).delete()
        
        # Delete pomodoro sessions if they exist
        # PomodoroSession.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/delete-account', methods=['DELETE'])
@login_required
def delete_user_account():
    """Delete user account and all associated data."""
    try:
        user_id = current_user.id
        
        # Delete all associated data first
        for subject in current_user.subjects:
            Topic.query.filter_by(subject_id=subject.id).delete()
        
        Subject.query.filter_by(user_id=user_id).delete()
        StudyPlan.query.filter_by(user_id=user_id).delete()
        
        # Delete the user account
        User.query.filter_by(id=user_id).delete()
        
        db.session.commit()
        logout_user()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/debug-session')
@login_required
def debug_session():
    """Debug route to check session data"""
    session_data = {}
    
    # Check for break time keys in session
    for key, value in session.items():
        if 'break_times' in key:
            session_data[key] = value
    
    # Get all subjects for current user
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    subject_info = []
    
    for subject in subjects:
        topics = Topic.query.filter_by(subject_id=subject.id).all()
        subject_info.append({
            'id': subject.id,
            'name': subject.name,
            'topic_count': len(topics),
            'topics': [{'id': t.id, 'name': t.name} for t in topics]
        })
    
    return jsonify({
        'session_data': session_data,
        'subjects': subject_info,
        'total_session_keys': len(session.keys()),
        'all_session_keys': list(session.keys())
    })


# Socket.IO events for group chat
@socketio.on('connect')
def on_connect():
    print(f"🔌 Socket.IO connected: User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"👤 Authenticated user: {current_user.username}")
    else:
        print("❌ User not authenticated for Socket.IO")

@socketio.on('join')
def on_join(data):
    if not current_user.is_authenticated:
        print("❌ Unauthenticated user trying to join room")
        return
        
    room = data['room']
    print(f"🏠 User {current_user.username} joining room {room}")
    join_room(room)
    
    # Also join the group room for member updates
    group_room = f'group_{room}'
    join_room(group_room)
    
    # Emit to the group room that user joined (broadcast to others)
    socketio.emit('user_joined', {
        'group_id': room,
        'username': current_user.username
    }, room=group_room, include_self=False)
    
    # Send status message to chat room (broadcast to all including sender)
    message = f'{current_user.username} has entered the chat.'
    socketio.emit('status', {'msg': message}, room=room)


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    
    # Also leave the group room
    group_room = f'group_{room}'
    leave_room(group_room)
    
    # Emit to the group room that user left
    socketio.emit('user_left', {
        'group_id': room,
        'username': current_user.username
    }, room=group_room, include_self=False)
    
    # Send status message to chat room
    message = f'{current_user.username} has left the chat.'
    socketio.emit('status', {'msg': message}, room=room)


@socketio.on('message')
def handle_message(data):
    if not current_user.is_authenticated:
        print("❌ Unauthenticated user trying to send message")
        return
        
    room = data['room']
    message_text = data['message']
    
    print(f"📨 Message from {current_user.username} in room {room}: {message_text}")

    # Save message to database
    message = GroupMessage(
        user_id=current_user.id,
        group_id=room,
        message=message_text
    )
    db.session.add(message)
    db.session.commit()

    # Emit to all users in the room (including sender)
    message_data = {
        'message': message_text,
        'username': current_user.username,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }
    print(f"📤 Broadcasting message to room {room}: {message_data}")
    socketio.emit('message', message_data, room=room)


@socketio.on('typing')
def handle_typing(data):
    if 'room' not in data or 'is_typing' not in data:
        return
    
    room = data['room']
    is_typing = data['is_typing']
    
    # Emit to everyone in the room except the sender
    socketio.emit('user_typing', {
        'group_id': room,
        'sender': current_user.username,
        'is_typing': is_typing
    }, room=room, include_self=False)


@socketio.on('test_message')
def handle_test_message(data):
    """Handle test messages from connection test page"""
    emit('test_response', {'status': 'success', 'message': 'Socket.IO working correctly!'})


@app.route('/api/topics/<int:subject_id>', methods=['GET'])
@login_required
def get_subject_topics(subject_id):
    """Get all topics for a specific subject."""
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Check if the subject belongs to the current user
        if subject.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        topics = Topic.query.filter_by(subject_id=subject_id).all()
        topics_data = []
        
        for topic in topics:
            topics_data.append({
                'id': topic.id,
                'name': topic.name,
                'is_completed': topic.is_completed,
                'dependencies': json.loads(topic.dependencies) if topic.dependencies else []
            })
            
        return jsonify({
            'subject_id': subject_id,
            'topics': topics_data
        })
    except Exception as e:
        app.logger.error(f'Error getting topics: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/topic/<int:topic_id>', methods=['GET'])
@login_required
def get_topic_details(topic_id):
    """Get details for a specific topic."""
    try:
        topic = Topic.query.get_or_404(topic_id)
        subject = Subject.query.get_or_404(topic.subject_id)
        
        # Check if the topic belongs to the current user
        if subject.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        topic_data = {
            'id': topic.id,
            'name': topic.name,
            'is_completed': topic.is_completed,
            'subject_id': topic.subject_id,
            'dependencies': json.loads(topic.dependencies) if topic.dependencies else []
        }
            
        return jsonify(topic_data)
    except Exception as e:
        app.logger.error(f'Error getting topic details: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/break-times/<int:subject_id>', methods=['GET'])
@login_required
def get_break_times(subject_id):
    """Get stored break times for a subject."""
    try:
        app.logger.info(f'Getting break times for subject {subject_id}')
        
        # Verify the subject belongs to the current user
        subject = Subject.query.get_or_404(subject_id)
        if subject.user_id != current_user.id:
            app.logger.warning(f'Access denied for subject {subject_id} by user {current_user.id}')
            return jsonify({'error': 'Access denied'}), 403
        
        # Get stored break times from database
        break_times_records = BreakTime.query.filter_by(subject_id=subject_id).all()
        
        # Convert to the format expected by frontend (key: "from_id_to_id", value: minutes)
        break_times_data = {}
        for record in break_times_records:
            key = f"{record.from_topic_id}_{record.to_topic_id}"
            break_times_data[key] = record.break_minutes
        
        app.logger.info(f'Retrieved break times for subject {subject_id}: {len(break_times_data)} entries')
        app.logger.debug(f'Break times data: {break_times_data}')
        
        return jsonify({
            'break_times': break_times_data,
            'subject_id': subject_id
        })
    except Exception as e:
        app.logger.error(f'Error getting break times: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/groups', methods=['GET'])
@login_required
def get_user_groups():
    """Get all groups a user is a member of."""
    try:
        # Try to get groups with new schema first
        try:
            user_groups = db.session.query(StudyGroup).join(GroupMember).filter(
                GroupMember.user_id == current_user.id
            ).all()
        except Exception as schema_error:
            # If new schema fails, try with old schema and basic data
            user_groups = db.session.execute(
                'SELECT id, name, created_by, created_at FROM study_group WHERE id IN '
                '(SELECT group_id FROM group_member WHERE user_id = ?)',
                (current_user.id,)
            ).fetchall()
            
            # Convert to basic format
            groups_data = []
            for group in user_groups:
                groups_data.append({
                    'id': group[0],
                    'name': group[1],
                    'creator': 'Unknown',
                    'created_at': group[3] if group[3] else 'Unknown',
                    'description': '',
                    'subject': 'General',
                    'is_private': False,
                    'member_count': 1,
                    'code': f'group-{group[0]}'  # Simple fallback code
                })
            
            return jsonify({
                'success': True,
                'groups': groups_data,
                'message': 'Using compatibility mode - please update database'
            })
        
        # Format the response with new schema
        groups_data = []
        for group in user_groups:
            # Get the creator's username
            creator = User.query.get(group.created_by)
            creator_name = creator.username if creator else "Unknown"
            
            # Get the number of members
            member_count = GroupMember.query.filter_by(group_id=group.id).count()
              # Use stored code or generate if missing
            group_code = getattr(group, 'code', None) or f'group-{group.id}'
            if hasattr(group, 'code') and not group.code:
                group.code = generate_group_code()
                db.session.commit()
            
            groups_data.append({
                'id': group.id,
                'name': group.name,
                'creator': creator_name,
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S') if group.created_at else 'Unknown',
                'description': getattr(group, 'description', '') or '',
                'subject': getattr(group, 'subject', 'General') or 'General',
                'is_private': getattr(group, 'is_private', False) or False,
                'member_count': member_count,
                'code': group_code,
                'is_creator': group.created_by == current_user.id
            })
        
        return jsonify({
            'success': True,
            'groups': groups_data
        })
    except Exception as e:
        app.logger.error(f"Error getting groups: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting groups: {str(e)}"
        }), 500


@app.route('/api/groups', methods=['POST'])
@login_required
def create_group_api():
    """Create a new study group."""
    try:
        data = request.json
          # Create the group with generated code
        group_code = generate_group_code()
        group = StudyGroup(
            name=data.get('name'),
            created_by=current_user.id,
            description=data.get('description', ''),
            subject=data.get('subject', ''),
            is_private=data.get('is_private', False),
            code=group_code
        )
        db.session.add(group)
        db.session.flush()  # Get the group ID without committing
        
        # Add creator as a member
        member = GroupMember(
            user_id=current_user.id,
            group_id=group.id
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Group created successfully',
            'group': {
                'id': group.id,
                'name': group.name,
                'code': group_code
            }
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating group: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error creating group: {str(e)}"
        }), 500


@app.route('/api/groups/join', methods=['POST'])
@login_required
def join_group():
    """Join a study group using a code."""
    try:
        data = request.json
        code = data.get('code')
        
        if not code:
            return jsonify({
                'success': False,
                'message': 'Group code is required'
            }), 400
          # Find the group by code
        group = StudyGroup.query.filter_by(code=code).first()
        if not group:
            return jsonify({
                'success': False,
                'message': 'Group not found'
            }), 404
        
        # Check if user is already a member
        existing_member = GroupMember.query.filter_by(
            user_id=current_user.id, 
            group_id=group.id
        ).first()
        
        if existing_member:
            return jsonify({
                'success': True,
                'message': 'You are already a member of this group',
                'group_id': group.id
            })        # Add user as member
        member = GroupMember(
            user_id=current_user.id,
            group_id=group.id
        )
        db.session.add(member)
        db.session.commit()
        
        # Get updated member count
        updated_member_count = GroupMember.query.filter_by(group_id=group.id).count()
        
        # Emit real-time event to update member count for all users in the group
        # This includes both chat room and groups page listeners
        socketio.emit('user_joined', {
            'group_id': group.id,
            'username': current_user.username,
            'member_count': updated_member_count
        }, room=f'group_{group.id}')
        
        # Also emit to a general room that groups page can listen to
        socketio.emit('group_updated', {
            'group_id': group.id,
            'type': 'member_joined',
            'username': current_user.username,
            'member_count': updated_member_count
        })
        
        return jsonify({
            'success': True,
            'message': f'Successfully joined {group.name}',
            'group_id': group.id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error joining group: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error joining group: {str(e)}"        }), 500


@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Delete a study group (only the creator can delete)."""
    # Check authentication for API requests
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
    
    try:
        # Find the group
        group = StudyGroup.query.get(group_id)
        if not group:
            return jsonify({
                'success': False,
                'message': 'Group not found'
            }), 404
        
        # Check if current user is the creator
        if group.created_by != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Only the group creator can delete this group'
            }), 403
        
        # Delete all group members first
        GroupMember.query.filter_by(group_id=group_id).delete()
        
        # Delete
        try:
            GroupMessage.query.filter_by(group_id=group_id).delete()
        except:
            # Table might not exist yet, that's okay
            pass
          # Delete the group
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Group deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting group: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error deleting group: {str(e)}"
        }), 500


@app.route('/api/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    """Leave a study group."""
    try:
        # Check if user is a member of this group
        member = GroupMember.query.filter_by(
            user_id=current_user.id, 
            group_id=group_id
        ).first()
        
        if not member:
            return jsonify({
                'success': False,
                'message': 'You are not a member of this group'
            }), 404
        
        # Get group info before leaving
        group = StudyGroup.query.get(group_id)
        if not group:
            return jsonify({
                'success': False,
                'message': 'Group not found'
            }), 404
        
        # Check if user is the group creator
        if group.created_by == current_user.id:
            # Check if there are other members
            other_members = GroupMember.query.filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id != current_user.id
            ).all()
            
            if other_members:
                # Transfer ownership to the next member (first one who joined)
                next_owner = other_members[0]
                group.created_by = next_owner.user_id
                db.session.commit()
        
        # Remove the member
        db.session.delete(member)
        db.session.commit()
        
        # Get updated member count
        updated_member_count = GroupMember.query.filter_by(group_id=group_id).count()
        
        # If no members left, delete the group
        if updated_member_count == 0:
            # Delete all messages first
            GroupMessage.query.filter_by(group_id=group_id).delete()
            # Delete the group
            db.session.delete(group)
            db.session.commit()
        else:
            # Emit real-time event to update member count
            socketio.emit('user_left', {
                'group_id': group_id,
                'username': current_user.username,
                'member_count': updated_member_count
            }, room=f'group_{group_id}')
        
        return jsonify({
            'success': True,
            'message': f'Successfully left {group.name}',
            'group_deleted': updated_member_count == 0
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error leaving group: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error leaving group: {str(e)}"
        }), 500


@app.route('/api/groups/<int:group_id>/members', methods=['GET'])
@login_required
def get_group_members(group_id):
    # Check if the user is a member of this group
    is_member = GroupMember.query.filter_by(
        user_id=current_user.id, 
        group_id=group_id
    ).first()
    
    if not is_member:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Get all members
    members_data = []
    members = db.session.query(User, GroupMember).join(GroupMember).filter(
        GroupMember.group_id == group_id
    ).all()
    
    for user, member in members:
        members_data.append({
            'id': user.id,
            'username': user.username,
            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
            'is_owner': StudyGroup.query.get(group_id).created_by == user.id
        })
    
    return jsonify({'success': True, 'members': members_data})


@app.route('/api/groups/<int:group_id>/messages', methods=['GET'])
@login_required
def get_group_messages(group_id):
    # Check if the user is a member of this group
    is_member = GroupMember.query.filter_by(
        user_id=current_user.id, 
        group_id=group_id
    ).first()
    
    if not is_member:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Get recent messages (limit to 100 most recent)
    messages = db.session.query(GroupMessage, User).join(User).filter(
        GroupMessage.group_id == group_id
    ).order_by(GroupMessage.timestamp.desc()).limit(100).all()
    
    messages_data = []
    for message, user in messages:
        messages_data.append({
            'id': message.id,
            'message': message.message,
            'username': user.username,
            'user_id': user.id,
            'timestamp': message.timestamp.isoformat() if message.timestamp else '',
            'is_current_user': user.id == current_user.id
        })
    
    # Return in chronological order (oldest first)
    messages_data.reverse()
    
    return jsonify({'success': True, 'messages': messages_data})


@app.route('/groups/<int:group_id>/chat')
@login_required
def group_chat(group_id):
    """Render the group chat page."""
    # Check if user is a member of the group
    is_member = GroupMember.query.filter_by(
        user_id=current_user.id, 
        group_id=group_id
    ).first()
    
    if not is_member:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get the group
    group = StudyGroup.query.get_or_404(group_id)
      # Get the number of members
    member_count = GroupMember.query.filter_by(group_id=group.id).count()
    
    # Add additional fields to group object
    group.member_count = member_count
    
    return render_template('group_chat.html', group=group)
    

@app.route('/groups/debug')
@login_required
def groups_debug():
    return render_template('groups_debug.html')
    

@app.route('/admin/fix-database')
def fix_database():
    """Admin route to fix database schema"""
    results = []
    
    try:
        # Use proper SQLAlchemy text() for raw SQL
        from sqlalchemy import text
        
        # Add missing columns one by one
        try:
            db.session.execute(text('ALTER TABLE study_group ADD COLUMN description TEXT DEFAULT ""'))
            db.session.commit()
            results.append("✅ Added description column")
        except Exception as e:
            results.append(f"Description column: {str(e)}")
        
        try:
            db.session.execute(text('ALTER TABLE study_group ADD COLUMN subject TEXT DEFAULT "General"'))
            db.session.commit()
            results.append("✅ Added subject column")
        except Exception as e:
            results.append(f"Subject column: {str(e)}")
        
        try:
            db.session.execute(text('ALTER TABLE study_group ADD COLUMN is_private BOOLEAN DEFAULT 0'))
            db.session.commit()
            results.append("✅ Added is_private column")
        except Exception as e:
            results.append(f"is_private column: {str(e)}")
        
        try:
            db.session.execute(text('ALTER TABLE study_group ADD COLUMN code TEXT'))
            db.session.commit()
            results.append("✅ Added code column")
        except Exception as e:
            results.append(f"Code column: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Database schema update completed!',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during database update: {str(e)}',
            'results': results
        })


def auto_fix_database_schema():
    """Automatically fix database schema on startup"""
    try:
        # Silently check and fix database schema
        from sqlalchemy import text
        
        # Add missing columns one by one
        columns_to_add = [
            ('description', 'TEXT DEFAULT ""'),
            ('subject', 'TEXT DEFAULT "General"'),
            ('is_private', 'BOOLEAN DEFAULT 0'),
            ('code', 'TEXT')
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                sql = f'ALTER TABLE study_group ADD COLUMN {col_name} {col_def}'
                db.session.execute(text(sql))
                db.session.commit()
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    # Only print if it's an unexpected error
                    print(f"⚠️ Error adding {col_name}: {e}")
        
        # Create unique index for code column
        try:
            db.session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS idx_study_group_code ON study_group(code)'))
            db.session.commit()
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"⚠️ Index creation: {e}")
        
    except Exception as e:
        print(f"❌ Error during schema fix: {e}")


@app.route('/test-ui')
def test_ui():
    """Test route to verify the new beautiful UI styling"""
    return render_template('test_ui.html')


@app.route('/api/groups/<int:group_id>/debug')
@login_required
def debug_group(group_id):
    """Debug endpoint to check group state."""
    group = StudyGroup.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group_id).all()
    member_users = []
    
    for member in members:
        user = User.query.get(member.user_id)
        member_users.append({
            'id': user.id,
            'username': user.username,
            'joined_at': member.joined_at.isoformat() if member.joined_at else None
        })
    
    return jsonify({
        'group': {
            'id': group.id,
            'name': group.name,
            'code': group.code,
            'created_by': group.created_by

        },
        'members': member_users,
        'member_count': len(member_users),
        'current_user_is_member': any(m.user_id == current_user.id for m in members)
    })


@app.route('/connection-test')
def connection_test():
    """Test page to verify cross-device connectivity"""
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Intelliplan Connection Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .info {{ color: #17a2b8; }}
            .warning {{ color: #ffc107; }}
            .error {{ color: #dc3545; }}
            .test-item {{ margin: 15px 0; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa; }}
            button {{ background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            #socketStatus {{ font-weight: bold; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Intelliplan Connection Test</h1>
            
            <div class="test-item">
                <h3 class="success">✅ Flask Server Status</h3>
                <p>Server is running and responding to HTTP requests.</p>
            </div>
            
            <div class="test-item">
                <h3 class="info">🌐 Network Information</h3>
                <p><strong>Server Hostname:</strong> {hostname}</p>
                <p><strong>Server IP:</strong> {local_ip}</p>
                <p><strong>Your IP:</strong> {request.remote_addr}</p>
                <p><strong>Access URL:</strong> http://{local_ip}:5000</p>
            </div>
            
            <div class="test-item">
                <h3>🔌 Socket.IO Connection Test</h3>
                <p>Status: <span id="socketStatus" class="warning">Testing...</span></p>
                <button onclick="testSocket()">Test Socket.IO Connection</button>
            </div>
            
            <div class="test-item">
                <h3>📱 Cross-Device Instructions</h3>
                <ol>
                    <li>Ensure all devices are on the same WiFi network</li>
                    <li>On other devices, visit: <strong>http://{local_ip}:5000</strong></li>
                    <li>If this page loads, HTTP connectivity works</li>
                    <li>Test group chat to verify Socket.IO works</li>
                </ol>
            </div>
            
            <div class="test-item">
                <h3>🛠️ Troubleshooting</h3>
                <ul>
                    <li>Check Windows Firewall settings</li>
                    <li>Verify all devices on same network</li>
                    <li>Try different port if 5000 is blocked</li>
                    <li>Check router settings for device isolation</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="text-decoration: none;">
                    <button>Go to Intelliplan Main App</button>
                </a>
            </div>
        </div>
        
        <script>
            let socket;
            let testInProgress = false;
            
            function testSocket() {{
                if (testInProgress) return;
                testInProgress = true;
                
                const statusEl = document.getElementById('socketStatus');
                statusEl.textContent = 'Connecting...';
                statusEl.className = 'warning';
                
                try {{
                    socket = io({{
                        forceNew: true,
                        timeout: 5000,
                        transports: ['polling', 'websocket']
                    }});
                    
                    socket.on('connect', function() {{
                        statusEl.textContent = '✅ Connected Successfully!';
                        statusEl.className = 'success';
                        testInProgress = false;
                        
                        // Test a simple message
                        socket.emit('test_message', 'Hello from connection test');
                    }});
                    
                    socket.on('disconnect', function() {{
                        statusEl.textContent = '❌ Disconnected';
                        statusEl.className = 'error';
                        testInProgress = false;
                    }});
                    
                    socket.on('connect_error', function(error) {{
                        statusEl.textContent = '❌ Connection Failed: ' + error;
                        statusEl.className = 'error';
                        testInProgress = false;
                    }});
                    
                    // Timeout after 10 seconds
                    setTimeout(() => {{
                        if (testInProgress) {{
                            statusEl.textContent = '⏰ Connection Timeout';
                            statusEl.className = 'error';
                            testInProgress = false;
                            if (socket) socket.disconnect();
                        }}
                    }}, 10000);
                    
                }} catch (error) {{
                    statusEl.textContent = '❌ Error: ' + error.message;
                    statusEl.className = 'error';
                    testInProgress = false;
                }}
            }}
            
            // Auto-test on page load
            window.onload = function() {{
                setTimeout(testSocket, 1000);
            }};
        </script>
    </body>
    </html>
    """
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Automatically fix database schema
        auto_fix_database_schema()
    
    # Configure for cross-device connectivity
    # Use host='0.0.0.0' to allow connections from other devices on the network
    # Use port=5000 or any available port
    socketio.run(
        app, 
        host='0.0.0.0',  # This allows connections from other devices
        port=5000,       # Standard Flask port
        debug=True,
        allow_unsafe_werkzeug=True  # For development only
    )