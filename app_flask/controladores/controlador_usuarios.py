from flask import render_template, request, redirect, session, flash
from app_flask.modelos.modelo_arboles import Arbol
from app_flask.modelos.modelo_usuarios import Usuario
from app_flask import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
#app.route 'aqui va el link donde fue redireccionado el usuario'
@app.route('/', methods=['GET'])
def despliega_login_registro():
    return render_template('login_registro.html') #aqui donde ira el usuario

@app.route('/procesa/registro', methods=['POST'])
def procesa_registro():
    datos_registro = {
        "nombre": request.form.get('nombre', ''),
        "apellido": request.form.get('apellido', ''),
        "email": request.form.get('email', ''),
        "password": request.form.get('password', ''),
        "password_confirmar": request.form.get('password_confirmar', '')
    }

    if not Usuario.validar_registro(datos_registro):
        return redirect('/')

    password_encriptado = bcrypt.generate_password_hash(datos_registro['password'])
    nuevo_usuario = {
        **datos_registro,
        'password': password_encriptado
    }
    id_usuario = Usuario.crear_uno(nuevo_usuario)

    session['id_usuario'] = id_usuario
    session['nombre'] = nuevo_usuario['nombre']
    session['apellido'] = nuevo_usuario['apellido']

    return redirect('/dashboard')

@app.route('/procesa/login', methods=['POST'])
def procesa_login():
    usuario_login = Usuario.obtener_uno({"email": request.form.get('email', '')})

    if usuario_login is None:
        flash('Este correo no existe', 'error_login')
        return redirect('/')

    if not bcrypt.check_password_hash(usuario_login.password, request.form.get('password', '')):
        flash('Credenciales incorrectas', 'error_login')
        return redirect('/')

    session['id_usuario'] = usuario_login.id
    session['nombre'] = usuario_login.nombre
    session['apellido'] = usuario_login.apellido

    return redirect('/dashboard')
#no se usa actualizar usuario pero puede servir en algun momento
@app.route('/actualiza/usuario', methods=['POST'])
def procesa_actualizar_usuario():
    
    usuario_actual = Usuario.obtener_por_id(session['id_usuario'])

    
    if usuario_actual is None:
        flash('Usuario no encontrado', 'error_actualizacion_usuario')
        return redirect('/user/account')

    
    datos_actualizacion = {
        "id_usuario": usuario_actual.id,
        "nombre": request.form.get('nombre', ''),
        "apellido": request.form.get('apellido', ''),
        "email": request.form.get('email', '')
    }

    if not Usuario.validar_actualizacion(datos_actualizacion):
        return redirect('/editar/usuario')

    if Usuario.actualizar_usuario(datos_actualizacion):
        session['nombre'] = datos_actualizacion['nombre']
        session['apellido'] = datos_actualizacion['apellido']

        flash('Datos actualizados correctamente.', 'success_actualizacion_usuario')
    else:
        flash('Error al actualizar los datos.', 'error_actualizacion_usuario')

    return redirect('/editar/usuario')

@app.route('/user/account')
def user_account():
    
    usuario_actual = Usuario.obtener_por_id(session.get('id_usuario'))

    arboles_del_usuario = Arbol.obtener_arboles_por_usuario(session.get('id_usuario'))

    return render_template('account.html', usuario=usuario_actual, arboles_del_usuario=arboles_del_usuario)


@app.route('/procesa/logout', methods=['POST'])
def procesa_logout():
    session.clear()
    return redirect('/')