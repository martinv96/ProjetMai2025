from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    nom = db.Column(db.String(100))        # Ajouté
    pseudo = db.Column(db.String(100))     # Ajouté
    photo = db.Column(db.String(200))      # Chemin du fichier image
    telephone = db.Column(db.String(20))   # Ajouté


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
