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

# --- FUNCIÓN 1: CONSTANCIA RH (Ya existente) ---
def generar_constancia_rh(docente, firmante, datos_firma=None):
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
    texto1 = f"La que suscribe, Jefa del Departamento de Administracion de Recursos Humanos del Instituto Tecnologico de Culiacan, hace CONSTAR que el (la) C. <b>{nombre}</b>, con filiación <b>{docente['rfc']}</b>, presta sus servicios en este Instituto desde el <b>{docente['fecha_ingreso']}</b>, a la fecha."
    story.append(Paragraph(texto1, s_body))
    story.append(Spacer(1, 0.5*cm))

    # (Resumido para brevedad, mantener lógica original si se requiere todo el texto RH)
    texto2 = "Se extiende la presente constancia para los fines legales que al(a) interesado(a) convengan."
    story.append(Paragraph(texto2, s_body))
    story.append(Spacer(1, 2*cm))

    # Firma
    story.append(Paragraph("A T E N T A M E N T E", s_firm))
    if datos_firma:
        img_firma = RLImage(datos_firma['ruta_firma'], width=4*cm, height=2*cm) if datos_firma.get('ruta_firma') else Spacer(1, 2*cm)
        img_sello = RLImage(datos_firma['ruta_sello'], width=3*cm, height=3*cm) if datos_firma.get('ruta_sello') else Spacer(1, 2*cm)
        t = Table([[Spacer(1,1), img_firma, img_sello]], colWidths=[3*cm, 5*cm, 4*cm])
        t.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(t)
    else:
        story.append(Spacer(1, 2*cm))

    bloque = f"<b>{firmante['nombre']} {firmante['apellidos']}</b><br/>{firmante['nombre_puesto'].upper()}"
    story.append(Paragraph(bloque, s_firm))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Excelencia en Educación Tecnológica®", s_slogan))

    doc.build(story)
    buffer.seek(0)
    return buffer


# --- FUNCIÓN 2: CARTA EXCLUSIVIDAD (Ya existente) ---
def generar_carta_exclusividad(docente):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story.append(Paragraph("CARTA EXCLUSIVIDAD LABORAL", style_center))
    # ... (Lógica existente) ...
    story.append(Paragraph("Documento generado.", style_center))
    doc.build(story)
    buffer.seek(0)
    return buffer


# --- FUNCIÓN 3: CONSTANCIA SERVICIOS ESCOLARES (NUEVA) ---
def generar_constancia_servicios_escolares(docente, firmante, datos_tabla, datos_firma=None):
    buffer = io.BytesIO()
    # Márgenes ajustados visualmente a la imagen
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=2*cm)
    
    # Estilos específicos
    s_top_inst = ParagraphStyle('TopInst', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica', fontSize=8)
    s_top_depto = ParagraphStyle('TopDepto', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=9)
    s_asunto = ParagraphStyle('Asunto', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=9)
    
    s_destinatario_bold = ParagraphStyle('DestBold', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=10, leading=12)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, fontName='Helvetica', fontSize=10, leading=13)
    
    s_table_header = ParagraphStyle('TabHead', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=8)
    s_table_cell = ParagraphStyle('TabCell', parent=styles['Normal'], alignment=TA_CENTER, fontName='Helvetica', fontSize=8)
    s_table_cell_left = ParagraphStyle('TabCellL', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica', fontSize=8)
    
    s_firma_cargo = ParagraphStyle('FirmaCargo', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=9)
    s_firma_nombre = ParagraphStyle('FirmaNombre', parent=styles['Normal'], alignment=TA_LEFT, fontName='Helvetica-Bold', fontSize=10)

    story = []

    # 1. Encabezado Superior Derecho
    story.append(Paragraph("Instituto Tecnológico de Culiacán", s_top_inst))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Depto. de Servicios Escolares", s_top_depto))
    story.append(Paragraph("Asunto: Constancia.", s_asunto))
    story.append(Spacer(1, 1.5*cm))

    # 2. Destinatario
    destinatario = """
    COMISIÓN DE EVALUACIÓN DEL TECNM<br/>
    PROGRAMA DE ESTIMULOS AL DESEMPEÑO DEL PERSONAL DOCENTE<br/>
    DE LOS INSTITUTOS TECNOLÓGICOS FEDERALES Y CENTROS<br/>
    P R E S E N T E.-
    """
    story.append(Paragraph(destinatario, s_destinatario_bold))
    story.append(Spacer(1, 0.5*cm))

    # 3. Cuerpo del texto
    nombre_completo = f"{docente['nombre']} {docente['apellidos']}"
    # Usamos id_docente como expediente por ahora
    expediente = str(docente['id_docente']) 
    texto = f"""
    La que suscribe, hace constar que según registros que existen en el archivo escolar, la C. <b>{nombre_completo}</b>, 
    expediente <b>{expediente}</b> impartió las siguientes materias durante los Periodos Enero-Junio y Agosto-Diciembre del año 2024:
    """
    story.append(Paragraph(texto, s_body))
    story.append(Spacer(1, 0.5*cm))

    # 4. Tabla Dinámica
    # Encabezados
    data = [[
        Paragraph("PERIODO", s_table_header),
        Paragraph("NIVEL", s_table_header),
        Paragraph("CLAVE DE LA MATERIA", s_table_header),
        Paragraph("NOMBRE DE LA MATERIA", s_table_header),
        Paragraph("ALUMNOS ATENDIDOS", s_table_header)
    ]]

    total_alumnos = 0
    
    # Filas dinámicas
    for fila in datos_tabla:
        # Fila: [Periodo, Nivel, Clave, Nombre, Cantidad]
        row_cells = [
            Paragraph(fila['periodo'], s_table_cell),
            Paragraph(fila['nivel'], s_table_cell),
            Paragraph(fila['clave'], s_table_cell),
            Paragraph(fila['nombre_materia'], s_table_cell_left),
            Paragraph(str(fila['alumnos']), s_table_cell)
        ]
        data.append(row_cells)
        total_alumnos += fila['alumnos']

    # Fila de Total
    data.append([
        '', '', '', 
        Paragraph("<b>Total</b>", ParagraphStyle('TotalRight', parent=s_table_cell, alignment=TA_RIGHT)), 
        Paragraph(f"<b>{total_alumnos}</b>", s_table_header)
    ])

    # Estilo de Tabla
    # Anchos aproximados: Total ~17cm. 
    # Cols: 3cm, 3cm, 3cm, 6cm, 2cm
    t = Table(data, colWidths=[2.8*cm, 2.8*cm, 2.5*cm, 6.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-2), 0.5, 'BLACK'), # Grid en todo menos la ultima fila
        ('BOX', (-2,-1), (-1,-1), 0.5, 'BLACK'), # Box solo en las celdas de total
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # 5. Texto final
    texto_final = "Se extiende la presente, en la ciudad de Culiacán, Sinaloa, a los nueve días del mes de junio de dos mil veinticinco, para los fines que más convengan al interesado."
    story.append(Paragraph(texto_final, s_body))
    story.append(Spacer(1, 2*cm))

    # 6. Firma (Alineada a la izquierda/centro visualmente como imagen)
    story.append(Paragraph("A T E N T A M E N T E", s_firma_nombre))
    story.append(Paragraph("<i>Excelencia en Educación Tecnológica®</i>", ParagraphStyle('SloganSmall', parent=styles['Normal'], fontSize=8)))
    
    # Espacio para firma/sello
    if datos_firma:
        # Tabla invisible para poner firma sobre nombre
        img_firma = RLImage(datos_firma['ruta_firma'], width=3.5*cm, height=1.5*cm) if datos_firma.get('ruta_firma') else Spacer(1, 1.5*cm)
        # Sello un poco a la derecha o sobrepuesto (aquí lo pondremos al lado para no complicar reportlab sin coordenadas)
        t_firma = Table([[img_firma]], colWidths=[5*cm])
        t_firma.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT')]))
        story.append(t_firma)
    else:
        story.append(Spacer(1, 1.5*cm))

    # Nombre y Cargo
    bloque_firma = f"{firmante['nombre']} {firmante['apellidos']}<br/>{firmante['nombre_puesto']}"
    story.append(Paragraph(bloque_firma.upper(), s_firma_nombre))

    doc.build(story)
    buffer.seek(0)
    return buffer