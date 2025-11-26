from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT, TA_LEFT
import io
import os
from datetime import datetime

# --- ESTILOS COMUNES ---
styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_center = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica', fontSize=10)
style_bold = ParagraphStyle('Bold', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=10)
style_justify = ParagraphStyle('Justify', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14)

# ==========================================
# 1. CONSTANCIA RECURSOS HUMANOS
# ==========================================
def generar_constancia_rh(docente, firmante, datos_firma=None):
    # CORRECCIÓN: Convertimos a diccionario para poder usar .get()
    docente = dict(docente)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_to_whom = ParagraphStyle('ToWhom', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=12, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>DEPTO. DE ADMON. DE REC. HUMANOS<br/>DARH-0288/VI/2025", s_header))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("A QUIEN CORRESPONDA:", s_to_whom))

    nombre = f"{docente['nombre']} {docente['apellidos']}"
    # Ahora .get() funcionará correctamente
    rfc = docente.get('rfc') or 'N/A'
    fecha_ingreso = docente.get('fecha_ingreso') or 'N/A'
    
    texto1 = f"La que suscribe, Jefa del Departamento de Administracion de Recursos Humanos del Instituto Tecnologico de Culiacan, hace CONSTAR que el (la) C. <b>{nombre}</b>, con filiación <b>{rfc}</b>, presta sus servicios en este Instituto desde el <b>{fecha_ingreso}</b>, a la fecha."
    story.append(Paragraph(texto1, s_body))
    story.append(Spacer(1, 0.5*cm))

    texto2 = "Se extiende la presente constancia para los fines legales que al(a) interesado(a) convengan."
    story.append(Paragraph(texto2, s_body))
    story.append(Spacer(1, 2*cm))

    # Firma
    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    
    if datos_firma and datos_firma.get('ruta_firma') and os.path.exists(datos_firma['ruta_firma']):
        try:
            img_firma = RLImage(datos_firma['ruta_firma'], width=4*cm, height=2*cm)
            # El sello es opcional
            if datos_firma.get('ruta_sello') and os.path.exists(datos_firma['ruta_sello']):
                img_sello = RLImage(datos_firma['ruta_sello'], width=3*cm, height=3*cm)
                data_tabla = [[Spacer(1,1), img_firma, img_sello]]
            else:
                data_tabla = [[Spacer(1,1), img_firma, Spacer(1,1)]]
                
            t = Table(data_tabla, colWidths=[3*cm, 5*cm, 4*cm])
            t.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(t)
        except Exception as e:
            print(f"Error cargando imagen firma: {e}")
            story.append(Spacer(1, 2*cm))
    else:
        story.append(Spacer(1, 2*cm))

    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto'].upper()}"
    story.append(Paragraph(bloque, s_firm))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 2. CARTA DE EXCLUSIVIDAD
# ==========================================
def generar_carta_exclusividad(docente):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14)
    
    story = []
    story.append(Paragraph("CARTA EXCLUSIVIDAD LABORAL", s_title))
    story.append(Spacer(1, 1*cm))
    
    nombre = f"{docente['nombre']} {docente['apellidos']}"
    texto = f"""
    El (la) que suscribe <b>{nombre}</b>, por medio de este documento manifiesto MI COMPROMISO con el Tecnologico Nacional de México, 
    campus Culiacán, y declaro que en caso de haber laborado en otra(s) institución(es) pública(s) o federal(es), 
    la jornada no excedió las 12 horas-semanas-mes durante el período a evaluar.
    <br/><br/>
    Me comprometo a no incurrir en conflicto de intereses y a dedicar el tiempo completo a las actividades de docencia e investigación.
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 2*cm))
    
    story.append(Paragraph("A T E N T A M E N T E", ParagraphStyle('Center', alignment=TA_CENTER)))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(f"<b>{nombre}</b>", ParagraphStyle('CenterBold', alignment=TA_CENTER, fontName='Helvetica-Bold')))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 3. CONSTANCIA DE DESARROLLO ACADÉMICO
# ==========================================
def generar_constancia_desarrollo(docente, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11)

    story = []
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Depto. de Desarrollo Académico", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("<b>A QUIEN CORRESPONDA:</b>", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    nombre = f"{docente['nombre']} {docente['apellidos']}"
    texto = f"""
    Por medio de la presente, se hace CONSTAR que no existe inconveniente alguno para que el (la) C. <b>{nombre}</b>, 
    docente adscrito a este Instituto, realice los trámites correspondientes ante las instancias pertinentes para su desarrollo académico y profesional.
    <br/><br/>
    Se extiende la presente a petición del interesado para los fines legales que convengan.
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 2.5*cm))

    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    story.append(Spacer(1, 2*cm))

    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto']}"
    story.append(Paragraph(bloque, s_firm))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 4. CONSTANCIA DE CVU
# ==========================================
def generar_constancia_cvu(docente, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11)

    story = []
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Depto. de Desarrollo Académico", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("<b>ASUNTO:</b> Constancia de Actualización de CVU.", styles['Normal']))
    story.append(Spacer(1, 1*cm))

    nombre = f"{docente['nombre']} {docente['apellidos']}"
    texto = f"""
    La que suscribe, Jefa del Departamento de Desarrollo Académico, hace CONSTAR que el (la) C. <b>{nombre}</b>, 
    cuenta con el registro y actualización de su Currículum Vitae (CVU-TecNM) en el portal oficial correspondiente al año en curso.
    <br/><br/>
    Se extiende la presente para los fines de acreditación y evaluación docente.
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 2.5*cm))

    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    story.append(Spacer(1, 2*cm))

    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto']}"
    story.append(Paragraph(bloque, s_firm))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 5. CONSTANCIA DE GRADO / CÉDULA
# ==========================================
def generar_constancia_grado(docente, grado_info, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_destinatario = ParagraphStyle('Dest', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=12, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_list_item = ParagraphStyle('ListItem', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica', fontSize=11, leading=14, leftIndent=20)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>DIVISIÓN DE ESTUDIOS DE POSGRADO E INVESTIGACIÓN<br/>Oficio No. DEPI-2025/089", s_header))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Evidencia de la cédula profesional.", s_destinatario))
    story.append(Spacer(1, 0.5*cm))

    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    texto_intro = f"Por medio de la presente, la División de Estudios de Posgrado e Investigación hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, adscrito(a) a este Instituto, ha acreditado fehacientemente contar con el grado académico de:"
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 0.5*cm))

    grado_titulo = grado_info.get('titulo', 'GRADO ACADÉMICO SUPERIOR').upper()
    story.append(Paragraph(f"<b>{grado_titulo}</b>", ParagraphStyle('Grado', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14)))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Mediante la presentación del siguiente documento probatorio:", s_body))
    story.append(Spacer(1, 0.5*cm))

    if grado_info.get('tipo_evidencia') == 'Acta de Examen':
        texto_evidencia = f"<b>ACTA DE EXAMEN DE GRADO</b><br/>Nombre del Trabajo: <b>\"{grado_info.get('nombre_trabajo', 'N/A')}\"</b><br/>Fecha de Examen: <b>{grado_info.get('fecha_examen', 'N/A')}</b>"
        story.append(Paragraph(texto_evidencia, s_list_item))
    else:
        texto_evidencia = f"<b>CÉDULA PROFESIONAL ELECTRÓNICA</b><br/>Número de Registro: <b>{grado_info.get('cedula', 'EN TRÁMITE')}</b>"
        story.append(Paragraph(texto_evidencia, s_list_item))

    story.append(Spacer(1, 2*cm))
    texto_cierre = "Se extiende la presente constancia para los fines legales correspondientes, en la ciudad de Culiacán, Sinaloa."
    story.append(Paragraph(texto_cierre, s_body))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 6. CONSTANCIA DE DISEÑO CURRICULAR
# ==========================================
def generar_constancia_participacion_planes(docente, participacion, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_list_label = ParagraphStyle('ListLabel', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=11, leading=14, leftIndent=20)
    s_list_content = ParagraphStyle('ListContent', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14, leftIndent=30, spaceAfter=5)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>SUBDIRECCIÓN ACADÉMICA<br/>Depto. de Desarrollo Académico", s_header))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("CONSTANCIA DE PARTICIPACIÓN EN DISEÑO CURRICULAR", s_title))
    story.append(Spacer(1, 1*cm))

    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    texto_intro = f"Por medio de la presente se hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, docente adscrito(a) a este Instituto, participó activamente en la elaboración y/o actualización de planes y programas de estudio."
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 1*cm))

    if participacion:
        story.append(Paragraph("Evento / Actividad:", s_list_label))
        story.append(Paragraph(participacion['nombre_evento'], s_list_content))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("Rol de Participación:", s_list_label))
        story.append(Paragraph(f"{participacion['rol']} (Oficio No. {participacion['numero_oficio_comision']})", s_list_content))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("Periodo:", s_list_label))
        story.append(Paragraph(participacion['nombre_periodo'], s_list_content))
    else:
        story.append(Paragraph("No se encontró información registrada.", s_body))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Se extiende la presente para los fines de acreditación académica correspondientes.", s_body))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 7. OFICIO DE LICENCIA (SABÁTICO/BECA)
# ==========================================
def generar_oficio_licencia(docente, licencia, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_asunto = ParagraphStyle('Asunto', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11, spaceAfter=20)
    s_destinatario = ParagraphStyle('Dest', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=11, spaceAfter=10)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_cc = ParagraphStyle('CC', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica', fontSize=7, leading=10)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []
    num_oficio = licencia['numero_oficio'] if licencia else "S/N"
    
    story.append(Paragraph(f"Instituto Tecnológico de Culiacán<br/>Subdirección de Servicios Administrativos<br/>Depto. de Recursos Humanos", s_header))
    story.append(Spacer(1, 1*cm))
    
    tipo_licencia = licencia['nombre_licencia'] if licencia else "Licencia"
    story.append(Paragraph(f"<b>ASUNTO:</b> Autorización de {tipo_licencia}.", s_asunto))
    story.append(Paragraph(f"<b>Oficio No.:</b> {num_oficio}", s_asunto))
    
    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    story.append(Paragraph(f"<b>C. {nombre_docente}</b><br/>DOCENTE DEL INSTITUTO<br/>PRESENTE.", s_destinatario))
    story.append(Spacer(1, 0.5*cm))

    if licencia:
        texto_cuerpo = f"""
        Por este conducto y con base en la normatividad vigente, me permito informarle que ha sido <b>AUTORIZADA</b> su solicitud de <b>{tipo_licencia.upper()}</b> ({licencia['descripcion']}), con efectos a partir del <b>{licencia['fecha_inicio']}</b> y concluyendo el <b>{licencia['fecha_fin']}</b>.
        <br/><br/>
        Dicha autorización se emite en cumplimiento a los requisitos establecidos y validados por la Comisión Dictaminadora Docente.
        """
    else:
        texto_cuerpo = "No se encontró registro de licencia vigente para este periodo."

    story.append(Paragraph(texto_cuerpo.strip(), s_body))
    story.append(Spacer(1, 2.5*cm))

    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 8. EVIDENCIA DE GRADO (VALIDACIÓN FIRMABLE)
# ==========================================
def generar_evidencia_grado_firmable(docente, grado_info):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_leyenda = ParagraphStyle('Leyenda', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=12, leading=14, spaceBefore=30)
    s_firma_linea = ParagraphStyle('FirmaLinea', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica', fontSize=11, leading=14)
    s_firma_nombre = ParagraphStyle('FirmaNombre', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []
    
    # Encabezado Institucional
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Subdirección Académica<br/>Depto. de Desarrollo Académico", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    # Título del Documento
    story.append(Paragraph("VALIDACIÓN DE EVIDENCIA DE GRADO ACADÉMICO", s_title))
    story.append(Spacer(1, 1*cm))

    # Cuerpo del documento
    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    grado_titulo = grado_info.get('titulo', 'GRADO ACADÉMICO').upper()
    
    texto_intro = f"""
    Por medio del presente, el (la) C. <b>{nombre_docente}</b>, docente adscrito(a) a este Instituto, hace entrega de la documentación probatoria correspondiente a su grado académico de:
    """
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 0.5*cm))
    
    # Mostrar el Grado
    story.append(Paragraph(f"<b>{grado_titulo}</b>", ParagraphStyle('Grado', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14)))
    story.append(Spacer(1, 1*cm))

    # Detalle de la evidencia presentada
    if grado_info.get('tipo_evidencia') == 'Acta de Examen':
        texto_evidencia = f"""
        <b>Documento presentado:</b> Copia del Acta de Examen de Grado.<br/>
        <b>Nombre del Trabajo:</b> "{grado_info.get('nombre_trabajo', 'N/A')}"<br/>
        <b>Fecha de Examen:</b> {grado_info.get('fecha_examen', 'N/A')}<br/>
        <br/>
        <i>* Se presenta Acta de Examen por tener una antigüedad menor a un año de su obtención, en cumplimiento con los lineamientos vigentes.</i>
        """
    else:
        # Cédula
        texto_evidencia = f"""
        <b>Documento presentado:</b> Cédula Profesional Electrónica.<br/>
        <b>Número de Registro:</b> {grado_info.get('cedula', 'EN TRÁMITE')}<br/>
        <b>Fuente:</b> Dirección General de Profesiones (SEP) / www.cedulaprofesional.sep.gob.mx
        """
    
    story.append(Paragraph(texto_evidencia, s_body))
    story.append(Spacer(1, 2.5*cm))

    # --- SECCIÓN DE FIRMA (LO QUE PIDIÓ EL USUARIO) ---
    
    # Leyenda Obligatoria
    story.append(Paragraph("ES COPIA FIEL DEL ORIGINAL", s_leyenda))
    story.append(Spacer(1, 2*cm)) # Espacio para firmar físicamente

    # Línea de firma
    story.append(Paragraph("_________________________________________", s_firma_linea))
    story.append(Paragraph(f"<b>{nombre_docente}</b>", s_firma_nombre))
    story.append(Paragraph("PERSONA SOLICITANTE", s_firma_linea))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 9. CONSTANCIA DE LIBERACIÓN DE ACTIVIDADES
# ==========================================
def generar_constancia_liberacion_actividades(docente, liberaciones):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_status = ParagraphStyle('Status', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=16, leading=20, textColor='black')
    
    story = []
    
    # Encabezado
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Departamento de Sistemas y Computación<br/>Oficio No. DSC-LIB-2024/558", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    # Título
    story.append(Paragraph("CONSTANCIA DE LIBERACIÓN DE ACTIVIDADES DOCENTES", s_title))
    story.append(Spacer(1, 1*cm))

    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    texto_intro = f"""
    Por medio de la presente se hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, docente adscrito al Departamento de Sistemas y Computación, 
    ha cumplido en tiempo y forma con las actividades encomendadas durante el año 2024.
    <br/><br/>
    A continuación se detallan los periodos evaluados y su estatus correspondiente:
    """
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 1*cm))

    # Tabla de Liberaciones
    if liberaciones:
        data = [['Periodo', 'Fecha de Liberación', 'Estatus']]
        for lib in liberaciones:
            # Determinamos el periodo basado en la fecha (lógica simple para visualización)
            fecha = lib['fecha_liberacion']
            periodo_texto = "Enero-Junio 2024" if "2024-06" in fecha else "Agosto-Diciembre 2024"
            data.append([periodo_texto, fecha, 'LIBERADO'])
    else:
        data = [['Periodo', 'Fecha de Liberación', 'Estatus'], ['2024', 'Sin registro', 'PENDIENTE']]

    t = Table(data, colWidths=[6*cm, 5*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'black'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 1.5*cm))

    # Estatus Final
    story.append(Paragraph("ESTATUS FINAL DEL DOCENTE:", s_title))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("LIBERADO(A)", s_status))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Se extiende la presente para los fines administrativos y de estímulos al desempeño que correspondan.", s_body))
    
    # Sin firma, solo sello digital o informativo
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Este documento es de carácter informativo y no requiere firma autógrafa para su descarga.", ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 10. CONSTANCIA DE EVALUACIÓN DOCENTE (FIRMABLE)
# ==========================================
# ==========================================
# 10. CONSTANCIA DE EVALUACIÓN DOCENTE (FIRMABLE)
# ==========================================
def generar_constancia_evaluacion(docente, evaluaciones, firmante, datos_firma=None):
    # --- CORRECCIÓN IMPORTANTE: Convertir a dict para usar .get() sin errores ---
    docente = dict(docente)
    firmante = dict(firmante)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    
    story = []
    
    # Encabezado (Ahora .get() funcionará correctamente)
    depto_nombre = docente.get('departamento', 'Departamento Académico')
    story.append(Paragraph(f"Instituto Tecnológico de Culiacán<br/>{depto_nombre}<br/>Oficio No. EV-2024/001", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("CONSTANCIA DE EVALUACIÓN DOCENTE", s_title))
    story.append(Spacer(1, 1*cm))

    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    texto = f"""
    El (la) que suscribe, hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, docente adscrito a este departamento, 
    ha cumplido con el proceso de Evaluación al Desempeño Docente correspondiente al año 2024, obteniendo los siguientes resultados:
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 1*cm))

    # Tabla de Resultados
    data = [['Periodo', 'Tipo de Evaluación', 'Calificación', 'Nivel']]
    
    if evaluaciones:
        for ev in evaluaciones:
            # Convertimos también cada fila de evaluación a dict o accedemos por índice si es necesario
            # sqlite3.Row permite acceso por nombre ev['campo']
            periodo = "Ene-Jun 2024" if ev['id_periodo'] == 1 else "Ago-Dic 2024"
            
            # Lógica visual para el tipo de evaluación
            if ev['id_tipo_evaluacion'] == 1:
                tipo = "Departamental"
            elif ev['id_tipo_evaluacion'] == 3:
                tipo = "Autoevaluación"
            else:
                tipo = "Posgrado"
                
            calif = ev['calificacion_global']
            
            # Determinar nivel "SUFICIENTE"
            nivel = "SUFICIENTE" # Por defecto para el demo
            try:
                if float(calif) < 3.7: # Criterio ejemplo numérico
                    nivel = "INSUFICIENTE"
            except:
                pass # Si es texto como "Excelente", se queda en SUFICIENTE

            data.append([periodo, tipo, calif, nivel])
    else:
        data.append(["2024", "Sin registros", "N/A", "N/A"])

    t = Table(data, colWidths=[4*cm, 5*cm, 3*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Se extiende la presente para los fines del Programa de Estímulos al Desempeño.", s_body))
    
    # --- SECCIÓN DE FIRMA ---
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph("A T E N T A M E N T E", s_firm))

    # Insertar imagen de firma si existe
    if datos_firma and datos_firma.get('ruta_firma') and os.path.exists(datos_firma['ruta_firma']):
        try:
            img_firma = RLImage(datos_firma['ruta_firma'], width=4*cm, height=2*cm)
            if datos_firma.get('ruta_sello') and os.path.exists(datos_firma['ruta_sello']):
                img_sello = RLImage(datos_firma['ruta_sello'], width=3*cm, height=3*cm)
                data_tabla = [[Spacer(1,1), img_firma, img_sello]]
            else:
                data_tabla = [[Spacer(1,1), img_firma, Spacer(1,1)]]
                
            t_firma = Table(data_tabla, colWidths=[3*cm, 5*cm, 4*cm])
            t_firma.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(t_firma)
        except:
            story.append(Spacer(1, 2*cm))
    else:
        story.append(Spacer(1, 2*cm)) 

    # Datos del Firmante
    nombre_firmante = f"{firmante['nombre']} {firmante['apellidos']}"
    puesto_firmante = firmante['nombre_puesto']
    
    story.append(Paragraph(f"<b>{nombre_firmante}</b><br/>{puesto_firmante}", s_firm))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", ParagraphStyle('Slogan', alignment=TA_CENTER, fontSize=9, fontName='Helvetica-Oblique')))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 11. CONSTANCIA DESEMPEÑO (DOBLE FIRMA)
# ==========================================
def generar_constancia_desempeno(docente, evaluaciones, firmante_desarrollo, firmante_sub, firmas_actuales={}):
    # firmas_actuales es un dict: {'desarrollo': ruta_img, 'subdireccion': ruta_img}
    docente = dict(docente)
    firmante_desarrollo = dict(firmante_desarrollo)
    firmante_sub = dict(firmante_sub)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=13, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=16)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica', fontSize=9)
    s_firm_bold = ParagraphStyle('FirmBold', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9)

    story = []
    
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Departamento de Desarrollo Académico<br/>Oficio No. DDA-EVAL-2024/099", s_header))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("CONSTANCIA DE EVALUACIÓN DEL DESEMPEÑO DOCENTE FRENTE A GRUPO", s_title))
    story.append(Spacer(1, 1*cm))

    nombre = f"{docente['nombre']} {docente['apellidos']}"
    texto = f"""
    El Departamento de Desarrollo Académico hace CONSTAR que el (la) C. <b>{nombre}</b>, ha cumplido satisfactoriamente con las evaluaciones del desempeño docente frente a grupo correspondientes al periodo 2024.
    <br/><br/>
    Se certifica que las evaluaciones presentadas obtuvieron una calificación mínima de <b>SUFICIENTE</b> y corresponden a la evaluación de al menos el <b>60%</b> del estudiantado atendido, cumpliendo con la normativa vigente.
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 1*cm))

    # Tabla de Detalles
    data = [['Periodo', 'Alumnos Evaluados', 'Calificación', 'Dictamen']]
    
    if evaluaciones:
        for ev in evaluaciones:
            periodo = "Ene-Jun 2024" if ev['id_periodo'] == 1 else "Ago-Dic 2024"
            alumnos = str(ev['alumnos_participantes'])
            calif = ev['calificacion_global']
            data.append([periodo, alumnos, calif, 'SATISFACTORIO'])
    else:
        data.append(["2024", "0", "N/A", "PENDIENTE"])

    t = Table(data, colWidths=[4.5*cm, 4*cm, 3.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 3*cm))

    # --- DOBLE FIRMA ---
    # Preparamos las celdas de la tabla de firmas
    
    # Firma Izquierda: Desarrollo Académico
    firma_img_des = Spacer(1, 2*cm)
    if firmas_actuales.get('desarrollo'):
        try:
            firma_img_des = RLImage(firmas_actuales['desarrollo'], width=3.5*cm, height=1.5*cm)
        except: pass

    # Firma Derecha: Subdirección (Vo. Bo.)
    firma_img_sub = Spacer(1, 2*cm)
    if firmas_actuales.get('subdireccion'):
        try:
            firma_img_sub = RLImage(firmas_actuales['subdireccion'], width=3.5*cm, height=1.5*cm)
        except: pass

    # Textos de los firmantes
    txt_des = [
        firma_img_des,
        Paragraph(f"<b>{firmante_desarrollo['nombre']} {firmante_desarrollo['apellidos']}</b>", s_firm_bold),
        Paragraph(firmante_desarrollo['nombre_puesto'], s_firm)
    ]
    
    txt_sub = [
        firma_img_sub,
        Paragraph(f"<b>{firmante_sub['nombre']} {firmante_sub['apellidos']}</b>", s_firm_bold),
        Paragraph("Vo. Bo. " + firmante_sub['nombre_puesto'], s_firm)
    ]

    # Tabla contenedora de firmas
    tabla_firmas = Table([[txt_des, Spacer(1,1), txt_sub]], colWidths=[8*cm, 1*cm, 8*cm])
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    
    story.append(tabla_firmas)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", ParagraphStyle('Slogan', alignment=TA_CENTER, fontSize=8, fontName='Helvetica-Oblique')))

    doc.build(story)
    buffer.seek(0)
    return buffer