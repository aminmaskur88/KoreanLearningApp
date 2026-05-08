from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@views_bp.route('/hangul')
def hangul():
    return render_template('hangul.html')

@views_bp.route('/vocabulary')
def vocabulary():
    return render_template('vocabulary.html')

@views_bp.route('/flashcards')
def flashcards():
    return render_template('flashcards.html')

@views_bp.route('/quiz')
def quiz():
    return render_template('quiz.html')

@views_bp.route('/lesson/intro')
def lesson_intro():
    return render_template('lesson_intro.html')

@views_bp.route('/session/<category>')
def session(category):
    return render_template('session.html', category=category)
