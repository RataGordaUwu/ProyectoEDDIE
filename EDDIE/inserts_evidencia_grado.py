import sqlite3
import os
from datetime import datetime

# Nombre de la base de datos
db_filename = 'EDDI.db'

# Verificar que la BD existe
if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("--- Insertando datos de Evidencia de Grado para José Enrique (ID 101) ---")

try:
    # 1. ASIGNAR GRADO ACADÉMICO (DOCTORADO)
    # ---------------------------------------------------------
    # Aseguramos que José tenga registrado el nivel de Doctorado en su escolaridad.
    # ID 3 corresponde a Doctorado según el catálogo en db_sqlite.py
    print("1. Asignando nivel de Doctorado...")
    cursor.execute("""
        INSERT OR IGNORE INTO Docente_Escolaridad (id_docente, id_escolaridad) 
        VALUES (101, 3) 
    """)

    # 2. CREAR ALUMNO 'FICTICIO' PARA VINCULAR EL ACTA
    # ---------------------------------------------------------
    # El sistema requiere un ID de alumno para registrar el acta. 
    # Usamos la convención 99000 + ID_Docente (99101) para vincularlo internamente.
    print("2. Creando registro temporal de alumno egresado...")
    cursor.execute("""
        INSERT OR IGNORE INTO Alumnos (id_alumno, numero_control, nombre, apellidos, id_institucion)
        VALUES (99101, 'DOC-PHD-101', 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', 2)
    """)

    # 3. REGISTRAR ACTA DE EXAMEN (Opción B del requisito)
    # ---------------------------------------------------------
    # Cumpliendo la regla de "máximo un año de haber obtenido el mismo".
    # Fecha de examen simulada: 20 de Mayo de 2024 (Reciente)
    print("3. Registrando Acta de Examen de Grado (Fecha reciente < 1 año)...")
    
    cursor.execute("""
        INSERT OR IGNORE INTO ActasExamen (
            id_acta, 
            id_alumno_titulado, 
            id_opcion_titulacion, 
            id_carrera, 
            nombre_trabajo, 
            fecha_examen
        ) VALUES (
            2024,   -- ID del acta
            99101,  -- ID vinculado a José
            3,      -- Opción: Proyecto de Investigación / Tesis (según catálogo)
            3,      -- Carrera: Maestría/Doctorado en Ciencias
            'Arquitectura de Microservicios para la Gestión Educativa en el TecNM', -- Tesis
            '2024-05-20' -- FECHA: Debe ser menor a 1 año para ser válida según la regla
        )
    """)

    # 4. REGISTRAR EVIDENCIA DIGITAL (Referencia al archivo físico)
    # ---------------------------------------------------------
    # Esto indica que el documento físico/PDF ya fue 'entregado' o 'validado'.
    print("4. Registrando validación de documento en Evidencias...")
    cursor.execute("""
        INSERT OR IGNORE INTO EvidenciasProfesionales (id_evidencia, id_docente, tipo_documento) 
        VALUES (1002, 101, 'Acta de Examen de Grado - Doctorado')
    """)

    conn.commit()
    print("\n¡Datos insertados correctamente!")
    print("José Enrique ahora cumple con los requisitos para generar la 'Constancia de Grado' usando su Acta de Examen.")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()