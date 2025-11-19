from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-muito-segura'  # mude depois
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///propostas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === Modelos ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    commission_default = db.Column(db.Float, default=0.0)

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    proposta = db.Column(db.String(100), nullable=False)
    parcela = db.Column(db.Integer, nullable=False)
    banco = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    comissao = db.Column(db.Float, nullable=False)

# === Cria banco e admin ao iniciar ===
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)
        db.session.commit()

# === Rotas ===
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('proposals'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/proposals')
def proposals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    proposals = Proposal.query.filter_by(user_id=session['user_id']).all()
    return render_template('proposals.html', proposals=proposals)

@app.route('/add_proposal', methods=['GET', 'POST'])
def add_proposal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        p = Proposal(
            user_id=session['user_id'],
            proposta=request.form['proposta'],
            parcela=int(request.form['parcela']),
            banco=request.form['banco'],
            valor=float(request.form['valor']),
            tipo=request.form['tipo'],
            comissao=float(request.form['comissao'])
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('proposals'))
    return render_template('add_proposal.html')

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect(url_for('proposals'))
    users = User.query.all()
    return render_template('register_user.html', users=users)

@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    username = request.form['username']
    password = request.form['password']
    commission = float(request.form.get('commission', 0.0))
    if User.query.filter_by(username=username).first():
        flash('Usuário já existe')
    else:
        user = User(username=username, password=password, commission_default=commission)
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/all')
def admin_all():
    if not session.get('is_admin'):
        return redirect(url_for('proposals'))
    proposals = db.session.query(Proposal, User.username).join(User).all()
    return render_template('admin_all.html', proposals=proposals)

if __name__ == '__main__':
    app.run(debug=True)