import sqlite3
import os

db_filename = 'EDDI.db'

if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}.")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("--- Configurando Jefe de Departamento de Sistemas (Para firma de Evaluaciones) ---")

try:
    # 1. ASIGNAR EL PUESTO A ROBERTO SÁNCHEZ (ID 103)
    # ---------------------------------------------------------
    # El puesto ID 1 es "Jefe de Departamento Académico" y está ligado al Depto 1 (Sistemas)
    # en el archivo db_sqlite.py original.
    print("1. Asignando a Roberto Sánchez Ruiz como Jefe de Sistemas...")
    
    cursor.execute("""
        INSERT OR REPLACE INTO AsignacionPuestos (
            id_asignacion, 
            id_puesto, 
            id_docente, 
            fecha_inicio
        ) VALUES (
            100, 
            1,    -- ID Puesto: Jefe de Departamento Académico
            103,  -- ID Docente: Roberto Sánchez Ruiz
            '2023-01-15'
        )
    """)

    # 2. CREAR USUARIO Y FIRMA PARA ROBERTO
    # ---------------------------------------------------------
    # Necesario para que el sistema pueda estampar la imagen 'firma.png' en el PDF.
    print("2. Registrando firma digital para el Jefe de Sistemas...")
    
    cursor.execute("""
        INSERT OR REPLACE INTO Usuarios (
            id_usuario, 
            contrasena, 
            rol, 
            ruta_firma, 
            ruta_sello
        ) VALUES (
            103, 
            '123', 
            'jefe', 
            'static/firmas/firma.png', 
            'static/firmas/sello.png'
        )
    """)

    conn.commit()
    print("\n¡Listo! Ahora Roberto Sánchez Ruiz (ID 103) es el Jefe de Sistemas.")
    print("Al generar la constancia de evaluación, aparecerá su nombre y firma.")

except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    conn.close()
    