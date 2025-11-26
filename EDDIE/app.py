from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

import sqlite3
import os
from datetime import datetime 
# Importamos la nueva función generar_constancia_grado
from pdf_creator import (
    generar_constancia_rh, 
    generar_carta_exclusividad, 
    generar_constancia_desarrollo, 
    generar_constancia_cvu,
    generar_constancia_grado,
    generar_constancia_participacion_planes
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

def get_db_connection():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'EDDI.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# --- FUNCIÓN PARA ARREGLAR RUTAS DE IMÁGENES ---
def resolver_ruta_imagen(ruta_relativa):
    if not ruta_relativa:
        return None
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_completa = os.path.join(base_dir, ruta_relativa)
    return os.path.normpath(ruta_completa)

# ================= MÉTODOS REUTILIZABLES =================

def obtener_datos_docente_completo(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.*, i.nombre_institucion, p.nombre_plaza, p.clave_presupuestal, dept.nombre AS departamento
        FROM Docentes d
        JOIN Instituciones i ON d.id_institucion = i.id_institucion
        JOIN Plazas p ON d.id_plaza = p.id_plaza
        JOIN Departamentos dept ON d.id_departamento = dept.id_departamento
        WHERE d.id_docente = ?
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchone()
    conn.close()
    return datos

def obtener_datos_firmante_rh():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.nombre, d.apellidos, pa.nombre_puesto
        FROM AsignacionPuestos ap
        JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
        JOIN Docentes d ON ap.id_docente = d.id_docente
        WHERE pa.nombre_puesto LIKE '%Recursos Humanos%' AND ap.fecha_fin IS NULL
    """
    cursor.execute(query)
    return cursor.fetchone() or {"nombre": "FUNCIONARIO", "apellidos": "DESCONOCIDO", "nombre_puesto": "JEFE DE RH"}

def obtener_datos_firmante_desarrollo():
    """Busca al Jefe de Desarrollo Académico actual."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.nombre, d.apellidos, pa.nombre_puesto
        FROM AsignacionPuestos ap
        JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
        JOIN Docentes d ON ap.id_docente = d.id_docente
        WHERE pa.nombre_puesto LIKE '%Desarrollo Académico%' AND ap.fecha_fin IS NULL
    """
    cursor.execute(query)
    resultado = cursor.fetchone()
    conn.close()
    return resultado or {"nombre": "FUNCIONARIO", "apellidos": "DESCONOCIDO", "nombre_puesto": "JEFE DE DESARROLLO"}

def buscar_id_destinatario_por_puesto(palabra_clave):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT ap.id_docente 
        FROM AsignacionPuestos ap
        JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
        WHERE pa.nombre_puesto LIKE ? AND ap.fecha_fin IS NULL
    """
    cursor.execute(query, (f'%{palabra_clave}%',))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado['id_docente']
    return None

# --- NUEVO HELPER: OBTENER DATOS DE GRADO / CÉDULA ---
def obtener_datos_grado(user_id):
    """
    Recupera el grado máximo y determina si usa Acta de Examen (Alumno Ficticio) o Cédula.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Buscamos el grado máximo registrado (Maestría o Doctorado)
    cursor.execute("""
        SELECT e.nombre_titulo 
        FROM Docente_Escolaridad de
        JOIN Escolaridades e ON de.id_escolaridad = e.id_escolaridad
        WHERE de.id_docente = ?
        ORDER BY de.id_escolaridad DESC LIMIT 1
    """, (user_id,))
    grado_res = cursor.fetchone()
    titulo_grado = grado_res['nombre_titulo'] if grado_res else "GRADO NO REGISTRADO"

    # 2. Buscamos si existe un Acta de Examen vinculada (Lógica del alumno ficticio 99000 + ID)
    id_alumno_ficticio = 99000 + int(user_id)
    
    cursor.execute("""
        SELECT ae.fecha_examen, ae.nombre_trabajo 
        FROM ActasExamen ae
        WHERE ae.id_alumno_titulado = ?
    """, (id_alumno_ficticio,))
    acta_res = cursor.fetchone()

    # 3. Datos del docente para backup de cédula
    cursor.execute("SELECT registro_cvu FROM Docentes WHERE id_docente = ?", (user_id,))
    docente_res = cursor.fetchone()
    cedula = docente_res['registro_cvu'] if docente_res else "SIN DATO"

    conn.close()

    # Preparamos el diccionario
    datos_grado = {'titulo': titulo_grado}

    # Lógica de prioridad: Acta > Cédula
    if acta_res:
        datos_grado['tipo_evidencia'] = 'Acta de Examen'
        datos_grado['fecha_examen'] = acta_res['fecha_examen']
        datos_grado['nombre_trabajo'] = acta_res['nombre_trabajo']
    else:
        datos_grado['tipo_evidencia'] = 'Cédula'
        datos_grado['cedula'] = cedula
        
    return datos_grado


# ================= RUTAS PRINCIPALES =================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuarios WHERE id_usuario = ? AND contrasena = ?', (usuario, contrasena))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id_usuario']
            session['rol'] = user['rol']
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    datos = obtener_datos_docente_completo(session['user_id'])
    return render_template('dashboard.html', docente=datos) if datos else "Error datos"

@app.route('/generar_documentos')
def generar_documentos():
    if 'user_id' not in session: return redirect(url_for('login'))
    datos = obtener_datos_docente_completo(session['user_id'])
    return render_template('generar_documentos.html', docente=datos)

@app.route('/recibidos')
def recibidos():
    if 'user_id' not in session or session.get('rol') != 'jefe':
        return redirect(url_for('dashboard'))
    
    destinatario_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca solicitudes pendientes
    query = """
        SELECT s.*, d.nombre, d.apellidos 
        FROM SolicitudesDocumentos s
        JOIN Docentes d ON s.id_docente_solicitante = d.id_docente
        WHERE s.id_usuario_destinatario = ? AND s.estado = 'Pendiente'
    """
    cursor.execute(query, (destinatario_id,))
    solicitudes = cursor.fetchall()
    conn.close()
    
    datos_jefe = obtener_datos_docente_completo(destinatario_id)
    return render_template('recibidos.html', docente=datos_jefe, solicitudes=solicitudes)

@app.route('/documentos_firmados')
def documentos_firmados():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca documentos YA firmados del usuario actual
    query = """
        SELECT * FROM SolicitudesDocumentos 
        WHERE id_docente_solicitante = ? AND estado = 'Firmado'
        ORDER BY fecha_firma DESC
    """
    cursor.execute(query, (user_id,))
    documentos = cursor.fetchall()
    conn.close()
    
    datos_docente = obtener_datos_docente_completo(user_id)
    return render_template('documentos_firmados.html', docente=datos_docente, documentos=documentos)

# ================= RUTAS DE DOCUMENTOS Y ACCIONES =================

@app.route('/enviar_documento/<tipo>', methods=['POST']) 
def enviar_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    solicitante_id = session['user_id']
    destinatario_id = None
    
    if tipo == 'constancia_rh':
        destinatario_id = buscar_id_destinatario_por_puesto('Recursos Humanos')
    
    # CAMBIO: Quitamos 'constancia_grado' de esta lista porque ya no se envía.
    elif tipo in ['constancia_desarrollo', 'constancia_cvu']: 
        destinatario_id = buscar_id_destinatario_por_puesto('Desarrollo Académico')
    
    if destinatario_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. VALIDACIÓN: ¿Ya existe una solicitud igual pendiente?
        cursor.execute("""
            SELECT id_solicitud FROM SolicitudesDocumentos 
            WHERE id_docente_solicitante = ? 
            AND tipo_documento = ? 
            AND estado = 'Pendiente'
        """, (solicitante_id, tipo))
        existe = cursor.fetchone()

        if existe:
            flash("Ya tienes una solicitud pendiente de este documento.")
        else:
            # 2. Si no existe, procedemos a insertar
            cursor.execute("""
                INSERT INTO SolicitudesDocumentos (id_docente_solicitante, id_usuario_destinatario, tipo_documento, estado)
                VALUES (?, ?, ?, 'Pendiente')
            """, (solicitante_id, destinatario_id, tipo))
            conn.commit()
            flash("Documento enviado correctamente a revisión.")
        
        conn.close()
    else:
        flash("Error: No se encontró destinatario.")
        
    return redirect(url_for('generar_documentos'))


# --- RUTA: VER DOCUMENTO (PREVISUALIZACIÓN) ---
@app.route('/ver_documento/<tipo>')
def ver_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # 1. Parámetros iniciales
    solicitud_id = request.args.get('id_solicitud')
    target_user_id = session['user_id']
    datos_firma = None # Por defecto limpio

    # Si hay solicitud (historial o recibidos), obtenemos el usuario target y firma si aplica
    if solicitud_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesDocumentos WHERE id_solicitud = ?", (solicitud_id,))
        solicitud = cursor.fetchone()
        conn.close()

        if solicitud:
            target_user_id = solicitud['id_docente_solicitante']
            if solicitud['estado'] == 'Firmado':
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = ?", (solicitud['id_usuario_destinatario'],))
                jefe_usuario = cursor.fetchone()
                conn.close()

                if jefe_usuario:
                    datos_firma = {
                        'ruta_firma': resolver_ruta_imagen(jefe_usuario['ruta_firma']),
                        'ruta_sello': resolver_ruta_imagen(jefe_usuario['ruta_sello'])
                    }

    # 2. LÓGICA SEGÚN EL TIPO DE DOCUMENTO
    datos_docente = obtener_datos_docente_completo(target_user_id)

    # === CASO A: CONSTANCIA RH ===
    if tipo == 'constancia_rh':
        datos_firmante = obtener_datos_firmante_rh()
        pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma)

    # === CASO B: CARTA EXCLUSIVIDAD ===
    elif tipo == 'carta_exclusividad':
        pdf_buffer = generar_carta_exclusividad(datos_docente)

    # === CASO C: CONSTANCIA DESARROLLO ===
    elif tipo == 'constancia_desarrollo':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_desarrollo(datos_docente, datos_firmante, datos_firma)

    # === CASO D: CONSTANCIA CVU ===
    elif tipo == 'constancia_cvu':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_cvu(datos_docente, datos_firmante, datos_firma)

    # === CASO E: CONSTANCIA GRADO (NUEVO) ===
    elif tipo == 'constancia_grado':
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)

    # ... (bloques anteriores) ...
    elif tipo == 'constancia_grado':
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)

    # === NUEVO: CONSTANCIA PARTICIPACIÓN PLANES ===
    elif tipo == 'constancia_participacion_planes':
        # No requiere jefe firmante, es informativa
        datos_participacion = obtener_datos_participacion_planes(target_user_id)
        # Reutilizamos la firma solo si viniera de BD, pero aquí pasamos None o vacío
        pdf_buffer = generar_constancia_participacion_planes(datos_docente, datos_participacion, None)
    
    else:
        return "Error: Tipo de documento no válido"
    
    # 3. Enviamos el PDF al navegador
    nombre_archivo = f"Vista_{tipo}_{datetime.now().strftime('%M%S')}.pdf"
    return send_file(pdf_buffer, as_attachment=False, download_name=nombre_archivo, mimetype='application/pdf')


# --- RUTA: DESCARGAR DOCUMENTO ---
@app.route('/descargar_documento/<tipo>')
def descargar_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    solicitud_id = request.args.get('id_solicitud')
    target_user_id = session['user_id']
    datos_firma = None

    if solicitud_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesDocumentos WHERE id_solicitud = ?", (solicitud_id,))
        solicitud = cursor.fetchone()
        conn.close()
        
        if solicitud:
            target_user_id = solicitud['id_docente_solicitante']
            if solicitud['estado'] == 'Firmado':
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = ?", (solicitud['id_usuario_destinatario'],))
                jefe_usuario = cursor.fetchone()
                conn.close()
                if jefe_usuario:
                    datos_firma = {
                        'ruta_firma': resolver_ruta_imagen(jefe_usuario['ruta_firma']),
                        'ruta_sello': resolver_ruta_imagen(jefe_usuario['ruta_sello'])
                    }

    datos_docente = obtener_datos_docente_completo(target_user_id)

    # === GENERACIÓN ===
    if tipo == 'constancia_rh':
        datos_firmante = obtener_datos_firmante_rh()
        pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma)
    elif tipo == 'carta_exclusividad':
        pdf_buffer = generar_carta_exclusividad(datos_docente)
    elif tipo == 'constancia_desarrollo':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_desarrollo(datos_docente, datos_firmante, datos_firma)
    elif tipo == 'constancia_cvu':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_cvu(datos_docente, datos_firmante, datos_firma)
    elif tipo == 'constancia_grado': # NUEVO
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)
# ... (bloques anteriores) ...
    elif tipo == 'constancia_grado':
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)
    
    # === NUEVO: CONSTANCIA PARTICIPACIÓN PLANES ===
    elif tipo == 'constancia_participacion_planes':
        datos_participacion = obtener_datos_participacion_planes(target_user_id)
        pdf_buffer = generar_constancia_participacion_planes(datos_docente, datos_participacion, None)

    else:
        return "Error: Tipo de documento no válido"

    nombre_archivo = f"{tipo}_{target_user_id}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')


@app.route('/firmar_solicitud/<int:id_solicitud>', methods=['POST'])
def firmar_solicitud(id_solicitud):
    if 'user_id' not in session or session['rol'] != 'jefe':
        return "No autorizado", 403

    password = request.form['password']
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Validar Contraseña
    cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = ? AND contrasena = ?", (user_id, password))
    usuario_jefe = cursor.fetchone()

    if not usuario_jefe:
        flash("Contraseña incorrecta.")
        conn.close()
        return redirect(url_for('recibidos'))

    # 2. Obtener solicitud
    cursor.execute("SELECT * FROM SolicitudesDocumentos WHERE id_solicitud = ?", (id_solicitud,))
    solicitud = cursor.fetchone()

    # 3. Firmar en BD
    fecha_firma = datetime.now()
    cursor.execute("""
        UPDATE SolicitudesDocumentos 
        SET estado = 'Firmado', fecha_firma = ?
        WHERE id_solicitud = ?
    """, (fecha_firma, id_solicitud))
    conn.commit()

    # 4. Generar PDF Firmado para descarga inmediata
    target_id = solicitud['id_docente_solicitante']
    datos_docente = obtener_datos_docente_completo(target_id)
    
    # Preparar datos de firma visual
    datos_firma_visual = {
        'ruta_firma': resolver_ruta_imagen(usuario_jefe['ruta_firma']),
        'ruta_sello': resolver_ruta_imagen(usuario_jefe['ruta_sello']) # Usamos sello del usuario jefe
    }
    
    tipo_doc = solicitud['tipo_documento']
    pdf_buffer = None

    if tipo_doc == 'constancia_rh':
        datos_firmante = obtener_datos_firmante_rh()
        pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma_visual)
    
    elif tipo_doc == 'constancia_desarrollo':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_desarrollo(datos_docente, datos_firmante, datos_firma_visual)
        
    elif tipo_doc == 'constancia_cvu':
        datos_firmante = obtener_datos_firmante_desarrollo()
        pdf_buffer = generar_constancia_cvu(datos_docente, datos_firmante, datos_firma_visual)
    
    elif tipo_doc == 'constancia_grado': # NUEVO
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma_visual)

    conn.close()

    if pdf_buffer:
        nombre_archivo = f"Firmado_{tipo_doc}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')
    else:
        return "Error al generar documento firmado"

# --- RUTA: PROCESAR RECHAZO (JEFE) ---
@app.route('/rechazar_solicitud/<int:id_solicitud>', methods=['POST'])
def rechazar_solicitud(id_solicitud):
    if 'user_id' not in session or session['rol'] != 'jefe':
        return "No autorizado", 403

    motivo = request.form['motivo'] 

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE SolicitudesDocumentos 
        SET estado = 'Rechazado', motivo_rechazo = ?
        WHERE id_solicitud = ?
    """, (motivo, id_solicitud))
    
    conn.commit()
    conn.close()
    
    flash("Documento rechazado correctamente.")
    return redirect(url_for('recibidos'))


# --- RUTA: VER DOCUMENTOS DENEGADOS (DOCENTE) ---
@app.route('/documentos_denegados')
def documentos_denegados():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM SolicitudesDocumentos 
        WHERE id_docente_solicitante = ? AND estado = 'Rechazado'
        ORDER BY fecha_solicitud DESC
    """
    cursor.execute(query, (user_id,))
    documentos = cursor.fetchall()
    conn.close()
    
    datos_docente = obtener_datos_docente_completo(user_id)
    return render_template('documentos_denegados.html', docente=datos_docente, documentos=documentos)

def obtener_datos_participacion_planes(user_id):
    """Recupera la participación en diseño curricular (Evento ID 4 en nuestro ejemplo)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscamos en CoordinacionEventos un evento que sea de "Diseño" o similar
    # En el insert usamos el ID 4 para la RNDIC-ISC
    query = """
        SELECT ce.*, ea.nombre AS nombre_evento, ea.organizador, pe.nombre_periodo
        FROM CoordinacionEventos ce
        JOIN EventosAcademicos ea ON ce.id_evento_acad = ea.id_evento_acad
        JOIN PeriodosEscolares pe ON ce.id_periodo = pe.id_periodo
        WHERE ce.id_docente = ? AND ea.nombre LIKE '%Diseño%'
        ORDER BY ce.id_periodo DESC LIMIT 1
    """
    cursor.execute(query, (user_id,))
    dato = cursor.fetchone()
    conn.close()
    return dato

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)