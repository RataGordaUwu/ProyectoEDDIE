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

print("--- Insertando datos para Constancia de Evaluación Docente (2024) ---")

try:
    # =========================================================================
    # 1. CREAR FUNCIONARIOS FALTANTES (PARA LAS FIRMAS)
    # =========================================================================
    print("1. Creando registros de docentes para los nuevos funcionarios...")

    # A) Subdirector Académico (ID 996)
    cursor.execute("""
        INSERT OR IGNORE INTO Docentes (
            id_docente, nombre, apellidos, id_departamento, id_plaza, id_institucion, estatus
        ) VALUES (
            996, 'CARLOS ARTURO', 'MÉNDEZ RÍOS', 
            1, -- Depto Sistemas (Origen)
            1, -- Plaza Titular C
            2, -- Tec Culiacán
            'ACTIVO'
        )
    """)

    # B) Jefa de la DEPI (ID 997)
    cursor.execute("""
        INSERT OR IGNORE INTO Docentes (
            id_docente, nombre, apellidos, id_departamento, id_plaza, id_institucion, estatus
        ) VALUES (
            997, 'LAURA ELENA', 'RIVERA SOTO', 
            4, -- Depto Posgrado (Origen)
            4, -- Profesor Investigador
            2, -- Tec Culiacán
            'ACTIVO'
        )
    """)

    # =========================================================================
    # 2. ASIGNAR PUESTOS ADMINISTRATIVOS
    # =========================================================================
    print("2. Asignando puestos administrativos...")

    # Aseguramos que existan los puestos en el catálogo
    # ID 4: Subdirector Académico
    cursor.execute("""
        INSERT OR IGNORE INTO PuestosAdministrativos (id_puesto, nombre_puesto, id_departamento)
        VALUES (4, 'Subdirector Académico', 1)
    """)

    # ID 12: Jefe de la DEPI
    cursor.execute("""
        INSERT OR IGNORE INTO PuestosAdministrativos (id_puesto, nombre_puesto, id_departamento)
        VALUES (12, 'Jefa de la División de Estudios de Posgrado e Investigación', 4)
    """)

    # Asignar los puestos a los docentes creados
    # Carlos -> Subdirector (Puesto 4)
    cursor.execute("""
        INSERT OR IGNORE INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio)
        VALUES (50, 4, 996, '2023-01-15')
    """)

    # Laura -> Jefa DEPI (Puesto 12)
    cursor.execute("""
        INSERT OR IGNORE INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio)
        VALUES (51, 12, 997, '2023-01-15')
    """)

    # =========================================================================
    # 3. INSERTAR EVALUACIONES DE JOSÉ (ID 101) - AÑO 2024
    # =========================================================================
    print("3. Registrando evaluaciones del 2024 para José Enrique...")

    # --- PERIODO 1: Enero-Junio 2024 ---
    # Evaluación Departamental
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202401, 101, 1, 1, '4.85', '2024-06-25', 30
        )
    """)
    # Autoevaluación
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202402, 101, 1, 3, 'Excelente', '2024-06-20', 0
        )
    """)

    # --- PERIODO 2: Agosto-Diciembre 2024 ---
    # Evaluación Departamental
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202403, 101, 2, 1, '4.92', '2025-01-10', 28
        )
    """)
    # Autoevaluación
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202404, 101, 2, 3, 'Excelente', '2025-01-08', 0
        )
    """)
    
    # Evaluación de Posgrado (Extra para cubrir requisito específico)
    cursor.execute("""
        INSERT OR IGNORE INTO TiposEvaluacion (id_tipo_evaluacion, nombre_evaluacion, aplica_a_nivel)
        VALUES (4, 'Evaluación de Posgrado', 'Posgrado')
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO EvaluacionesDocentes (
            id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, 
            calificacion_global, fecha_evaluacion, alumnos_participantes
        ) VALUES (
            202405, 101, 2, 4, '4.95', '2025-01-12', 5
        )
    """)

    # =========================================================================
    # 4. CREAR USUARIOS Y FIRMAS (NUEVO: NECESARIO PARA PDF)
    # =========================================================================
    print("4. Registrando usuarios y firmas para los funcionarios...")

    # Registramos a los nuevos jefes en la tabla Usuarios para que el sistema tenga sus firmas.
    # Usamos las rutas genéricas que ya existen en tu proyecto.
    
    # Usuario para el Subdirector (Carlos)
    cursor.execute("""
        INSERT OR REPLACE INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello)
        VALUES (
            996, 
            '123', 
            'jefe', 
            'static/firmas/firma.png', 
            'static/firmas/sello.png'
        )
    """)

    # Usuario para la Jefa DEPI (Laura)
    cursor.execute("""
        INSERT OR REPLACE INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello)
        VALUES (
            997, 
            '123', 
            'jefe', 
            'static/firmas/firma_yareli.png', -- Usamos la otra firma para variar visualmente, o puedes usar firma.png
            'static/firmas/sello.png'
        )
    """)

    conn.commit()
    print("\n¡Proceso completado con éxito!")
    print("- Funcionarios creados y asignados.")
    print("- Evaluaciones 2024 registradas.")
    print("- Usuarios con firmas configurados (Carlos: firma.png, Laura: firma_yareli.png).")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()