import sqlite3
import os

db_filename = 'EDDI.db'

# Verificar existencia de la BD
if not os.path.exists(db_filename):
    print(f"Error: No se encontró {db_filename}. Ejecuta primero db_sqlite.py")
    exit()

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("--- Insertando Liberación de Actividades Docentes para José Enrique (2024) ---")

try:
    
    print("1. Registrando 'Departamento de Sistemas' como organismo emisor...")
    
    cursor.execute("""
        INSERT OR IGNORE INTO OrganismosAcademicos (id_organismo_acad, nombre, tipo)
        VALUES (10, 'Departamento de Sistemas y Computación', 'Departamento')
    """)

    
    
    print("2. Registrando actividades sujetas a liberación...")

    
    cursor.execute("""
        INSERT OR IGNORE INTO ActividadesAcademicas (id_actividad_acad, id_docente, id_organismo_acad, estado)
        VALUES (20241, 101, 10, 'LIBERADO')
    """)

    
    cursor.execute("""
        INSERT OR IGNORE INTO ActividadesAcademicas (id_actividad_acad, id_docente, id_organismo_acad, estado)
        VALUES (20242, 101, 10, 'LIBERADO')
    """)

    
    
    print("3. Generando registros de fechas de liberación...")

    
    cursor.execute("""
        INSERT OR IGNORE INTO LiberacionesAcademicas (id_liberacion, id_actividad_acad, fecha_liberacion)
        VALUES (6001, 20241, '2024-06-28')
    """)


    cursor.execute("""
        INSERT OR IGNORE INTO LiberacionesAcademicas (id_liberacion, id_actividad_acad, fecha_liberacion)
        VALUES (6002, 20242, '2025-01-15')
    """)

    conn.commit()
    print("\n¡Inserts realizados con éxito!")
    print("Se han registrado las liberaciones de actividades para los periodos:")
    print("  - Enero-Junio 2024 (Fecha: 2024-06-28)")
    print("  - Agosto-Diciembre 2024 (Fecha: 2025-01-15)")

except sqlite3.Error as e:
    print(f"Error al insertar datos: {e}")
finally:
    conn.close()