from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

import sqlite3
import os
from datetime import datetime 
from pdf_creator import generar_constancia_rh, generar_carta_exclusividad # <-- Agregado

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

# --- MODIFICADO: ENVIAR CON VALIDACIÓN ANTI-DUPLICADOS ---
@app.route('/enviar_documento/<tipo>', methods=['POST']) # ¡Ahora solo acepta POST!
def enviar_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    solicitante_id = session['user_id']
    destinatario_id = None
    
    if tipo == 'constancia_rh':
        destinatario_id = buscar_id_destinatario_por_puesto('Recursos Humanos')
    
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

    # 2. LÓGICA SEGÚN EL TIPO DE DOCUMENTO
    
    # === CASO A: CONSTANCIA RH (Lleva flujo de firmas) ===
    if tipo == 'constancia_rh':
        # Si nos pasan un ID de solicitud (historial o recibidos), buscamos si está firmado
        if solicitud_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SolicitudesDocumentos WHERE id_solicitud = ?", (solicitud_id,))
            solicitud = cursor.fetchone()
            conn.close()

            if solicitud:
                target_user_id = solicitud['id_docente_solicitante']
                
                # Solo si el estado es 'Firmado', buscamos las imágenes del jefe
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
        
        # Generamos el PDF (Con o sin firma según lo anterior)
        datos_docente = obtener_datos_docente_completo(target_user_id)
        datos_firmante = obtener_datos_firmante_rh()
        pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma)

    # === CASO B: CARTA EXCLUSIVIDAD (Personal, sin flujo de jefe) ===
    elif tipo == 'carta_exclusividad':
        # Este es directo, siempre con los datos del usuario actual
        datos_docente = obtener_datos_docente_completo(target_user_id)
        pdf_buffer = generar_carta_exclusividad(datos_docente)

    else:
        return "Error: Tipo de documento no válido"
    
    # 3. Enviamos el PDF al navegador (Vista Previa)
    # Agregamos fecha al nombre para evitar que el navegador guarde caché
    nombre_archivo = f"Vista_{tipo}_{datetime.now().strftime('%M%S')}.pdf"
    return send_file(pdf_buffer, as_attachment=False, download_name=nombre_archivo, mimetype='application/pdf')


# --- RUTA: DESCARGAR DOCUMENTO ---
@app.route('/descargar_documento/<tipo>')
def descargar_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    solicitud_id = request.args.get('id_solicitud')
    target_user_id = session['user_id']
    datos_firma = None

    # === CASO A: CONSTANCIA RH ===
    if tipo == 'constancia_rh':
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
        datos_firmante = obtener_datos_firmante_rh()
        pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma)

    # === CASO B: CARTA EXCLUSIVIDAD ===
    elif tipo == 'carta_exclusividad':
        datos_docente = obtener_datos_docente_completo(target_user_id)
        pdf_buffer = generar_carta_exclusividad(datos_docente)

    else:
        return "Error: Tipo de documento no válido"

    # Enviamos como DESCARGA
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
    datos_docente = obtener_datos_docente_completo(solicitud['id_docente_solicitante'])
    datos_firmante = obtener_datos_firmante_rh()

    ruta_sello = None
    if solicitud['tipo_documento'] == 'constancia_rh':
        ruta_sello = usuario_jefe['ruta_sello']
    
    datos_firma_visual = {
        'ruta_firma': resolver_ruta_imagen(usuario_jefe['ruta_firma']),
        'ruta_sello': resolver_ruta_imagen(ruta_sello)
    }
    conn.close()

    pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma_visual)
    nombre_archivo = f"Firmado_{solicitud['tipo_documento']}.pdf"
    
    return send_file(pdf_buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')

# ... (Rutas anteriores) ...

# --- RUTA: PROCESAR RECHAZO (JEFE) ---
@app.route('/rechazar_solicitud/<int:id_solicitud>', methods=['POST'])
def rechazar_solicitud(id_solicitud):
    if 'user_id' not in session or session['rol'] != 'jefe':
        return "No autorizado", 403

    motivo = request.form['motivo'] # Obtenemos el texto del modal

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Actualizamos estado a 'Rechazado' y guardamos el motivo
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
    
    # Buscamos solicitudes RECHAZADAS de este usuario
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)