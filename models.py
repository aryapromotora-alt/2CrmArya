from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    commission_default = db.Column(db.Float, default=0.0)  # comissão padrão do usuário

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    proposta = db.Column(db.String(100), nullable=False)
    parcela = db.Column(db.Integer, nullable=False)
    banco = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # novo, refin, etc.
    comissao = db.Column(db.Float, nullable=False)    # pode ser diferente por proposta