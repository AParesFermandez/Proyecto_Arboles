from app_flask.config.mysqlconnection import connectToMySQL
from flask import flash, request
from app_flask import BASE_DATOS

class Arbol:
    def __init__(self, datos):
        self.id = datos['id']
        self.id_creador = datos['id_creador']
        self.especie = datos['especie']
        self.ubicacion = datos['ubicacion']
        self.razon = datos['razon']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']
        self.fecha_plantacion = datos['fecha_plantacion']
        self.nombre_creador = datos.get('nombre_creador')  

    @classmethod
    def crear_arbol(cls, datos_arbol):
        query = """
                INSERT INTO arbol(id_creador, especie, ubicacion, razon, fecha_plantacion)
                VALUES (%(id_creador)s, %(especie)s, %(ubicacion)s, %(razon)s, %(fecha_plantacion)s);
                """
        return connectToMySQL(BASE_DATOS).query_db(query, datos_arbol)

    @classmethod
    def obtener_arbol_por_id(cls, id_arbol):
        query = """
                SELECT a.*, u.nombre AS nombre_creador
                FROM arbol a
                JOIN usuario u ON a.id_creador = u.id
                WHERE a.id = %(id_arbol)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_arbol': id_arbol})
        if len(resultado) == 0:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_todos(cls):
        query = """
                SELECT *
                FROM arbol;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)
        return [cls(resultado) for resultado in resultados]

    @classmethod
    def obtener_todos_con_creador(cls):
        query = """
                SELECT a.*, u.nombre AS nombre_creador
                FROM arbol a
                JOIN usuario u ON a.id_creador = u.id;
                """
        resultados = connectToMySQL(BASE_DATOS).query_db(query)
        arboles = []
        for resultado in resultados:
            arbol = cls(resultado)
            arbol.nombre_creador = resultado['nombre_creador']
            arboles.append(arbol)
        return arboles
    
    @classmethod
    def obtener_uno_con_creador(cls, id_arbol):
        query = """
                SELECT a.*, u.nombre AS nombre_creador
                FROM arbol a
                JOIN usuario u ON a.id_creador = u.id
                WHERE a.id = %(id_arbol)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_arbol': id_arbol})
        if not resultado or len(resultado) == 0:
            return None
        arbol = cls(resultado[0])
        arbol.nombre_creador = resultado[0]['nombre_creador']
        return arbol

    @classmethod
    def eliminar_arbol(cls, id_arbol):
        query = """
                DELETE FROM arbol
                WHERE id = %(id_arbol)s;
                """
        return connectToMySQL(BASE_DATOS).query_db(query, {'id_arbol': id_arbol})

    
    @classmethod
    def obtener_detalles_por_id_usuario(cls, id_usuario, id_arbol):
        query = """
                SELECT a.*, u.nombre AS nombre_usuario
                FROM arbol a
                JOIN usuario u ON a.id_creador = u.id
                WHERE a.id = %(id_arbol)s AND a.id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_arbol': id_arbol, 'id_usuario': id_usuario})

        if not resultado or len(resultado) == 0:
            return None

        arbol = cls(resultado[0])
        arbol.nombre_usuario = resultado[0]['nombre_usuario']
        return arbol

    @classmethod
    def obtener_arboles_por_usuario(cls, id_usuario):
        query = """
                SELECT *
                FROM arbol
                WHERE id_creador = %(id_usuario)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'id_usuario': id_usuario})
        return [cls(arbol) for arbol in resultado]
    #contador
    @classmethod
    def contar_visitantes_por_arbol(cls, arbol_id):
        query = """
                SELECT COUNT(*) AS numero_visitantes
                FROM visitantes
                WHERE arbol_id = %(arbol_id)s;
                """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, {'arbol_id': arbol_id})
        return resultado[0]['numero_visitantes'] if resultado else 0

    @classmethod
    def actualizar_arbol(cls, id_arbol, datos_arbol):
        if cls.validar_arbol(datos_arbol):
            query = """
                    UPDATE arbol
                    SET especie = %(especie)s,
                        ubicacion = %(ubicacion)s,
                        razon = %(razon)s,
                        fecha_plantacion = %(fecha_plantacion)s,
                        fecha_actualizacion = NOW()
                    WHERE id = %(id)s;
                    """
            datos_arbol['id'] = id_arbol
            connectToMySQL(BASE_DATOS).query_db(query, datos_arbol)
            return True
        else:
            return False


    @staticmethod
    def validar_arbol(datos_arbol):
        es_valido = True
        if len(datos_arbol['especie']) < 5:
            es_valido = False
            flash('La especie debe tener al menos 5 caracteres.', 'error_especie')

        if len(datos_arbol['ubicacion']) < 2:
            es_valido = False
            flash('La ubicación debe tener al menos 2 caracteres.', 'error_ubicacion')

        if len(datos_arbol['razon']) > 50:
            es_valido = False
            flash('La razón no puede exceder los 50 caracteres.', 'error_razon')

        return es_valido