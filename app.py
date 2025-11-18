from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Proposal
import os

# Define o caminho absoluto da pasta static
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder_path = os.path.join(current_dir, 'static')

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder=static_folder_path
)

# Chave secreta (substitua por uma forte em produção)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# 🔴 FORÇANDO o uso do PostgreSQL do Render
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://proposta_db_user:gHAfGxaMNp0FZe1eT2sK16Wwvh4r7V6u@'
    'dpg-d4do0lbuibrs73dpf0f0-a.oregon-postgres.render.com/proposta_db'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def setup():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123', is_admin=True)
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('proposals'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
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
    user_id = session['user_id']
    proposals = Proposal.query.filter_by(user_id=user_id).all()
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
    proposals = db.session.query(Proposal, User.username)\
                          .join(User, Proposal.user_id == User.id)\
                          .all()
    return render_template('admin_all.html', proposals=proposals)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)