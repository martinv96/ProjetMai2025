from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, Message, Post, db, Like, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import cloudinary.uploader
from io import BytesIO
import os

bp = Blueprint('main', __name__)

# Fonction utilitaire
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


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
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(prenom=prenom, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
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
            flash("Connexion réussie !", "success")
            return redirect(url_for('main.profile'))
        else:
            flash("Identifiants incorrects. Veuillez réessayer.", "danger")

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
            else:
                flash("Les mots de passe ne correspondent pas.", "danger")

        # Photo de profil
        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.photo = f'uploads/{filename}'

        db.session.commit()
        flash("Profil mis à jour avec succès !", "success")
        return redirect(url_for('main.profile'))

    return render_template("profile.html", user=current_user)



@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('main.login'))

@bp.route('/messages')
@login_required
def view_messages():
    if current_user.role != 'admin':
        flash("Accès réservé à l'administrateur.", "warning")
        return redirect(url_for('main.index'))  # ou une autre page d'accueil
    messages = Message.query.all()
    return render_template("messages_reçus.html", messages=messages)


@bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('main.view_messages'))


@bp.route('/partage', methods=['GET', 'POST'])
@login_required
def partage():
    if request.method == 'POST':
        contenu = request.form.get('contenu')[:300]
        image = request.files.get('image')
        video = request.files.get('video')

        image_url = None
        video_url = None

        # Upload image (si présente)
        if image and allowed_file(image.filename):
            try:
                result = cloudinary.uploader.upload(
                    image,
                    resource_type="image"
                )
                image_url = result.get("secure_url")
            except Exception as e:
                flash(f"Erreur lors de l'envoi de l'image : {str(e)}", "danger")
                return redirect(url_for('main.partage'))

        # Upload vidéo (si présente)
        if video and allowed_file(video.filename):
            try:
                # Ouvrir le fichier vidéo en mode binaire
                video_bytes = BytesIO(video.read())  # Lecture du fichier comme bytes
                result = cloudinary.uploader.upload_large(
                    video_bytes,
                    resource_type="video"
                )
                video_url = result.get("secure_url")
            except Exception as e:
                flash(f"Erreur lors de l'envoi de la vidéo : {str(e)}", "danger")
                return redirect(url_for('main.partage'))

        # Création du post
        new_post = Post(contenu=contenu, image_url=image_url, video_url=video_url, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash("Post publié avec succès !", "success")
        return redirect(url_for('main.feed'))

    return render_template("partage.html")


@bp.route('/feed')
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("feed.html", posts=posts)

@bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)

    # Vérifier si l'utilisateur a déjà liké ce post
    existing_like = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    if existing_like:
        db.session.delete(existing_like)  # Si oui, on supprime le like
    else:
        new_like = Like(post_id=post.id, user_id=current_user.id)
        db.session.add(new_like)  # Sinon, on ajoute un nouveau like

    db.session.commit()
    return redirect(url_for('main.feed'))

@bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    contenu = request.form.get('contenu')

    if contenu:
        new_comment = Comment(contenu=contenu, post_id=post.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for('main.feed'))

@bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Vérification si l'utilisateur est celui qui a posté le commentaire
    if comment.user_id == current_user.id:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('main.feed'))  # Ou la page où vous affichez les posts
    else:
        return redirect(url_for('main.feed'))  # Ou une page d'erreur si nécessaire
    
@bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user.id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash('Post supprimé avec succès', 'success')
    else:
        flash('Vous n\'êtes pas autorisé à supprimer ce post', 'danger')
    return redirect(url_for('main.feed'))

@bp.route('/create-tables')
def create_tables():
    # Créer toutes les tables
    from app import db
    db.create_all()

    # Vérifier si l'utilisateur admin existe déjà pour éviter les doublons
    if not User.query.filter_by(email='martinv9663@gmail.com').first():
        # Créer un utilisateur avec les données spécifiées
        hashed_password = generate_password_hash('azerty', method='pbkdf2:sha256')
        admin_user = User(
            prenom='Martin', 
            email='martinv9663@gmail.com', 
            password=hashed_password, 
            role='admin'  # Attribuer le rôle 'admin'
        )
        
        # Ajouter l'utilisateur à la base de données
        db.session.add(admin_user)
        db.session.commit()

    return "Tables créées et utilisateur admin ajouté (si nécessaire)"
