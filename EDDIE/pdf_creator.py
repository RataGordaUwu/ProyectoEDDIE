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

    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    story.append(Spacer(1, 2.5*cm)) 
    
    bloque_firma = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto'].upper()}"
    story.append(Paragraph(bloque_firma, s_firm))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("C.c.p. Subdirección Académica.<br/>C.c.p. Expediente.", s_cc))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer