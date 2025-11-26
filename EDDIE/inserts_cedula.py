import sqlite3
import os

# Nombre de la base de datos
db_filename = 'EDDI.db'

# Verificar que la BD existe
if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Insertando datos para evidencia de Cédula y Grado...")

# =========================================================================
# ESTRATEGIA DE INSERCIÓN PARA CUMPLIR EL REQUERIMIENTO
# =========================================================================
# El documento requiere evidencia de:
# 1. Cédula Profesional (SEP)
# 2. O Copia del Acta de Examen de Grado (Reciente < 1 año)
# Para Profesor con Doctorado o Maestría.
# =========================================================================

try:
    # 1. ASEGURAR GRADOS ACADÉMICOS PARA JOSÉ (ID 101)
    # ---------------------------------------------------------------------
    # Ya tenía Maestría (2), le agregamos Doctorado (3) para cumplir el perfil completo.
    print("- Registrando grados académicos...")
    cursor.execute("""
        INSERT OR IGNORE INTO Docente_Escolaridad (id_docente, id_escolaridad) 
        VALUES (101, 3) -- 3 = Doctorado
    """)

    # 2. REGISTRAR LA EVIDENCIA FÍSICA (EL DOCUMENTO CARGADO)
    # ---------------------------------------------------------------------
    # Usamos la tabla 'EvidenciasProfesionales' para indicar que José ya subió estos PDFs.
    print("- Registrando existencia de documentos (Evidencias)...")
    
    # Evidencia de la Cédula de Maestría
    cursor.execute("""
        INSERT OR IGNORE INTO EvidenciasProfesionales (id_evidencia, id_docente, tipo_documento) 
        VALUES (1001, 101, 'Cédula Profesional - Maestría en Ciencias')
    """)

    # Evidencia del Acta de Examen de Doctorado (Reciente)
    cursor.execute("""
        INSERT OR IGNORE INTO EvidenciasProfesionales (id_evidencia, id_docente, tipo_documento) 
        VALUES (1002, 101, 'Acta de Examen de Grado - Doctorado')
    """)

    # 3. SIMULAR DATOS DETALLADOS DEL ACTA DE EXAMEN
    # ---------------------------------------------------------------------
    # Como la tabla 'ActasExamen' se liga a 'Alumnos', registramos a José 
    # temporalmente como "Alumno Egresado" para poder guardar los datos 
    # de su tesis y fecha de examen (necesario para validar que sea < 1 año).
    
    print("- Simulando datos del Acta de Examen (Fecha y Tesis)...")

    # a) Registrar a José como Alumno (Egresado de Posgrado)
    cursor.execute("""
        INSERT OR IGNORE INTO Alumnos (id_alumno, numero_control, nombre, apellidos, id_institucion)
        VALUES (99101, 'DOC-PHD-101', 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', 2)
    """)

    # b) Crear el Acta de Examen (Fecha reciente para cumplir el requisito)
    # Suponemos que se graduó hace 6 meses (cumple < 1 año)
    cursor.execute("""
        INSERT OR IGNORE INTO ActasExamen (
            id_acta, 
            id_alumno_titulado, 
            id_opcion_titulacion, 
            id_carrera, 
            nombre_trabajo, 
            fecha_examen
        ) VALUES (
            2024, -- ID del acta
            99101, -- José como alumno
            1, -- Tesis
            3, -- Maestría/Doctorado en Ciencias (Usamos ID carrera 3 del catálogo)
            'Arquitectura de Microservicios para la Gestión Educativa en el TecNM', -- Tesis
            '2024-05-20' -- Fecha reciente (< 1 año desde hoy)
        )
    """)

    # c) Registrar el Jurado de ese examen (Opcional, pero da robustez)
    # Ponemos a otros docentes como su jurado
    cursor.execute("""
        INSERT OR IGNORE INTO JuradoExamen (id_jurado, id_acta, id_docente, rol)
        VALUES (501, 2024, 102, 'Presidente') -- María González
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO JuradoExamen (id_jurado, id_acta, id_docente, rol)
        VALUES (502, 2024, 103, 'Secretario') -- Roberto Sánchez
    """)

    conn.commit()
    print("¡Inserts realizados con éxito!")
    print("Ahora José (101) tiene:")
    print("  1. Grado de Doctorado en Docente_Escolaridad.")
    print("  2. Registro de documentos en EvidenciasProfesionales.")
    print("  3. Datos de su Acta de Examen (tesis, fecha) en ActasExamen.")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()