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