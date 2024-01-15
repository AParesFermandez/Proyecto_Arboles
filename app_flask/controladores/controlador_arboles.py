from flask import render_template, request, redirect, session, flash, url_for
from app_flask.modelos.modelo_arboles import Arbol
from app_flask import app
from app_flask.modelos.modelo_usuarios import Usuario

@app.route('/dashboard', methods=['GET'])
def desplegar_arboles():
    if 'id_usuario' not in session:
        return redirect('/')

    lista_arboles = Arbol.obtener_todos_con_creador()

    for arbol in lista_arboles:
        arbol.numero_visitantes = Arbol.contar_visitantes_por_arbol(arbol.id)

    return render_template('dashboard.html', lista_arboles=lista_arboles)

@app.route('/new', methods=['GET'])
def desplegar_formulario_arboles():
    if 'id_usuario' not in session:
        return redirect('/')

    return render_template('new.html')

@app.route('/new', methods=['POST'])
def crear_arboles():
    if 'id_usuario' not in session:
        return redirect('/')

    especie = request.form.get('especie', '')
    ubicacion = request.form.get('ubicacion', '')
    razon = request.form.get('razon', '')
    fecha_plantacion = request.form.get('fecha_plantacion', '')

    nuevo_arbol = {
        'id_creador': session['id_usuario'],
        'especie': especie,
        'ubicacion': ubicacion,
        'razon': razon,
        'fecha_plantacion': fecha_plantacion  
    }

    if not Arbol.validar_arbol(nuevo_arbol):
        flash('Error al crear el árbol. Por favor, inténtalo de nuevo.', 'error_creacion_arbol')
        return redirect('/new')

    id_arbol = Arbol.crear_arbol(nuevo_arbol)

    if not id_arbol:
        flash('Error al crear el árbol.', 'error_creacion_arbol')
    else:
        flash('Árbol creado exitosamente.', 'success_creacion_arbol')

    return redirect('/dashboard')

@app.route('/eliminar/arboles/<int:id>', methods=['POST'])
def eliminar_arboles(id):
    resultado = Arbol.eliminar_arbol(id)

    if resultado:
        flash('Árbol eliminado exitosamente.', 'success_eliminar_arbol')
    else:
        flash('Error al eliminar el árbol.', 'error_eliminar_arbol')

    return redirect('/dashboard')

@app.route('/arboles/usuario', methods=['GET'])
def obtener_arboles_usuario():
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']
    arboles_del_usuario = Arbol.obtener_arboles_por_usuario(id_usuario)

    return render_template('arboles_usuario.html', arboles_del_usuario=arboles_del_usuario)

@app.route('/eliminar/arboles/<int:id>', methods=['POST'])
def eliminar_arbol(id):
    arbol = {'id': id}
    Arbol.elimina_uno(arbol)
    return redirect('/user/account')

#logica para los visitantes

@app.route('/visitar/<int:id>', methods=['GET'])
def visitar_arbol(id):
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    if Usuario.ya_visitado_arbol(id_usuario, id):
        flash('Ya has visitado este árbol.', 'error_visitar_arbol')
        return redirect(f'/show/{id}')

    Usuario.registrar_visita_arbol(id_usuario, id)

    return redirect(f'/show/{id}')

@app.route('/visitar/<int:id_arbol>', methods=['GET'])
def registrar_visita(id_arbol):
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']
    Usuario.registrar_visita_arbol(id_usuario, id_arbol)

    return redirect(url_for('desplegar_detalle_arboles', id=id_arbol))

@app.route('/show/<int:id>')
def desplegar_detalle_arboles(id):
    arbol = Arbol.obtener_arbol_por_id(id)

    if arbol is None:
        flash('No se encontró el árbol.', 'error_arbol_no_encontrado')
        return redirect('/dashboard')

    usuarios_visitantes = Usuario.obtener_usuarios_por_arbol_id(id)
    id_usuario = session.get('id_usuario')

    ya_visitado = False
    visitado = False

    if id_usuario:
        ya_visitado = any(usuario.id == id_usuario for usuario in usuarios_visitantes)
        visitado = Usuario.ya_visitado_arbol(id_usuario, id)

    return render_template('show.html', arbol=arbol, visitantes=usuarios_visitantes, ya_visitado=ya_visitado, visitado=visitado)

#para editar arboles

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_arbol(id):
    if request.method == 'GET':
        arbol = Arbol.obtener_arbol_por_id(id)
        if arbol:
            return render_template('editar_arbol.html', arbol=arbol)
        else:
            flash('Árbol no encontrado.', 'error')
            return redirect('/dashboard')

    elif request.method == 'POST':
        especie = request.form['especie']
        ubicacion = request.form['ubicacion']
        razon = request.form['razon']
        fecha_plantacion = request.form['fecha_plantacion']
        
        datos_arbol = {
            'especie': especie,
            'ubicacion': ubicacion,
            'razon': razon,
            'fecha_plantacion': fecha_plantacion
        }
        
        if not Arbol.validar_arbol(datos_arbol):
            return redirect(f'/editar/{id}')
        
        resultado_actualizacion = Arbol.actualizar_arbol(id, datos_arbol)
        print("Resultado de la actualización:", resultado_actualizacion)
        if resultado_actualizacion:
            flash('Árbol actualizado correctamente.', 'success')
            return redirect('/user/account')
        else:
            flash('Error al actualizar el árbol.', 'error')
        return redirect(f'/editar/{id}')