from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId 
import json

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGO ---
MONGO_URI = "mongodb+srv://#######:########@clusterudla1.m2zgafd.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client['Catecismo'] 

# --- RUTAS ---

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/estudiantes')
def estudiantes():
    # Traemos los estudiantes (limitado a 20 para rapidez)
    datos = list(db.Estudiantes.find().limit(20))
    return render_template('estudiantes.html', lista_estudiantes=datos)

# --- CREAR (CREATE) ---
@app.route('/crear_estudiante')
def crear_estudiante():
    return render_template('formulario_estudiante.html')

@app.route('/guardar_estudiante', methods=['POST'])
def guardar_estudiante():
    # Recibir datos del formulario
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    cedula = request.form['nroDoc']
    telefono = request.form['telefono']
    ciudad = request.form['ciudad']

    # Crear documento JSON
    nuevo_estudiante = {
        "nombres": nombres,
        "apellidos": apellidos,
        "nroDoc": cedula,
        "tipoPerfil": "ESTUDIANTE",
        "contacto": {
            "telefono": telefono,
            "direccion": {
                "ciudad": ciudad
            }
        },
        "historialInscripciones": []
    }

    # Guardar en Mongo
    db.Estudiantes.insert_one(nuevo_estudiante)
    return redirect('/estudiantes')

# --- ELIMINAR (DELETE) ---
@app.route('/eliminar_estudiante/<id_mongo>')
def eliminar_estudiante(id_mongo):
    # Usamos ObjectId para encontrar el ID exacto
    db.Estudiantes.delete_one({"_id": ObjectId(id_mongo)})
    return redirect('/estudiantes')

# --- EDITAR (UPDATE) - ¡FALTABA ESTO! ---

# 1. Mostrar el formulario con los datos cargados
@app.route('/editar_estudiante/<id_mongo>')
def editar_estudiante(id_mongo):
    # Buscamos al estudiante específico
    estudiante = db.Estudiantes.find_one({"_id": ObjectId(id_mongo)})
    return render_template('editar_estudiante.html', estudiante=estudiante)

# 2. Guardar los cambios
@app.route('/actualizar_estudiante/<id_mongo>', methods=['POST'])
def actualizar_estudiante(id_mongo):
    # Recibimos los nuevos datos
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    telefono = request.form['telefono']
    ciudad = request.form['ciudad']

    # Actualizamos en Mongo usando $set (para no borrar lo demás)
    db.Estudiantes.update_one(
        {"_id": ObjectId(id_mongo)},
        {"$set": {
            "nombres": nombres,
            "apellidos": apellidos,
            "contacto.telefono": telefono,
            "contacto.direccion.ciudad": ciudad
        }}
    )
    return redirect('/estudiantes')

# --- RUTA 4: VER PERFIL COMPLETO (Ficha Unificada) ---
@app.route('/ver_perfil/<id_mongo>')
def ver_perfil(id_mongo):
    # 1. Buscamos el documento crudo
    item = db.Estudiantes.find_one({"_id": ObjectId(id_mongo)})
    
    # 2. NORMALIZACIÓN (Detectar si es dato antiguo anidado o nuevo plano)
    est = item['Estudiantes'][0] if 'Estudiantes' in item else item

    # 3. SANITIZACIÓN (Convertir textos JSON a Listas/Objetos reales si es necesario)
    # Lista de campos que podrían venir sucios como texto desde SQL
    campos_complejos = ['contacto', 'representantes', 'sacramentosRecibidos', 'historialInscripciones']
    
    for campo in campos_complejos:
        # Si el campo existe y es un STRING (Texto), lo convertimos a JSON real
        if campo in est and isinstance(est[campo], str):
            try:
                est[campo] = json.loads(est[campo])
            except:
                pass # Si falla, lo dejamos como estaba

    # Enviamos 'est' (datos limpios) y 'item._id' (el ID original para los enlaces)
    return render_template('perfil_estudiante.html', estudiante=est, id_original=item['_id'])

@app.route('/catequistas')
def catequistas():
    # Traemos todos los catequistas
    datos = list(db.Catequistas.find())
    return render_template('catequistas.html', lista=datos)

@app.route('/parroquias')
def parroquias():
    # 1. Traemos los datos crudos de la base
    datos = list(db.Parroquias.find())
    
    # 2. SANITIZACIÓN: Convertimos el texto JSON a Objeto real
    for item in datos:
        # Detectamos si es dato antiguo (anidado) o nuevo
        p = item['Parroquias'][0] if 'Parroquias' in item else item
        
        # Si la ubicación es TEXTO (str), usamos json.loads para convertirla a DICCIONARIO
        if isinstance(p.get('ubicacion'), str):
            try:
                p['ubicacion'] = json.loads(p['ubicacion'])
            except:
                pass # Si falla, lo dejamos como estaba
                
    return render_template('parroquias.html', lista=datos)

@app.route('/grupos')
def grupos():
    # 1. Traemos los datos
    datos = list(db.Grupos.find())
    
    # 2. SANITIZACIÓN: Convertir texto JSON a Objeto
    for item in datos:
        # Detectamos si es dato antiguo (anidado) o nuevo
        g = item['Grupos'][0] if 'Grupos' in item else item
        
        # Buscamos la llave correcta (puede ser con mayúscula o minúscula)
        key_anio = 'anioLectivo' if 'anioLectivo' in g else 'aniolectivo'
        
        # Si existe y es TEXTO, lo convertimos a DICCIONARIO
        if key_anio in g and isinstance(g[key_anio], str):
            try:
                g[key_anio] = json.loads(g[key_anio])
            except:
                pass # Si falla, no hacemos nada

    return render_template('grupos.html', lista=datos)

if __name__ == '__main__':
    app.run(debug=True, port=5000)