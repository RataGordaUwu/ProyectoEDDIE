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

print("Insertando datos de Licencias (Sabático / Beca Comisión)...")

try:
    # -------------------------------------------------------------------------
    # INSERTAR LICENCIA PARA JOSÉ (DOCENTE 101)
    # -------------------------------------------------------------------------
    # Vamos a registrar un "Periodo Sabático" (id_tipo_licencia = 1).
    # Si quisieras Beca Comisión, solo cambiarías el id_tipo_licencia a 2.
    
    print("- Registrando Oficio de Autorización de Sabático para José...")

    cursor.execute("""
        INSERT OR IGNORE INTO Licencias (
            id_licencia,
            id_docente,
            id_tipo_licencia,
            numero_oficio,
            fecha_oficio,
            fecha_inicio,
            fecha_fin
        ) VALUES (
            3001,               -- ID único de la licencia
            101,                -- José Enrique
            1,                  -- 1 = Periodo Sabático, 2 = Beca Comisión
            'TecNM-ITC-DP-2024/058', -- El número de oficio (Dato clave del documento)
            '2023-11-15',       -- Fecha en que se emitió el oficio
            '2024-02-01',       -- Inicio del sabático
            '2025-01-31'        -- Fin del sabático
        )
    """)

    # Opcional: Si quisieras probar Beca Comisión, podrías descomentar esto:
    # cursor.execute("""
    #     INSERT OR IGNORE INTO Licencias (id_licencia, id_docente, id_tipo_licencia, numero_oficio, fecha_oficio, fecha_inicio, fecha_fin) 
    #     VALUES (3002, 101, 2, 'TecNM-BEC-2025/001', '2024-12-01', '2025-01-01', '2026-01-01')
    # """)

    conn.commit()
    print("¡Inserts realizados con éxito!")
    print("José ahora tiene registrado un Periodo Sabático con oficio 'TecNM-ITC-DP-2024/058'.")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()