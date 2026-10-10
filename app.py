from flask import Flask, render_template, url_for, request, redirect, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db
from models import User, QuestionHistory, UnansweredQuestion, ContactQuery
from utils.rag_pipeline import rag_answer

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.secret_key='secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)

with app.app_context():
        db.create_all()


@app.route('/')
def home():
        return render_template('home.html') 

def login_required(f):
        @wraps(f)
        def decorated(*args,**kwargs):
                if 'user_id' not in session:
                        flash('Please login to access this page','error')
                        return redirect(url_for('signin'))
                return f(*args,**kwargs)
        return decorated

def admin_required(f):
        @wraps(f)
        def decorated(*args,**kwargs):
                if 'user_id' not in session:
                        flash('Please login to access this page','error')
                        return redirect(url_for('signin'))
                user = User.query.get(session['user_id'])
                if not user or not user.is_admin:
                        flash('Admin access required','error')
                        return redirect(url_for('home'))
                return f(*args,**kwargs)
        return decorated


@app.route('/signin',methods=['GET','POST'])    #login page
def signin():
        if request.method=='POST':
                email=request.form['email']
                password=request.form['password']
                user=User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password,password):
                        session['user_id']=user.id
                        session['user_name']=user.name
                        flash('Signin successful','success')
                        return redirect(url_for('home'))
        return render_template('signin.html')


@app.route('/signup',methods=['GET','POST'])    #register page
def signup():
        if request.method=='POST':
                name=request.form['name']
                email=request.form['email']
                password=request.form['password']
                confirm_password=request.form['confirm_password']

                if not name or len(name.strip())<2:
                        flash('name must be atleast 2 character long','error')
                        return redirect(url_for('signup'))
                if not email or '@' not in email :
                        flash('Invalid email','error')
                        return redirect(url_for('signup'))
                if not password or len(password)<8 or not any(char.isalpha() for char in password ) or not any(char.isdigit() for char in password) or not any (not char.isalnum() for char in password):
                        flash('pass must be atleast 8 char long and contain letters and contain numbers and special characters','error')
                        return redirect(url_for('signup'))
                if confirm_password!=password:
                        flash('Confirm password should match password','error')
                        return redirect(url_for('signup'))
                #check if user already exists
                existing_user=User.query.filter_by(email=email).first()
                if existing_user:
                        flash('Email already exists.Please login. ','error')
                        return redirect(url_for('signup'))
                # generate hash password
                hashed_password=generate_password_hash(password)
                is_admin = (email.strip().lower() == 'admin@nyayagpt.com')
                new_user=User(
                        name=name.strip(),
                        email=email.strip(),
                        password=hashed_password,
                        is_admin=is_admin
                )
                try:
                        db.session.add(new_user)
                        db.session.commit()
                        flash('Registration successful .Proceed to signin','success')
                        return redirect(url_for('signin'))
                except Exception as e:
                        db.session.rollback()
                        flash('Some error occured while registering','error')
                        return redirect(url_for('signup'))

        return render_template('signup.html')

@app.route('/rag', methods=['GET', 'POST'])
def rag_assistant():
    answer = None
    sources = []

    if request.method == "POST":
        query = request.form.get("query")
        sector = request.form.get("sector")
        
        # Get year range from frontend slider
        start_year = request.form.get("start_year", 1950)
        end_year = request.form.get("end_year", 2025)
        
        try:
            start_year = int(start_year)
            end_year = int(end_year)
        except (ValueError, TypeError):
            start_year, end_year = 1950, 2025

        # Pass the current logged-in user's id and year range into the RAG pipeline
        user_id = session.get('user_id')
        try:
            result = rag_answer(query, sector, start_year=start_year, end_year=end_year, user_id=user_id)
            answer = result["answer"]
            sources = result["sources"]
        except FileNotFoundError as fnfe:
            flash(str(fnfe), "warning")
            answer = "Sorry, the legal database for this sector is currently being indexed. Please try again in a few minutes."
            sources = []
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            answer = "An error occurred while processing your request."
            sources = []

    return render_template(
        "rag.html",
        answer=answer,
        sources=sources,
        start_year=request.form.get("start_year", 1950), # Preserve values for UI
        end_year=request.form.get("end_year", 2025)
    )

@app.route('/history')
@login_required
def get_history():
    user_id = session.get('user_id')
    history = QuestionHistory.query.filter_by(user_id=user_id).order_by(QuestionHistory.timestamp.desc()).all()
    
    return [{
        "question": h.question,
        "sector": h.sector,
        "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for h in history]

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash('Name, email, and message are required', 'error')
            return redirect(url_for('contact'))
            
        new_query = ContactQuery(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        try:
            db.session.add(new_query)
            db.session.commit()
            flash('Your query has been submitted successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your query', 'error')
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    user_queries = ContactQuery.query.order_by(ContactQuery.timestamp.desc()).all()
    unanswered_questions = UnansweredQuestion.query.order_by(UnansweredQuestion.timestamp.desc()).all()
    
    return render_template('admin.html', user_queries=user_queries, unanswered_questions=unanswered_questions)

if __name__=='__main__':
        app.run(debug=True,port=5001 )  