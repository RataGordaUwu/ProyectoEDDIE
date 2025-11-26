from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT, TA_LEFT
import io
import os

# --- FUNCIÓN 1: CONSTANCIA RH (Con firma y sello) ---
def generar_constancia_rh(docente, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_to_whom = ParagraphStyle('ToWhom', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=12, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []

    # Encabezado
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>DEPTO. DE ADMON. DE REC. HUMANOS<br/>DARH-0288/VI/2025", s_header))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("A QUIEN CORRESPONDA:", s_to_whom))

    # Cuerpo
    nombre = f"{docente['nombre']} {docente['apellidos']}"
    texto1 = f"La que suscribe, Jefa del Departamento de Administracion de Recursos Humanos del Instituto Tecnologico de Culiacan, hace CONSTAR que el (la) C. <b>{nombre}</b>, con filiación <b>{docente['rfc']}</b>, presta sus servicios en este Instituto desde el <b>{docente['fecha_ingreso']}</b>, a la fecha."
    story.append(Paragraph(texto1, s_body))
    story.append(Spacer(1, 0.5*cm))

    texto2 = f"Tenía hasta el 1º de Enero de 2024, la(s) categoría(s) de <b>{docente['nombre_plaza']}</b> estatus <b>{docente['estatus']}</b>, y actualmente goza de la(s) categoría(s) <b>{docente['nombre_plaza']}</b>, con la clave de: <b>{docente['clave_presupuestal']}</b>, con efectos desde el 01 de Octubre de 2023, con estatus <b>{docente['estatus']}</b> presupuestal."
    story.append(Paragraph(texto2, s_body))
    story.append(Spacer(1, 0.5*cm))

    texto3 = "No cuenta con ninguna sanción durante el periodo comprendido del 1º de Enero al 31 de Diciembre de 2024, el (la) maestro(a) mencionado(a) cumplió con más del 90% de su jornada laboral y horario de trabajo."
    story.append(Paragraph(texto3, s_body))
    story.append(Spacer(1, 0.5*cm))

    texto4 = "Se extiende la presente constancia para los fines legales que al(a) interesado(a) convengan, en la ciudad de Culiacán, Sinaloa, a los nueve días del mes de Junio del año dos mil veinticinco."
    story.append(Paragraph(texto4, s_body))
    story.append(Spacer(1, 1.5*cm))

    # --- ÁREA DE FIRMA ---
    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    
    # Objetos por defecto (espacios vacíos)
    img_firma = Spacer(1, 2*cm)
    img_sello = Spacer(1, 2*cm)

    # Lógica para cargar imágenes (Sin try/except ciego para ver errores en consola)
    if datos_firma:
        # 1. FIRMA
        ruta_f = datos_firma.get('ruta_firma')
        if ruta_f and os.path.exists(ruta_f):
            print(f"Cargando firma desde: {ruta_f}") # Debug en terminal
            img_firma = RLImage(ruta_f, width=4*cm, height=2*cm)
        else:
            print(f"No se encontró archivo de firma en: {ruta_f}")

        # 2. SELLO
        ruta_s = datos_firma.get('ruta_sello')
        if ruta_s and os.path.exists(ruta_s):
            print(f"Cargando sello desde: {ruta_s}") # Debug en terminal
            img_sello = RLImage(ruta_s, width=3*cm, height=3*cm)
    
    # Tabla para alinear: [Espacio Izq, Firma, Sello]
    # Anchos: 3cm aire, 5cm firma, 4cm sello (Total 12cm, cabe bien)
    tabla_firma_data = [[Spacer(1,1), img_firma, img_sello]]
    
    t = Table(tabla_firma_data, colWidths=[3*cm, 5*cm, 4*cm])
    t.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,0), 'CENTER'), # Firma centrada en su celda
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alineación vertical
    ]))
    
    story.append(t)

    # Nombre del firmante
    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto'].upper()}"
    story.append(Paragraph(bloque, s_firm))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer


# --- FUNCIÓN 2: CARTA EXCLUSIVIDAD (Mantenemos la versión optimizada) ---
def generar_carta_exclusividad(docente):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    styles = getSampleStyleSheet()

    s_center_bold = ParagraphStyle('CenterBold', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=12, leading=14)
    s_center_small_bold = ParagraphStyle('CenterSmallBold', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10, leading=12)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14)
    s_firm_name = ParagraphStyle('FirmName', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_firm_line = ParagraphStyle('FirmLine', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica', fontSize=11, leading=14)
    s_footer = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=8, leading=10)

    story = []
    story.append(Paragraph("CARTA EXCLUSIVIDAD LABORAL", s_center_bold))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("DOCENTES CON PLAZA DE TIEMPO COMPLETO*", s_center_small_bold))
    story.append(Spacer(1, 0.8*cm))

    nombre_completo = f"{docente['nombre']} {docente['apellidos']}"
    texto_cuerpo = f"""
    El (la) que suscribe <b>{nombre_completo}</b>, con filiación: <b>{docente['rfc']}</b>, 
    con clave presupuestal: <b>{docente['clave_presupuestal']}</b>, 
    por medio de este documento manifiesto MI COMPROMISO con el Tecnológico Nacional de México, 
    campus <b>{docente['nombre_institucion']}</b>, declaro que en caso de haber laborado en otra(s) 
    institución(es) pública(s) o federal(es), la jornada no excedió las 12 horas-semanas-mes durante 
    el periodo a evaluar del estímulo, y en caso estar laborando en otra(s) institución(es), la jornada 
    no excederá las 12 horas-semanas-mes y los horarios establecidos para el desempeño de las mismas, 
    por lo que autorizo que se revise con el departamento de recursos humanos, la compatibilidad de horarios 
    de mi institución de adscripción.
    <br/><br/>
    Asimismo, manifiesto mi disposición para realizar las actividades propias de la Educación Superior Tecnológica 
    enfocadas a satisfacer las necesidades de la dedicación, la calidad en el desempeño y permanencia en las 
    actividades de la docencia, que la autoridad correspondiente de mi institución me encomiende y podré realizar 
    estudios de posgrado siempre y cuando estas actividades sean compatibles con la carga horaria reglamentaria 
    asignada, en el entendido de que en todos los productos derivados de mis actividades como profesor de tiempo 
    completo de la institución, tales como: patentes, modelos de utilidad, derechos de autor, publicaciones en 
    revistas, congresos y libros, mencionaré mi adscripción al Tecnológico Nacional de México, excepto con 
    autorización por escrito por el TecNM. Adicionalmente me comprometo a no incurrir en conflicto de intereses.
    <br/><br/>
    En caso de que se me compruebe la NO EXCLUSIVIDAD LABORAL, me haré acreedor a la aplicación de las sanciones 
    correspondientes de la normatividad vigente y perderé de manera permanente el derecho a participar en el 
    Programa de Estímulos al Desempeño del Personal Docente.¹
    """
    story.append(Paragraph(texto_cuerpo.strip(), s_body))
    story.append(Spacer(1, 1.5*cm))

    story.append(Paragraph("ATENTAMENTE", s_center_bold))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("____________________________________________", s_firm_line))
    story.append(Paragraph(nombre_completo, s_firm_name))
    story.append(Paragraph("Nombre y firma del docente", s_firm_line))

    story.append(Spacer(1, 1*cm))
    nota_pie = "¹ Artículo 05 de los Lineamientos para la Operación del Programa de Estímulos al Desempeño del Personal Docente para los Institutos Tecnológicos Federales y Centros 2025."
    story.append(Paragraph(nota_pie, s_footer))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNCIÓN 3: CONSTANCIA DESARROLLO ACADÉMICO ---
def generar_constancia_desarrollo(docente, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos
    s_header_right = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=12, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=8)

    story = []

    # Encabezado
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>Departamento de Desarrollo Académico", s_header_right))
    story.append(Spacer(1, 1.5*cm))
    
    story.append(Paragraph("CONSTANCIA DE NO INCONVENIENTE", s_title))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph("A QUIEN CORRESPONDA:", ParagraphStyle('To', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)))
    story.append(Spacer(1, 0.5*cm))

    # Cuerpo
    nombre_completo = f"{docente['nombre']} {docente['apellidos']}"
    # NOTA: Simulo datos de evaluación (Periodo y Calificación) ya que no están en la BD simplificada
    texto = f"""
    La que suscribe, <b>{firmante['nombre_puesto']}</b>, hace CONSTAR que el (la) C. <b>{nombre_completo}</b>, 
    con R.F.C. <b>{docente['rfc']}</b>, presentó la Cédula de Evaluación al Desempeño Docente 
    correspondiente al periodo <b>Enero-Junio 2024</b>, obteniendo una calificación de <b>98.50 (Excelente)</b>.
    <br/><br/>
    Por lo anterior, este departamento a mi cargo no tiene inconveniente en que realice los trámites correspondientes.
    """
    story.append(Paragraph(texto.strip(), s_body))
    story.append(Spacer(1, 1*cm))

    texto_cierre = "A petición de la persona interesada para los fines legales que a la misma convengan, se extiende la presente en la ciudad de Culiacán, Sinaloa, a los veinticinco días del mes de Noviembre del año dos mil veinticinco."
    story.append(Paragraph(texto_cierre, s_body))
    story.append(Spacer(1, 2*cm))

    # Firma
    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    
    img_firma = Spacer(1, 2*cm)
    img_sello = Spacer(1, 2*cm)

    if datos_firma:
        if datos_firma.get('ruta_firma') and os.path.exists(datos_firma['ruta_firma']):
            try: img_firma = RLImage(datos_firma['ruta_firma'], width=4*cm, height=2*cm)
            except: pass
        if datos_firma.get('ruta_sello') and os.path.exists(datos_firma['ruta_sello']):
            try: img_sello = RLImage(datos_firma['ruta_sello'], width=3*cm, height=3*cm)
            except: pass

    # Tabla de firma (Igual que la de RH)
    tabla_firma_data = [[Spacer(1,1), img_firma, img_sello]]
    t = Table(tabla_firma_data, colWidths=[3*cm, 5*cm, 4*cm])
    t.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t)

    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto'].upper()}"
    story.append(Paragraph(bloque, s_firm))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ... (Imports anteriores) ...

# --- FUNCIÓN 4: CONSTANCIA CVU (Desarrollo Académico) ---
def generar_constancia_cvu(docente, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos
    s_header_right = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_destinatario = ParagraphStyle('Dest', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=11, leading=14, spaceAfter=15)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_firm = ParagraphStyle('Firm', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=11, leading=14)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []

    # 1. Encabezado (Derecha)
    header_text = """
    Instituto Tecnológico de Culiacán<br/>
    Culiacán, Sinaloa,<br/>
    DEPTO. DE DESARROLLO ACADÉMICO<br/>
    Núm. de Oficio: DDA-476-06-2025
    """
    story.append(Paragraph(header_text, s_header_right))
    story.append(Spacer(1, 1.5*cm))

    # 2. Destinatario (Izquierda)
    story.append(Paragraph("H. COMISION DICTAMINADORA DEL EDD<br/>PRESENTE", s_destinatario))
    story.append(Spacer(1, 0.5*cm))

    # 3. Cuerpo
    # Usamos las variables de la BD para que coincida con quien firma realmente
    nombre_jefa = f"{firmante['nombre']} {firmante['apellidos']}"
    puesto_jefa = firmante['nombre_puesto']
    
    intro = f"La que suscribe <b>{nombre_jefa}</b>, {puesto_jefa} del Instituto Tecnológico de Culiacán."
    story.append(Paragraph(intro, s_body))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("<b>HACE CONSTAR</b>", ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold')))
    story.append(Spacer(1, 0.5*cm))

    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    registro_cvu = docente['registro_cvu'] if docente['registro_cvu'] else "SIN REGISTRO"

    texto_principal = f"""
    Que el (la) C. <b>{nombre_docente}</b> cuenta con el registro <b>{registro_cvu}</b>, así como la actualización de su Currículum Vitae (CVU-TecNM) en el portal https://cvu.dpil.tecnm.mx correspondiente al año 2024, entregando en formato electrónico su CVU en extenso al Departamento De Desarrollo Académico.
    """
    story.append(Paragraph(texto_principal.strip(), s_body))
    story.append(Spacer(1, 1*cm))

    texto_cierre = "A solicitud del interesado y para los fines que al mismo convenga se extiende la presente a los diez días del mes de junio del año dos mil veinticinco."
    story.append(Paragraph(texto_cierre, s_body))
    story.append(Spacer(1, 2*cm))

    # 4. Firma
    story.append(Paragraph("ATENTAMENTE", s_firm))
    
    img_firma = Spacer(1, 2*cm)
    img_sello = Spacer(1, 2*cm)

    if datos_firma:
        if datos_firma.get('ruta_firma') and os.path.exists(datos_firma['ruta_firma']):
            try: img_firma = RLImage(datos_firma['ruta_firma'], width=4*cm, height=2*cm)
            except: pass
        if datos_firma.get('ruta_sello') and os.path.exists(datos_firma['ruta_sello']):
            try: img_sello = RLImage(datos_firma['ruta_sello'], width=3*cm, height=3*cm)
            except: pass

    tabla_firma_data = [[Spacer(1,1), img_firma, img_sello]]
    t = Table(tabla_firma_data, colWidths=[3*cm, 5*cm, 4*cm])
    t.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t)

    bloque = f"<b>{nombre_jefa}</b><br/>{puesto_jefa.upper()}"
    story.append(Paragraph(bloque, s_firm))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph('"Excelencia en Educación Tecnológica"', s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNCIÓN 5: CONSTANCIA DE GRADO / CÉDULA (Versión Sin Firma) ---
def generar_constancia_grado(docente, grado_info, firmante, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos Personalizados
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_destinatario = ParagraphStyle('Dest', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=12, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_list_item = ParagraphStyle('ListItem', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica', fontSize=11, leading=14, leftIndent=20)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []

    # 1. Encabezado
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>DIVISIÓN DE ESTUDIOS DE POSGRADO E INVESTIGACIÓN<br/>Oficio No. DEPI-2025/089", s_header))
    story.append(Spacer(1, 1.5*cm))

    # 2. Destinatario
    story.append(Paragraph("Evidencia de la cédula profesional.", s_destinatario))
    story.append(Spacer(1, 0.5*cm))

    # 3. Cuerpo (Redacción impersonal)
    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    
    # Cambio: "Se hace CONSTAR" en lugar de "El que suscribe..."
    texto_intro = f"Por medio de la presente, la División de Estudios de Posgrado e Investigación hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, adscrito(a) a este Instituto, ha acreditado fehacientemente contar con el grado académico de:"
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 0.5*cm))

    # Nombre del Grado
    grado_titulo = grado_info.get('titulo', 'GRADO ACADÉMICO SUPERIOR').upper()
    story.append(Paragraph(f"<b>{grado_titulo}</b>", ParagraphStyle('Grado', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14)))
    story.append(Spacer(1, 0.5*cm))

    # Detalles de la Evidencia
    story.append(Paragraph("Mediante la presentación del siguiente documento probatorio:", s_body))
    story.append(Spacer(1, 0.5*cm))

    if grado_info.get('tipo_evidencia') == 'Acta de Examen':
        texto_evidencia = f"""
        <b>ACTA DE EXAMEN DE GRADO</b><br/>
        Nombre del Trabajo: <b>"{grado_info.get('nombre_trabajo', 'N/A')}"</b><br/>
        Fecha de Examen: <b>{grado_info.get('fecha_examen', 'N/A')}</b>
        """
        story.append(Paragraph(texto_evidencia, s_list_item))
    else:
        texto_evidencia = f"""
        <b>CÉDULA PROFESIONAL ELECTRÓNICA</b><br/>
        Número de Registro: <b>{grado_info.get('cedula', 'EN TRÁMITE')}</b>
        """
        story.append(Paragraph(texto_evidencia, s_list_item))

    story.append(Spacer(1, 2*cm))

    # Cierre
    texto_cierre = "Se extiende la presente constancia para los fines legales correspondientes, en la ciudad de Culiacán, Sinaloa, a los veinticinco días del mes de Noviembre del año dos mil veinticinco."
    story.append(Paragraph(texto_cierre, s_body))
    story.append(Spacer(1, 3*cm))

    # 4. Pie de página (Solo eslogan, sin firma)
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNCIÓN 6: CONSTANCIA DE DISEÑO CURRICULAR (Sin firma, Informativa) ---
def generar_constancia_participacion_planes(docente, participacion, datos_firma=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos
    s_header = ParagraphStyle('HeaderRight', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10, leading=14)
    s_title = ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=14, spaceAfter=20)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=18)
    s_list_label = ParagraphStyle('ListLabel', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=11, leading=14, leftIndent=20)
    s_list_content = ParagraphStyle('ListContent', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=11, leading=14, leftIndent=30, spaceAfter=5)
    s_slogan = ParagraphStyle('Slogan', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)

    story = []

    # 1. Encabezado
    story.append(Paragraph("Instituto Tecnológico de Culiacán<br/>SUBDIRECCIÓN ACADÉMICA<br/>Depto. de Desarrollo Académico", s_header))
    story.append(Spacer(1, 1.5*cm))

    # 2. Título
    story.append(Paragraph("CONSTANCIA DE PARTICIPACIÓN EN DISEÑO CURRICULAR", s_title))
    story.append(Spacer(1, 1*cm))

    # 3. Cuerpo
    nombre_docente = f"{docente['nombre']} {docente['apellidos']}"
    texto_intro = f"Por medio de la presente se hace CONSTAR que el (la) C. <b>{nombre_docente}</b>, docente adscrito(a) a este Instituto, participó activamente en la elaboración y/o actualización de planes y programas de estudio, conforme a los registros oficiales obrantes en este departamento."
    story.append(Paragraph(texto_intro, s_body))
    story.append(Spacer(1, 1*cm))

    # 4. Detalles de la Participación (Datos de los Inserts)
    if participacion:
        # Evento
        story.append(Paragraph("Evento / Actividad:", s_list_label))
        story.append(Paragraph(participacion['nombre_evento'], s_list_content))
        story.append(Spacer(1, 0.2*cm))

        # Rol y Oficio
        story.append(Paragraph("Rol de Participación:", s_list_label))
        story.append(Paragraph(f"{participacion['rol']} (Oficio No. {participacion['numero_oficio_comision']})", s_list_content))
        story.append(Spacer(1, 0.2*cm))

        # Periodo
        story.append(Paragraph("Periodo de realización:", s_list_label))
        story.append(Paragraph(participacion['nombre_periodo'], s_list_content))
        story.append(Spacer(1, 0.2*cm))
        
        # Actividades
        if participacion['actividades_desarrolladas']:
            story.append(Paragraph("Actividades desarrolladas:", s_list_label))
            story.append(Paragraph(participacion['actividades_desarrolladas'], s_list_content))
    else:
        story.append(Paragraph("No se encontró información registrada de participación curricular vigente.", s_body))

    story.append(Spacer(1, 2*cm))

    # 5. Cierre
    texto_cierre = "Se extiende la presente para los fines de acreditación académica correspondientes, en la ciudad de Culiacán, Sinaloa, a los veinticinco días del mes de Noviembre del año dos mil veinticinco."
    story.append(Paragraph(texto_cierre, s_body))
    story.append(Spacer(1, 3*cm))

    # 6. Pie (Sin firma)
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer