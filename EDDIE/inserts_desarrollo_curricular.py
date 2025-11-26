import sqlite3
import os

db_filename = 'EDDI.db'

# Verificar que la BD existe
if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Insertando datos para Desarrollo Curricular (Planes y Programas)...")

try:
    # -------------------------------------------------------------------------
    # 1. INSERTAR EL EVENTO DE DISEÑO CURRICULAR
    # -------------------------------------------------------------------------
    # Registramos la reunión nacional como un 'Evento Académico'.
    # Usamos un ID (ej. 4) que no choque con los existentes (1, 2, 3).
    print("- Registrando Reunión Nacional de Diseño Curricular...")
    
    cursor.execute("""
        INSERT OR IGNORE INTO EventosAcademicos (
            id_evento_acad, 
            nombre, 
            siglas, 
            organizador, 
            ambito
        ) VALUES (
            4, 
            'Reunión Nacional de Diseño e Innovación Curricular de la Carrera de Ingeniería en Sistemas Computacionales', 
            'RNDIC-ISC', 
            'TecNM', 
            'Nacional'
        )
    """)

    # -------------------------------------------------------------------------
    # 2. INSERTAR LA PARTICIPACIÓN DE JOSÉ (DOCENTE 101)
    # -------------------------------------------------------------------------
    # Usamos la tabla 'CoordinacionEventos' porque tiene la estructura perfecta:
    # - id_docente: 101 (José)
    # - id_evento_acad: 4 (El evento creado arriba)
    # - numero_oficio_comision: 'ITC-DIR-099/2024' (El requisito clave)
    # - rol: 'Representante Institucional' o 'Participante'
    # - id_periodo: 1 (Enero-Junio 2024)
    
    print("- Registrando participación y Oficio de Comisión de José...")

    cursor.execute("""
        INSERT OR IGNORE INTO CoordinacionEventos (
            id_coordinacion, 
            id_docente, 
            id_evento_acad, 
            id_periodo, 
            rol, 
            numero_oficio_comision, 
            actividades_desarrolladas
        ) VALUES (
            5001, -- ID único para esta participación
            101,  -- José Enrique
            4,    -- El evento de Diseño Curricular
            1,    -- Periodo Enero-Junio 2024
            'Representante Institucional en Diseño Curricular', 
            'ITC-DIR-099/2024', 
            'Análisis, elaboración y actualización de los programas de estudio de la especialidad en Ingeniería de Software.'
        )
    """)

    conn.commit()
    print("¡Inserts realizados con éxito!")
    print("Datos listos para generar la constancia de Desarrollo Curricular.")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()