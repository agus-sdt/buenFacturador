from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.usuario import Usuario
from datetime import datetime, timezone


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password) and usuario.is_active():
            usuario.ultimo_acceso = datetime.now(timezone.utc)
            db.session.commit()

            login_user(usuario, remember=remember)
            flash(f'Bienvenido {usuario.nombre}!', 'succes')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        terminos = request.form.get('terminos')

        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')

        if not all([nombre, email, password]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/register.html')
        
        if not terminos:
            flash('Debes aceptar los terminos y condiciones', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('La contrasea debe tener al menos 6 caracteres', 'error')
            return render_template('auth/register.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ya esta registrado', 'error')
            return render_template('auth/register.html')
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email
        )
        nuevo_usuario.set_password(password)

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('registro exitoso! ahora puede iniciar sesion', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'error al crea la cuenta. intenta nuevamente {e}', 'error')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('has cerrado sesion correctamente', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods = ['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash('Por favor ingresa tu email', 'error')
            return render_template('auth/forgot_password.html')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            flash('Si el email existe, recibirás un enlace de recuperación', 'info')
        else:
            flash('Si el email existe, recibirás un enlace de recuperación', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')