from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
import os
from datetime import datetime 


from pdf_creator import (
    generar_constancia_rh, 
    generar_carta_exclusividad, 
    generar_constancia_desarrollo, 
    generar_constancia_cvu,
    generar_constancia_grado,               
    generar_constancia_participacion_planes, 
    generar_oficio_licencia,                
    generar_evidencia_grado_firmable,
    generar_constancia_liberacion_actividades,
    generar_constancia_evaluacion,
    generar_constancia_desempeno
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

def get_db_connection():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'EDDI.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def resolver_ruta_imagen(ruta_relativa):
    if not ruta_relativa:
        return None
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_completa = os.path.join(base_dir, ruta_relativa)
    return os.path.normpath(ruta_completa)



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


def obtener_datos_grado(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    

    cursor.execute("""
        SELECT e.nombre_titulo 
        FROM Docente_Escolaridad de
        JOIN Escolaridades e ON de.id_escolaridad = e.id_escolaridad
        WHERE de.id_docente = ?
        ORDER BY de.id_escolaridad DESC LIMIT 1
    """, (user_id,))
    grado_res = cursor.fetchone()
    titulo_grado = grado_res['nombre_titulo'] if grado_res else "GRADO NO REGISTRADO"


    id_alumno_ficticio = 99000 + int(user_id) 
    
    cursor.execute("""
        SELECT ae.fecha_examen, ae.nombre_trabajo 
        FROM ActasExamen ae
        WHERE ae.id_alumno_titulado = ? OR ae.id_alumno_titulado = ?
    """, (id_alumno_ficticio, 99101)) 
    acta_res = cursor.fetchone()


    cursor.execute("SELECT registro_cvu FROM Docentes WHERE id_docente = ?", (user_id,))
    docente_res = cursor.fetchone()
    cedula = docente_res['registro_cvu'] if docente_res else "SIN DATO"

    conn.close()

    datos_grado = {'titulo': titulo_grado}

    if acta_res:
        datos_grado['tipo_evidencia'] = 'Acta de Examen'
        datos_grado['fecha_examen'] = acta_res['fecha_examen']
        datos_grado['nombre_trabajo'] = acta_res['nombre_trabajo']
    else:
        datos_grado['tipo_evidencia'] = 'Cédula'
        datos_grado['cedula'] = cedula
        
    return datos_grado


def obtener_datos_participacion_planes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
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


def obtener_datos_licencia(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.*, tl.nombre_licencia, tl.descripcion
        FROM Licencias l
        JOIN TiposLicencia tl ON l.id_tipo_licencia = tl.id_tipo_licencia
        WHERE l.id_docente = ?
        ORDER BY l.fecha_inicio DESC LIMIT 1
    """
    cursor.execute(query, (user_id,))
    dato = cursor.fetchone()
    conn.close()
    return dato




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
    
    
    
    query = """
        SELECT s.*, d.nombre, d.apellidos 
        FROM SolicitudesDocumentos s
        JOIN Docentes d ON s.id_docente_solicitante = d.id_docente
        WHERE s.id_usuario_destinatario = ? AND s.estado LIKE 'Pendiente%'
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



@app.route('/enviar_documento/<tipo>', methods=['POST']) 
def enviar_documento(tipo):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    solicitante_id = session['user_id']
    destinatario_id = None
    estado_inicial = 'Pendiente' 
    
    
    if tipo == 'constancia_rh' or tipo == 'oficio_licencia':
        destinatario_id = buscar_id_destinatario_por_puesto('Recursos Humanos')
    
    
    elif tipo in ['constancia_desarrollo', 'constancia_cvu', 'constancia_grado']: 
        destinatario_id = buscar_id_destinatario_por_puesto('Desarrollo Académico')

    
    elif tipo == 'constancia_evaluacion':
        jefe_data = obtener_jefe_inmediato(solicitante_id)
        if jefe_data:
            destinatario_id = jefe_data['id_docente']

    
    elif tipo == 'constancia_desempeno':
        
        destinatario_id = 998 
        estado_inicial = 'Pendiente_Desarrollo'
    
    
    if destinatario_id:
        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute("""
            SELECT id_solicitud FROM SolicitudesDocumentos 
            WHERE id_docente_solicitante = ? 
            AND tipo_documento = ? 
            AND estado IN ('Pendiente', 'Pendiente_Desarrollo', 'Pendiente_Subdireccion')
        """, (solicitante_id, tipo))
        
        existe = cursor.fetchone()

        if existe:
            flash("Ya tienes una solicitud en proceso para este documento.")
        else:
            cursor.execute("""
                INSERT INTO SolicitudesDocumentos (id_docente_solicitante, id_usuario_destinatario, tipo_documento, estado)
                VALUES (?, ?, ?, ?)
            """, (solicitante_id, destinatario_id, tipo, estado_inicial))
            conn.commit()
            flash("Documento enviado correctamente a revisión.")
        
        conn.close()
    else:
        flash("Error: No se encontró destinatario para este trámite.")
        
    return redirect(url_for('generar_documentos'))



@app.route('/ver_documento/<tipo>')
def ver_documento(tipo):
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
    pdf_buffer = None

    
    
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

    
    elif tipo == 'constancia_grado':
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)

    elif tipo == 'constancia_participacion_planes':
        datos_participacion = obtener_datos_participacion_planes(target_user_id)
        pdf_buffer = generar_constancia_participacion_planes(datos_docente, datos_participacion, None)

    elif tipo == 'oficio_licencia':
        datos_firmante = obtener_datos_firmante_rh()
        datos_licencia = obtener_datos_licencia(target_user_id)
        pdf_buffer = generar_oficio_licencia(datos_docente, datos_licencia, datos_firmante, datos_firma)

    

    elif tipo == 'constancia_grado':
        
        datos_grado = obtener_datos_grado(target_user_id)
        
        
        pdf_buffer = generar_evidencia_grado_firmable(datos_docente, datos_grado)

    
    elif tipo == 'constancia_liberacion':
        datos_liberacion = obtener_datos_liberacion(target_user_id)
        pdf_buffer = generar_constancia_liberacion_actividades(datos_docente, datos_liberacion)

    
    
    elif tipo == 'constancia_evaluacion':
        evaluaciones = obtener_datos_evaluaciones(target_user_id)
        
        datos_firmante = obtener_jefe_inmediato(target_user_id) 
        
        
        if not datos_firmante:
            datos_firmante = {"nombre": "JEFE", "apellidos": "DEPARTAMENTO", "nombre_puesto": "Jefe Inmediato"}
            
        pdf_buffer = generar_constancia_evaluacion(datos_docente, evaluaciones, datos_firmante, datos_firma)
    
    
    
    elif tipo == 'constancia_desempeno':
        evaluaciones = obtener_datos_desempeno(target_user_id)
        datos_yareli = obtener_datos_jefe_usuario(998)
        datos_carlos = obtener_datos_jefe_usuario(996)
        firmas_mostrar = {}

        
        if solicitud_id:
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT estado FROM SolicitudesDocumentos WHERE id_solicitud = ?", (solicitud_id,))
            res = cursor.fetchone()
            conn.close()
            
            estado = res['estado'] if res else ''
            
            
            if estado == 'Pendiente_Subdireccion':
                
                firmas_mostrar['desarrollo'] = resolver_ruta_imagen(datos_yareli['ruta_firma'])
            elif estado == 'Firmado':
                
                firmas_mostrar['desarrollo'] = resolver_ruta_imagen(datos_yareli['ruta_firma'])
                firmas_mostrar['subdireccion'] = resolver_ruta_imagen(datos_carlos['ruta_firma'])
        
        pdf_buffer = generar_constancia_desempeno(datos_docente, evaluaciones, datos_yareli, datos_carlos, firmas_mostrar)
    
    else:
        return "Error: Tipo de documento no válido"
    
    nombre_archivo = f"Vista_{tipo}_{datetime.now().strftime('%M%S')}.pdf"
    return send_file(pdf_buffer, as_attachment=False, download_name=nombre_archivo, mimetype='application/pdf')



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
    pdf_buffer = None

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
    elif tipo == 'constancia_grado':
        datos_firmante = obtener_datos_firmante_desarrollo()
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma)
    elif tipo == 'constancia_participacion_planes':
        datos_participacion = obtener_datos_participacion_planes(target_user_id)
        pdf_buffer = generar_constancia_participacion_planes(datos_docente, datos_participacion, None)
    elif tipo == 'oficio_licencia':
        datos_firmante = obtener_datos_firmante_rh()
        datos_licencia = obtener_datos_licencia(target_user_id)
        pdf_buffer = generar_oficio_licencia(datos_docente, datos_licencia, datos_firmante, datos_firma)

    

    elif tipo == 'constancia_grado':
        datos_grado = obtener_datos_grado(target_user_id)
        pdf_buffer = generar_evidencia_grado_firmable(datos_docente, datos_grado)

    
    elif tipo == 'constancia_liberacion':
        datos_liberacion = obtener_datos_liberacion(target_user_id)
        pdf_buffer = generar_constancia_liberacion_actividades(datos_docente, datos_liberacion)

    
    
    elif tipo == 'constancia_evaluacion':
        evaluaciones = obtener_datos_evaluaciones(target_user_id)
        
        datos_firmante = obtener_jefe_inmediato(target_user_id) 
        
        
        if not datos_firmante:
            datos_firmante = {"nombre": "JEFE", "apellidos": "DEPARTAMENTO", "nombre_puesto": "Jefe Inmediato"}
            
        pdf_buffer = generar_constancia_evaluacion(datos_docente, evaluaciones, datos_firmante, datos_firma)

    
    
    elif tipo == 'constancia_desempeno':
        evaluaciones = obtener_datos_desempeno(target_user_id)
        datos_yareli = obtener_datos_jefe_usuario(998)
        datos_carlos = obtener_datos_jefe_usuario(996)
        firmas_mostrar = {}

        
        if solicitud_id:
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT estado FROM SolicitudesDocumentos WHERE id_solicitud = ?", (solicitud_id,))
            res = cursor.fetchone()
            conn.close()
            
            estado = res['estado'] if res else ''
            
            
            if estado == 'Pendiente_Subdireccion':
                
                firmas_mostrar['desarrollo'] = resolver_ruta_imagen(datos_yareli['ruta_firma'])
            elif estado == 'Firmado':
                
                firmas_mostrar['desarrollo'] = resolver_ruta_imagen(datos_yareli['ruta_firma'])
                firmas_mostrar['subdireccion'] = resolver_ruta_imagen(datos_carlos['ruta_firma'])
        
        pdf_buffer = generar_constancia_desempeno(datos_docente, evaluaciones, datos_yareli, datos_carlos, firmas_mostrar)
    
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
    
    
    cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = ? AND contrasena = ?", (user_id, password))
    usuario_jefe = cursor.fetchone()

    if not usuario_jefe:
        flash("Contraseña incorrecta.")
        conn.close()
        return redirect(url_for('recibidos'))

    
    cursor.execute("SELECT * FROM SolicitudesDocumentos WHERE id_solicitud = ?", (id_solicitud,))
    solicitud = cursor.fetchone()
    
    if not solicitud:
        conn.close()
        return "Solicitud no encontrada", 404

    tipo_doc = solicitud['tipo_documento']
    estado_actual = solicitud['estado']
    target_id = solicitud['id_docente_solicitante']
    
    
    datos_docente = obtener_datos_docente_completo(target_id)
    
    
    datos_firma_visual = {
        'ruta_firma': resolver_ruta_imagen(usuario_jefe['ruta_firma']),
        'ruta_sello': resolver_ruta_imagen(usuario_jefe['ruta_sello'])
    }

    pdf_buffer = None


    if tipo_doc == 'constancia_desempeno':
        
        if estado_actual == 'Pendiente_Desarrollo':
            
            nuevo_estado = 'Pendiente_Subdireccion'
            nuevo_destinatario = 996 
            
            cursor.execute("""
                UPDATE SolicitudesDocumentos 
                SET estado = ?, id_usuario_destinatario = ?
                WHERE id_solicitud = ?
            """, (nuevo_estado, nuevo_destinatario, id_solicitud))
            conn.commit()
            
            
            evaluaciones = obtener_datos_desempeno(target_id)
            datos_yareli = obtener_datos_jefe_usuario(998)
            datos_carlos = obtener_datos_jefe_usuario(996)
            
            
            rutas_firmas = {'desarrollo': resolver_ruta_imagen(usuario_jefe['ruta_firma'])}
            
            pdf_buffer = generar_constancia_desempeno(datos_docente, evaluaciones, datos_yareli, datos_carlos, rutas_firmas)

        elif estado_actual == 'Pendiente_Subdireccion':
            
            fecha_firma = datetime.now()
            cursor.execute("""
                UPDATE SolicitudesDocumentos 
                SET estado = 'Firmado', fecha_firma = ?
                WHERE id_solicitud = ?
            """, (fecha_firma, id_solicitud))
            conn.commit()
            
            
            evaluaciones = obtener_datos_desempeno(target_id)
            datos_yareli = obtener_datos_jefe_usuario(998)
            datos_carlos = obtener_datos_jefe_usuario(996)
            
            rutas_firmas = {
                'desarrollo': resolver_ruta_imagen(datos_yareli['ruta_firma']), 
                'subdireccion': resolver_ruta_imagen(usuario_jefe['ruta_firma']) 
            }
            pdf_buffer = generar_constancia_desempeno(datos_docente, evaluaciones, datos_yareli, datos_carlos, rutas_firmas)

    
    else:
        
        fecha_firma = datetime.now()
        cursor.execute("""
            UPDATE SolicitudesDocumentos 
            SET estado = 'Firmado', fecha_firma = ?
            WHERE id_solicitud = ?
        """, (fecha_firma, id_solicitud))
        conn.commit()

        
        if tipo_doc == 'constancia_rh':
            datos_firmante = obtener_datos_firmante_rh()
            pdf_buffer = generar_constancia_rh(datos_docente, datos_firmante, datos_firma_visual)
        
        elif tipo_doc == 'constancia_desarrollo':
            datos_firmante = obtener_datos_firmante_desarrollo()
            pdf_buffer = generar_constancia_desarrollo(datos_docente, datos_firmante, datos_firma_visual)
            
        elif tipo_doc == 'constancia_cvu':
            datos_firmante = obtener_datos_firmante_desarrollo()
            pdf_buffer = generar_constancia_cvu(datos_docente, datos_firmante, datos_firma_visual)
            
        elif tipo_doc == 'constancia_grado':
            datos_grado = obtener_datos_grado(target_id)
            datos_firmante = obtener_datos_firmante_desarrollo()
            pdf_buffer = generar_constancia_grado(datos_docente, datos_grado, datos_firmante, datos_firma_visual)
            
        elif tipo_doc == 'oficio_licencia':
            datos_licencia = obtener_datos_licencia(target_id)
            datos_firmante = obtener_datos_firmante_rh()
            pdf_buffer = generar_oficio_licencia(datos_docente, datos_licencia, datos_firmante, datos_firma_visual)

        elif tipo_doc == 'constancia_evaluacion':
            evaluaciones = obtener_datos_evaluaciones(target_id)
            
            
            cursor.execute("""
                SELECT nombre_puesto FROM PuestosAdministrativos pa
                JOIN AsignacionPuestos ap ON pa.id_puesto = ap.id_puesto
                WHERE ap.id_docente = ? AND ap.fecha_fin IS NULL
            """, (user_id,))
            puesto_res = cursor.fetchone()
            
            
            datos_jefe_dict = dict(obtener_datos_docente_completo(user_id))
            datos_jefe_dict['nombre_puesto'] = puesto_res['nombre_puesto'] if puesto_res else "JEFE AUTORIZADO"
            
            pdf_buffer = generar_constancia_evaluacion(datos_docente, evaluaciones, datos_jefe_dict, datos_firma_visual)

    conn.close()

    if pdf_buffer:
        nombre_archivo = f"Firmado_{tipo_doc}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')
    else:
        return "Error: Tipo de documento desconocido al generar firma."


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


def obtener_datos_liberacion(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT la.fecha_liberacion, aa.estado
        FROM LiberacionesAcademicas la
        JOIN ActividadesAcademicas aa ON la.id_actividad_acad = aa.id_actividad_acad
        WHERE aa.id_docente = ? AND (aa.id_actividad_acad = 20241 OR aa.id_actividad_acad = 20242)
        ORDER BY la.fecha_liberacion ASC
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_datos_evaluaciones(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT ed.*, te.nombre_evaluacion 
        FROM EvaluacionesDocentes ed
        JOIN TiposEvaluacion te ON ed.id_tipo_evaluacion = te.id_tipo_evaluacion
        WHERE ed.id_docente = ? AND ed.id_periodo IN (1, 2)
        ORDER BY ed.id_periodo ASC
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos

# 
def obtener_jefe_inmediato(docente_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT id_departamento FROM Docentes WHERE id_docente = ?", (docente_id,))
    res = cursor.fetchone()
    id_depto = res['id_departamento'] if res else 1
    

    
    puesto_clave = '%Estudios de Posgrado%' if id_depto == 4 else '%Jefe de Departamento%'
    
    query_jefe = """
        SELECT d.id_docente, d.nombre, d.apellidos, pa.nombre_puesto 
        FROM AsignacionPuestos ap
        JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
        JOIN Docentes d ON ap.id_docente = d.id_docente
        WHERE pa.nombre_puesto LIKE ? AND ap.fecha_fin IS NULL AND pa.id_departamento = ?
    """
    
    cursor.execute(query_jefe, (puesto_clave, id_depto))
    jefe = cursor.fetchone()
    
    
    if not jefe:
        cursor.execute("""
            SELECT d.id_docente, d.nombre, d.apellidos, pa.nombre_puesto 
            FROM AsignacionPuestos ap
            JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
            JOIN Docentes d ON ap.id_docente = d.id_docente
            WHERE pa.nombre_puesto LIKE '%Jefe de Departamento%' LIMIT 1
        """)
        jefe = cursor.fetchone()
        
    conn.close()
    return jefe


def obtener_datos_desempeno(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM EvaluacionesDocentes 
        WHERE id_docente = ? AND id_tipo_evaluacion = 2 
        ORDER BY id_periodo ASC
    """
    cursor.execute(query, (user_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_datos_jefe_usuario(user_id_jefe):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT d.nombre, d.apellidos, pa.nombre_puesto, u.ruta_firma, u.ruta_sello
        FROM Docentes d
        JOIN AsignacionPuestos ap ON d.id_docente = ap.id_docente
        JOIN PuestosAdministrativos pa ON ap.id_puesto = pa.id_puesto
        LEFT JOIN Usuarios u ON d.id_docente = u.id_usuario
        WHERE d.id_docente = ? AND ap.fecha_fin IS NULL
    """
    cursor.execute(query, (user_id_jefe,))
    datos = cursor.fetchone()
    conn.close()
    return datos

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)