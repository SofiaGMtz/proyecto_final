from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models.users import User
from .models.questions import Question
from .models.answers import Answer
from .models.votes import Vote
from sqlalchemy import desc

main = Blueprint('main', __name__)

@main.route('/')
def index():
    secret_key = current_app.config['SECRET_KEY']
    recent_questions = Question.query.order_by(Question.created_at.desc()).limit(8).all()
    return render_template('index.html', recent_questions=recent_questions)

@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        flash('Por favor, ingresa un término de búsqueda.', 'warning')
        return redirect(url_for('main.questions'))

    search_results = Question.query.filter(
        (Question.title.ilike(f'%{query}%')) |
        (Question.content.ilike(f'%{query}%'))
    ).order_by(Question.created_at.desc()).all()
    
    return render_template('search_results.html', query=query, questions=search_results)

@main.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        user = User.get_user_by_email(email=email)
        
        if user is not None:
            flash('Correo ya registrado')
            print('Correo ya registrado')
        
        elif not username or not email or not password:
            flash('Faltan campos por llenar')
            print('Hay campos vacíos')

        else:
            nuevo_usuario = User(username=username, email=email)
            nuevo_usuario.set_password(password=password)
            nuevo_usuario.save()

            login_user(nuevo_usuario)

            print('Nuevo usuario creado y sesión iniciada')
            print(f'''
                Nombre: {username}
                Correo: {email}
                Contraseña: {password}
            ''')
            return redirect(url_for('main.index'))

    return render_template('/auth/register.html')

@main.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        user = User.get_user_by_email(email=email)

        if user and user.check_password(password=password):
            login_user(user)
            print('Nuevo inicio de sesión')
            print(f'''
                Correo: {email}
                Contraseña: {password}
            ''')
            return redirect(url_for('main.index'))
        
        elif not email or not password: 
            flash('Faltan campos por llenar')
            print('Hay campos vacíos')

        else:
            flash('Correo o contraseña incorrectos')
            print('Correo o contraseña incorrectos')

    return render_template('/auth/login.html')

@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión con éxito')
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        
        if new_username:
            current_user.username = new_username
            current_user.save() 

            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Nombre de usuario no puede estar vacío', 'error')
    
    return render_template('profile.html')

@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('username')
    
    if new_username:
        current_user.username = new_username
        current_user.save()

        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('main.profile'))
    else:
        flash('Nombre de usuario no puede estar vacío', 'error')
        return redirect(url_for('main.profile'))

@main.route('/questions')
def questions():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    questions_pagination = Question.query.order_by(Question.created_at.desc()).paginate(page=page, per_page=per_page)
    
    questions_info = []
    for question in questions_pagination.items:
        answers_count = len(question.answers)
        likes_count = sum(1 if vote.is_upvote else -1 for answer in question.answers for vote in answer.votes)  # Contar likes incluyendo negativos
        questions_info.append({
            'question': question,
            'answers_count': answers_count,
            # 'likes_count': likes_count
        })
    
    return render_template('questions/questions.html', questions_info=questions_info, pagination=questions_pagination)

@main.route('/questions/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        print(f'Título: {title}, Contenido: {content}') 

        if not title or not content:
            flash('Todos los campos son obligatorios', 'warning')
            print('no se manda nada')
            return redirect(url_for('main.ask_question'))

        question = Question(title=title, content=content, user_id=current_user.id)
        question.save()
        print('Pregunta enviada con éxito')
        flash('Pregunta enviada con éxito', 'success')
        return redirect(url_for('main.questions'))

    return render_template('questions/ask_question.html')

@main.route('/questions/<int:question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    question = Question.query.get_or_404(question_id)

    user_votes = {}
    if current_user.is_authenticated:
        user_votes = {vote.answer_id: vote.is_upvote for vote in current_user.votes}

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Por favor inicia sesión para enviar una respuesta.', 'warning')
            return redirect(url_for('main.login'))

        content = request.form.get('content')
        if not content:
            flash('El contenido de la respuesta no puede estar vacío.', 'warning')
        else:
            answer = Answer(content=content, question_id=question_id, user_id=current_user.id)
            answer.save()
            flash('Respuesta enviada con éxito.', 'success')
        return redirect(url_for('main.view_question', question_id=question_id))
    
    return render_template('questions/view_question.html', question=question, user_votes=user_votes)

@main.route('/vote/<int:answer_id>/<action>', methods=['POST'])
def vote(answer_id, action):
    if not current_user.is_authenticated:
        flash('Por favor inicia sesión para votar.', 'warning')
        return redirect(url_for('main.login'))
    
    answer = Answer.query.get_or_404(answer_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.id, answer_id=answer_id).first()

    if existing_vote:
        if existing_vote.is_upvote and action == 'dislike':
            existing_vote.is_upvote = False
            existing_vote.save()
        elif not existing_vote.is_upvote and action == 'like':
            existing_vote.is_upvote = True
            existing_vote.save()
        else:
            existing_vote.delete_vote()
    else:
        is_upvote = (action == 'like')
        vote = Vote(user_id=current_user.id, answer_id=answer_id, is_upvote=is_upvote)
        vote.save()

    return redirect(url_for('main.view_question', question_id=answer.question_id))