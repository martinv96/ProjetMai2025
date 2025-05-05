from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Message, db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template("index.html")

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        message = request.form.get('message')

        nouveau_message = Message(prenom=prenom, email=email, contenu=message)
        db.session.add(nouveau_message)
        db.session.commit()

        return render_template("merci.html", prenom=prenom)

    return render_template("contact.html")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(prenom=prenom, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template("register.html")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Vérifie si l'utilisateur est déjà connecté
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))  # Rediriger vers la page de profil si l'utilisateur est déjà connecté

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifie si l'utilisateur existe et si le mot de passe est correct
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # Connexion de l'utilisateur
            return redirect(url_for('main.profile'))  # Rediriger vers la page de profil après la connexion

    return render_template("login.html")  # Affiche le formulaire de connexion si la méthode est GET ou si les informations sont invalides

@bp.route('/profile')
@login_required
def profile():
    return render_template("profile.html", prenom=current_user.prenom)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/messages')
@login_required  # Optionnel, selon si tu veux que seuls les utilisateurs connectés y accèdent
def view_messages():
    messages = Message.query.all()
    return render_template("messages_reçus.html", messages=messages)

@bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('main.view_messages'))
