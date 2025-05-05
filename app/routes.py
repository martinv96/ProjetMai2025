from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Message, db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

bp = Blueprint('main', __name__)

# Fonction utilitaire
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

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
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.profile'))

    return render_template("login.html")

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        field_modified = request.form.get('field_modified')

        if field_modified == 'nom':
            current_user.nom = request.form.get('nom')
        elif field_modified == 'prenom':
            current_user.prenom = request.form.get('prenom')
        elif field_modified == 'pseudo':
            current_user.pseudo = request.form.get('pseudo')
        elif field_modified == 'telephone':
            current_user.telephone = request.form.get('telephone')
        elif field_modified == 'email':
            current_user.email = request.form.get('email')
        elif field_modified == 'new_password':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('new_password_confirm')
            if new_password and new_password == confirm_password:
                hashed_password = generate_password_hash(new_password, method='sha256')
                current_user.password = hashed_password

        # Photo de profil
        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.photo = f'uploads/{filename}'

        db.session.commit()
        return redirect(url_for('main.profile'))

    return render_template("profile.html", user=current_user)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/messages')
@login_required
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
