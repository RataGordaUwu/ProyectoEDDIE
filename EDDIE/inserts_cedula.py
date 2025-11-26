import sqlite3
import os


db_filename = 'EDDI.db'


if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Insertando datos para evidencia de Cédula y Grado...")



try:
    
    print("- Registrando grados académicos...")
    cursor.execute("""
        INSERT OR IGNORE INTO Docente_Escolaridad (id_docente, id_escolaridad) 
        VALUES (101, 3) -- 3 = Doctorado
    """)

    
    print("- Registrando existencia de documentos (Evidencias)...")
    
    
    cursor.execute("""
        INSERT OR IGNORE INTO EvidenciasProfesionales (id_evidencia, id_docente, tipo_documento) 
        VALUES (1001, 101, 'Cédula Profesional - Maestría en Ciencias')
    """)

    
    cursor.execute("""
        INSERT OR IGNORE INTO EvidenciasProfesionales (id_evidencia, id_docente, tipo_documento) 
        VALUES (1002, 101, 'Acta de Examen de Grado - Doctorado')
    """)

    
    
    print("- Simulando datos del Acta de Examen (Fecha y Tesis)...")

    
    cursor.execute("""
        INSERT OR IGNORE INTO Alumnos (id_alumno, numero_control, nombre, apellidos, id_institucion)
        VALUES (99101, 'DOC-PHD-101', 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', 2)
    """)

    
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