from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=True)
    
    nom = db.Column(db.String(100))        # Ajouté
    pseudo = db.Column(db.String(100))     # Ajouté
    photo = db.Column(db.String(200))      # Chemin du fichier image
    telephone = db.Column(db.String(20))   # Ajouté

    posts = db.relationship('Post', back_populates='user')
    likes = db.relationship('Like', back_populates='user', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete-orphan")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contenu = db.Column(db.Text, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.String(300), nullable=False)
    image_url = db.Column(db.String(150), nullable=True)
    video_url = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='posts')

    # Relations avec Likes et Comments
    likes = db.relationship('Like', back_populates='post', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='post', cascade="all, delete-orphan")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', back_populates='likes')
    user = db.relationship('User', back_populates='likes')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contenu = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

   
