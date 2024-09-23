import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('postgresql://samvela:2SeoGMqxUjLbo2eZT3xpF7nqJQwrdiDT@dpg-crjk96dumphs73d1nt3g-a/samvela')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Estudiante(db.Model):
    __tablename__ = 'alumnos'
    __table_args__ = {'schema': 'public'}
    no_control = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String)
    ap_paterno = db.Column(db.String)
    ap_materno = db.Column(db.String)
    semestre = db.Column(db.Integer)

    def to_dict(self):
        return {
            'no_control': self.no_control,
            'nombre': self.nombre,
            'ap_paterno': self.ap_paterno,
            'ap_materno': self.ap_materno,
            'semestre': self.semestre
        }

# Rutas de la API

@app.route('/api/alumnos', methods=['GET'])
def api_get_alumnos():
    """Obtiene la lista de todos los alumnos."""
    try:
        alumnos = Estudiante.query.all()
        return jsonify([alumno.to_dict() for alumno in alumnos])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alumnos/<string:no_control>', methods=['GET'])
def api_get_alumno(no_control):
    """Obtiene un alumno específico por su no_control."""
    alumno = Estudiante.query.get(no_control)
    return jsonify(alumno.to_dict()) if alumno else ('', 404)

@app.route('/api/alumnos', methods=['POST'])
def api_create_alumno():
    """Crea un nuevo alumno."""
    new_alumno = request.json
    if not all(key in new_alumno for key in ['no_control', 'nombre', 'ap_paterno', 'ap_materno', 'semestre']):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    nuevo_estudiante = Estudiante(
        no_control=new_alumno['no_control'],
        nombre=new_alumno['nombre'],
        ap_paterno=new_alumno['ap_paterno'],
        ap_materno=new_alumno['ap_materno'],
        semestre=new_alumno['semestre']
    )
    db.session.add(nuevo_estudiante)
    db.session.commit()
    return jsonify(nuevo_estudiante.to_dict()), 201

@app.route('/api/alumnos/<string:no_control>', methods=['PUT'])
def api_update_alumno(no_control):
    """Actualiza un alumno existente."""
    alumno = Estudiante.query.get(no_control)
    if not alumno:
        return ('', 404)

    updated_alumno = request.json
    for key, value in updated_alumno.items():
        setattr(alumno, key, value)
    
    db.session.commit()
    return ('', 204)

@app.route('/api/alumnos/<string:no_control>', methods=['PATCH'])
def api_patch_alumno(no_control):
    """Actualiza parcialmente un alumno existente."""
    alumno = Estudiante.query.get(no_control)
    if not alumno:
        return ('', 404)

    updated_fields = request.json
    for key, value in updated_fields.items():
        setattr(alumno, key, value)
    
    db.session.commit()
    return ('', 204)

@app.route('/api/alumnos/<string:no_control>', methods=['DELETE'])
def api_delete_alumno(no_control):
    """Elimina un alumno existente."""
    alumno = Estudiante.query.get(no_control)
    if alumno:
        db.session.delete(alumno)
        db.session.commit()
    return ('', 204)

# Rutas con vistas

@app.route('/')
def index():
    """Página principal que lista todos los alumnos."""
    alumnos = Estudiante.query.all()
    return render_template('index.html', alumnos=alumnos)

@app.route('/alumnos/new', methods=['GET', 'POST'])
def create_estudiante():
    """Crea un nuevo estudiante."""
    if request.method == 'POST':
        no_control = request.form['no_control']
        nombre = request.form['nombre']
        ap_paterno = request.form['ap_paterno']
        ap_materno = request.form['ap_materno']
        semestre = request.form['semestre']

        if not all([no_control, nombre, ap_paterno, ap_materno, semestre.isdigit()]):
            return render_template('create_estudiante.html', error="Por favor, complete todos los campos correctamente.")

        nuevo_estudiante = Estudiante(
            no_control=no_control,
            nombre=nombre,
            ap_paterno=ap_paterno,
            ap_materno=ap_materno,
            semestre=int(semestre)
        )
        db.session.add(nuevo_estudiante)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create_estudiante.html')

@app.route('/alumnos/update/<string:no_control>', methods=['GET', 'POST'])
def update_estudiante(no_control):
    """Actualiza un estudiante existente."""
    estudiante = Estudiante.query.get(no_control)
    if request.method == 'POST':
        estudiante.nombre = request.form['nombre']
        estudiante.ap_paterno = request.form['ap_paterno']
        estudiante.ap_materno = request.form['ap_materno']
        estudiante.semestre = int(request.form['semestre'])
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('update_estudiante.html', estudiante=estudiante)

@app.route('/alumnos/delete/<string:no_control>')
def delete_estudiante(no_control):
    """Elimina un estudiante existente."""
    estudiante = Estudiante.query.get(no_control)
    if estudiante:
        db.session.delete(estudiante)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
