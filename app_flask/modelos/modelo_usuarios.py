import re
from .modelo_arboles import Arbol
from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash
from app_flask import BASE_DATOS, EMAIL_REGEX

class Usuario:
    def __init__(self, datos):
        self.id = datos['id']
        self.nombre = datos['nombre']
        self.apellido = datos['apellido']
        self.email = datos['email']
        self.password = datos['password']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

    @classmethod
    def crear_uno(cls, datos):
        query = """
                INSERT INTO usuario(nombre, apellido, email, password)
                VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos)

    @classmethod
    def obtener_por_email(cls, email):
        query = """
                SELECT *
                FROM usuario
                WHERE email = %(email)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'email': email})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_uno(cls, datos):
        query = """
                SELECT *
                FROM usuario
                WHERE email = %(email)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, datos)
        if len(resultado) == 0:
            return None
        return cls(resultado[0])
    
    @classmethod
    def obtener_por_id(cls, id_usuario):
        query = """
                SELECT *
                FROM usuario
                WHERE id = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])
    
    @classmethod
    def actualizar_usuario(cls, datos_actualizacion):
        if not datos_actualizacion['nombre'] or not datos_actualizacion['apellido'] or not datos_actualizacion['email']:
            flash('Todos los campos son obligatorios.', 'error_actualizacion_usuario')
            return False

        if len(datos_actualizacion['nombre']) < 3 or len(datos_actualizacion['apellido']) < 3:
            flash('El nombre y el apellido deben tener al menos 3 caracteres.', 'error_actualizacion_usuario')
            return False

        Usuario = cls.obtener_por_id(datos_actualizacion['id_usuario'])

        if not Usuario.validar_email(datos_actualizacion['email']):
            flash('Correo electrónico inválido.', 'error_actualizacion_usuario')
            return False

        query = """
                UPDATE usuario
                SET nombre = %(nombre)s, apellido = %(apellido)s, email = %(email)s
                WHERE id = %(id_usuario)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos_actualizacion)

    @classmethod
    def obtener_arboles_del_usuario(cls, id_usuario):
        query = """
                SELECT *
                FROM arbol
                WHERE id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        return [Arbol(arbol) for arbol in resultado]
    
    #logica visita de arbol

    @classmethod
    def ya_visitado_arbol(cls, id_usuario, id_arbol):
        query = """
            SELECT *
            FROM visitantes
            WHERE usuario_id = %(id_usuario)s AND arbol_id = %(id_arbol)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_arbol': id_arbol})
        return bool(resultado)
    
    @classmethod
    def registrar_visita_arbol(cls, id_usuario, id_arbol):
        query = """
            INSERT INTO visitantes (usuario_id, arbol_id)
            VALUES (%(id_usuario)s, %(id_arbol)s)
        """
        data = {
            'id_usuario': id_usuario,
            'id_arbol': id_arbol
        }
        connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def obtener_usuarios_por_arbol_id(cls, id_arbol):
        query = """
            SELECT u.*
            FROM usuario u
            JOIN visitantes v ON u.id = v.usuario_id
            WHERE v.arbol_id = %(id_arbol)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_arbol': id_arbol})
        return [cls(usuario) for usuario in resultado]

    @classmethod
    def ya_visitado_arbol(cls, id_usuario, id_arbol):
        query = """
            SELECT *
            FROM visitantes
            WHERE usuario_id = %(id_usuario)s AND arbol_id = %(id_arbol)s;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario, 'id_arbol': id_arbol})
        return bool(resultado)

    @staticmethod
    def validar_actualizacion(cls, datos):
            es_valido = True
            if len(datos['nombre']) < 3:
                es_valido = False
                flash('Por favor escribe tu nombre, 3 caracteres mínimos.', 'error_nombre')
            if len(datos['apellido']) < 3:
                es_valido = False
                flash('Por favor escribe tu apellido, 3 caracteres mínimos.', 'error_apellido')
            if not cls.validar_email(datos['email']):
                es_valido = False
                flash('Por favor ingresa un correo válido', 'error_email')
            return es_valido

    @staticmethod
    def validar_registro(datos):
        es_valido = True
        if len(datos['nombre']) < 2:
            es_valido = False
            flash('Por favor escribe tu nombre, 2 caracteres mínimos.', 'error_nombre')
        if len(datos['apellido']) < 2:
            es_valido = False
            flash('Por favor escribe tu apellido, 2 caracteres mínimos.', 'error_apellido')
        if not Usuario.validar_email(datos['email']):
            es_valido = False
            flash('Por favor ingresa un correo válido', 'error_email')
        if datos['password'] != datos['password_confirmar']:
            es_valido = False
            flash('Tus contraseñas no coinciden.', 'error_password')
        if len(datos['password']) < 8:
            es_valido = False
            flash('Por favor proporciona una contraseña, 8 caracteres mínimos.', 'error_password')
        return es_valido

    @staticmethod
    def validar_email(email):
        return re.match(EMAIL_REGEX, email) is not None
