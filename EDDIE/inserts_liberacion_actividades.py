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
    # -------------------------------------------------------------------------
    # 1. CREAR EL "ORGANISMO" QUE LIBERA (EL DEPARTAMENTO)
    # -------------------------------------------------------------------------
    # Usamos la tabla OrganismosAcademicos para representar al Depto. que emite la liberación.
    print("1. Registrando 'Departamento de Sistemas' como organismo emisor...")
    
    cursor.execute("""
        INSERT OR IGNORE INTO OrganismosAcademicos (id_organismo_acad, nombre, tipo)
        VALUES (10, 'Departamento de Sistemas y Computación', 'Departamento')
    """)

    # -------------------------------------------------------------------------
    # 2. REGISTRAR LAS ACTIVIDADES DE LOS DOS SEMESTRES
    # -------------------------------------------------------------------------
    # Registramos dos entradas en ActividadesAcademicas para José (ID 101),
    # una para cada semestre. Aunque la tabla no tiene campo 'periodo', 
    # la 'fecha_liberacion' en la siguiente tabla nos servirá para distinguirlos.
    
    print("2. Registrando actividades sujetas a liberación...")

    # Actividad Semestre 1 (Ene-Jun 2024)
    cursor.execute("""
        INSERT OR IGNORE INTO ActividadesAcademicas (id_actividad_acad, id_docente, id_organismo_acad, estado)
        VALUES (20241, 101, 10, 'LIBERADO')
    """)

    # Actividad Semestre 2 (Ago-Dic 2024)
    cursor.execute("""
        INSERT OR IGNORE INTO ActividadesAcademicas (id_actividad_acad, id_docente, id_organismo_acad, estado)
        VALUES (20242, 101, 10, 'LIBERADO')
    """)

    # -------------------------------------------------------------------------
    # 3. REGISTRAR LAS FECHAS DE LIBERACIÓN (CONSTANCIAS)
    # -------------------------------------------------------------------------
    # Aquí es donde definimos a qué periodo corresponde cada una mediante la fecha.
    
    print("3. Generando registros de fechas de liberación...")

    # Liberación Enero-Junio 2024 (Se libera al final del semestre, ej: Junio)
    cursor.execute("""
        INSERT OR IGNORE INTO LiberacionesAcademicas (id_liberacion, id_actividad_acad, fecha_liberacion)
        VALUES (6001, 20241, '2024-06-28')
    """)

    # Liberación Agosto-Diciembre 2024 (Se libera al final o inicio del sig, ej: Enero 2025)
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