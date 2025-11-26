import sqlite3
import os

db_filename = 'EDDI.db'

if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("--- Insertando Evaluaciones de Alumnos (Frente a Grupo) para José Enrique (2024) ---")

try:
    
    
    print("1. Registrando calificaciones de los alumnos (Ene-Jun y Ago-Dic)...")

    
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202406, 
            101, -- José Enrique
            1,   -- Ene-Jun 2024
            2,   -- Tipo 2: Evaluación por Alumnos (Frente a Grupo)
            '4.88', -- Calificación alta (Suficiente)
            '2024-06-15', 
            35   -- Alta participación para cumplir el >60%
        )
    """)

    
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202407, 
            101, -- José Enrique
            2,   -- Ago-Dic 2024
            2,   -- Tipo 2: Evaluación por Alumnos (Frente a Grupo)
            '4.91', 
            '2024-12-10', 
            32
        )
    """)

    
    print("2. Configurando firmantes requeridos...")

    
    cursor.execute("""
        INSERT OR REPLACE INTO Usuarios (
            id_usuario, contrasena, rol, ruta_firma, ruta_sello
        ) VALUES (
            998, '123', 'jefe', 
            'static/firmas/firma_yareli.png', 
            'static/firmas/sello.png'
        )
    """)
    
    
    cursor.execute("""
        INSERT OR IGNORE INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio)
        VALUES (2, 2, 998, '2023-01-01') -- Puesto 2 = Jefe Desarrollo Académico
    """)

    
    cursor.execute("""
        INSERT OR IGNORE INTO Docentes (id_docente, nombre, apellidos, id_departamento, id_plaza, id_institucion, estatus) 
        VALUES (996, 'CARLOS ARTURO', 'MÉNDEZ RÍOS', 1, 1, 2, 'ACTIVO')
    """)
    
    cursor.execute("""
        INSERT OR REPLACE INTO Usuarios (
            id_usuario, contrasena, rol, ruta_firma, ruta_sello
        ) VALUES (
            996, '123', 'jefe', 
            'static/firmas/firma.png', 
            'static/firmas/sello.png'
        )
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio)
        VALUES (50, 4, 996, '2023-01-15') -- Puesto 4 = Subdirector Académico
    """)

    conn.commit()
    print("\n¡Datos listos!")
    print("- Evaluaciones de alumnos insertadas para José Enrique.")
    print("- Firmantes configurados: Yareli (Desarrollo) y Carlos (Subdirección).")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()