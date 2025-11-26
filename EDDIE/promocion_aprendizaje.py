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

print("--- Insertando datos para PROMOCIÓN DEL APRENDIZAJE (1.1.1 - 1.1.5) ---")

try:
    # =========================================================================
    # 0. DEPENDENCIAS BASE (Instituciones, Carreras, Periodos, Aulas)
    # =========================================================================
    print("0. Verificando dependencias base (Instituciones, Carreras, Periodos)...")

    # Institución
    cursor.execute("INSERT OR IGNORE INTO Instituciones (id_institucion, nombre_institucion) VALUES (2, 'INSTITUTO TECNOLOGICO DE CULIACAN')")
    
    # Carreras
    cursor.execute("INSERT OR IGNORE INTO Carreras (id_carrera, nombre_carrera, nivel) VALUES (1, 'Ingeniería en Sistemas Computacionales', 'Licenciatura')")
    cursor.execute("INSERT OR IGNORE INTO Carreras (id_carrera, nombre_carrera, nivel) VALUES (3, 'Maestría en Ciencias de la Computación', 'Posgrado')")
    
    # Periodos
    cursor.execute("INSERT OR IGNORE INTO PeriodosEscolares (id_periodo, nombre_periodo, fecha_inicio, fecha_fin, tipo_periodo) VALUES (1, 'Enero-Junio 2024', '2024-01-26', '2024-06-30', 'Semestral')")
    cursor.execute("INSERT OR IGNORE INTO PeriodosEscolares (id_periodo, nombre_periodo, fecha_inicio, fecha_fin, tipo_periodo) VALUES (2, 'Agosto-Diciembre 2024', '2024-08-21', '2024-12-15', 'Semestral')")
    
    # Aulas
    cursor.execute("INSERT OR IGNORE INTO Aulas (id_aula, nombre_aula) VALUES (1, 'Laboratorio C1')")
    cursor.execute("INSERT OR IGNORE INTO Aulas (id_aula, nombre_aula) VALUES (2, 'Aula 22')")
    cursor.execute("INSERT OR IGNORE INTO Aulas (id_aula, nombre_aula) VALUES (3, 'Sala Audiovisual')")

    # =========================================================================
    # 0.5. DEPENDENCIAS CRÍTICAS (Plazas, Deptos, DOCENTE 101)
    # =========================================================================
    # ESTE PASO ES CLAVE PARA EVITAR EL ERROR DE FOREIGN KEY
    print("0.5. Asegurando existencia del Docente José Enrique y sus datos...")

    # Departamentos
    cursor.execute("INSERT OR IGNORE INTO Departamentos (id_departamento, nombre) VALUES (1, 'Departamento de Sistemas y Computación')")
    cursor.execute("INSERT OR IGNORE INTO Departamentos (id_departamento, nombre) VALUES (6, 'Departamento de Servicios Escolares')")

    # Plazas (Necesarias para crear docentes)
    cursor.execute("INSERT OR IGNORE INTO Plazas (id_plaza, nombre_plaza, clave_presupuestal) VALUES (1, 'Profesor de Carrera Titular C Tiempo Completo', 'E3817')")

    # EL DOCENTE PROTAGONISTA (José Enrique - ID 101)
    cursor.execute("""
        INSERT OR IGNORE INTO Docentes (
            id_docente, nombre, apellidos, fecha_ingreso, id_departamento, 
            registro_cvu, id_plaza, id_institucion, rfc, curp, estatus
        ) VALUES (
            101, 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', '2020-08-15', 1, 
            'CVU-TEC-2024-001', 1, 2, 'EILJ900815XX1', 'EILJ900815HSRNNS01', 'ACTIVO'
        )
    """)

    # =========================================================================
    # 1. CONFIGURACIÓN DE SERVICIOS ESCOLARES (Jefa Ana María)
    # =========================================================================
    print("1. Configurando Departamento de Servicios Escolares...")

    cursor.execute("INSERT OR IGNORE INTO PuestosAdministrativos (id_puesto, nombre_puesto, id_departamento) VALUES (15, 'Jefa del Departamento de Servicios Escolares', 6)")
    
    # Funcionario (Jefa Escolares)
    cursor.execute("""
        INSERT OR IGNORE INTO Docentes (id_docente, nombre, apellidos, id_departamento, id_plaza, id_institucion, estatus) 
        VALUES (995, 'ANA MARÍA', 'MARTÍNEZ LÓPEZ', 6, 1, 2, 'ACTIVO')
    """)
    
    # Asignación del Puesto
    cursor.execute("INSERT OR IGNORE INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio) VALUES (60, 15, 995, '2023-01-15')")
    
    # Usuario para Firma
    cursor.execute("INSERT OR REPLACE INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello) VALUES (995, '123', 'jefe', 'static/firmas/firma_yareli.png', 'static/firmas/sello.png')")

    # =========================================================================
    # 2. INSERTAR ASIGNATURAS
    # =========================================================================
    print("2. Registrando asignaturas...")
    asignaturas = [
        ('SCD-1015', 'Programación Web', 1, 'ISIC-2010-224'),
        ('SCD-1021', 'Redes de Computadoras', 1, 'ISIC-2010-224'),
        ('SCD-1027', 'Taller de Sistemas Operativos', 1, 'ISIC-2010-224'),
        ('AED-1026', 'Estructura de Datos', 1, 'ISIC-2010-224'),
        ('MPA-2001', 'Minería de Datos Avanzada', 3, 'MCCI-2012-01'),
        ('MPA-2002', 'Inteligencia de Negocios', 3, 'MCCI-2012-01')
    ]
    for a in asignaturas:
        cursor.execute("INSERT OR IGNORE INTO Asignaturas (clave_asignatura, nombre_asignatura, id_carrera, plan_estudio) VALUES (?, ?, ?, ?)", a)

    # =========================================================================
    # 3. INSERTAR GRUPOS Y HORARIOS
    # =========================================================================
    print("3. Asignando grupos y horarios...")
    # Grupos para José (ID 101) - AHORA SEGURO PORQUE JOSÉ EXISTE
    grupos = [
        (101, 'A', 'SCD-1015', 101, 1, 'Escolarizada'),
        (102, 'B', 'AED-1026', 101, 1, 'Escolarizada'),
        (103, 'U', 'MPA-2001', 101, 1, 'Posgrado'),
        (201, 'A', 'SCD-1021', 101, 2, 'Escolarizada'),
        (202, 'B', 'SCD-1027', 101, 2, 'Escolarizada'),
        (203, 'X', 'MPA-2002', 101, 2, 'Posgrado')
    ]
    for g in grupos:
        cursor.execute("INSERT OR IGNORE INTO Grupos (id_grupo, clave_grupo, clave_asignatura, id_docente, id_periodo, modalidad) VALUES (?, ?, ?, ?, ?, ?)", g)

    horarios = [
        (101, 'Lunes', '09:00', '11:00', 1), (101, 'Miércoles', '09:00', '11:00', 1),
        (102, 'Martes', '11:00', '13:00', 2), (103, 'Viernes', '16:00', '19:00', 3),
        (201, 'Lunes', '07:00', '09:00', 1), (202, 'Jueves', '09:00', '11:00', 2),
        (203, 'Sábado', '08:00', '13:00', 3)
    ]
    for idx, h in enumerate(horarios):
        cursor.execute("INSERT OR IGNORE INTO HorariosClase (id_horario, id_grupo, dia_semana, hora_inicio, hora_fin, id_aula) VALUES (?, ?, ?, ?, ?, ?)", (5000+idx, h[0], h[1], h[2], h[3], h[4]))

    # =========================================================================
    # 4. VERIFICAR QUE LOS GRUPOS EXISTEN ANTES DE INSERTAR ALUMNOS
    # =========================================================================
    print("4. Verificando que los grupos existen...")
    cursor.execute("SELECT id_grupo FROM Grupos WHERE id_grupo IN (101, 201)")
    grupos_existentes = [row[0] for row in cursor.fetchall()]
    print(f"Grupos existentes: {grupos_existentes}")

    if not grupos_existentes:
        print("ERROR: No se encontraron los grupos necesarios. Revisa la inserción de grupos.")
        conn.rollback()
        exit()

    # =========================================================================
    # 5. SIMULAR ALUMNOS E INSCRIPCIONES (CON VERIFICACIÓN)
    # =========================================================================
    print("5. Inscribiendo alumnos...")
    
    # Primero verificar si ya existen alumnos para evitar duplicados
    cursor.execute("SELECT COUNT(*) FROM Alumnos WHERE id_alumno BETWEEN 21170000 AND 21170040")
    alumnos_existentes = cursor.fetchone()[0]
    
    if alumnos_existentes == 0:
        # Alumnos - usar INSERT OR IGNORE para evitar errores
        for i in range(40):
            cursor.execute("""
                INSERT OR IGNORE INTO Alumnos (id_alumno, numero_control, nombre, apellidos, id_institucion) 
                VALUES (?, ?, ?, ?, ?)
            """, (21170000+i, f'211700{i:02d}', f'Alumno{i}', 'Generico', 2))
        print(f"   Creados {40} alumnos nuevos")
    else:
        print(f"   Ya existen {alumnos_existentes} alumnos, continuando...")

    # Inscripciones - SOLO para grupos que existen
    inscripcion_id = 1000
    for grupo_id in grupos_existentes:
        if grupo_id == 101:
            # Grupo 101 - 30 alumnos
            for i in range(30):
                cursor.execute("""
                    INSERT OR IGNORE INTO Inscripciones (id_inscripcion, id_alumno, id_grupo) 
                    VALUES (?, ?, ?)
                """, (inscripcion_id, 21170000+i, grupo_id))
                inscripcion_id += 1
            print(f"   Inscritos 30 alumnos en grupo 101")
        
        elif grupo_id == 201:
            # Grupo 201 - 25 alumnos  
            for i in range(25):
                cursor.execute("""
                    INSERT OR IGNORE INTO Inscripciones (id_inscripcion, id_alumno, id_grupo) 
                    VALUES (?, ?, ?)
                """, (inscripcion_id, 21170000+i, grupo_id))
                inscripcion_id += 1
            print(f"   Inscritos 25 alumnos en grupo 201")

    # =========================================================================
    # 6. INSERTAR TUTORÍAS
    # =========================================================================
    print("6. Registrando tutorías...")
    cursor.execute("INSERT OR IGNORE INTO Tutorias (id_tutoria, id_docente_tutor, id_periodo) VALUES (701, 101, 1)")
    cursor.execute("INSERT OR IGNORE INTO HorariosTutoria (id_horario_tutoria, id_tutoria, dia_semana, hora_inicio, hora_fin, id_aula) VALUES (7001, 701, 'Viernes', '12:00', '14:00', 2)")
    
    cursor.execute("INSERT OR IGNORE INTO Tutorias (id_tutoria, id_docente_tutor, id_periodo) VALUES (702, 101, 2)")
    cursor.execute("INSERT OR IGNORE INTO HorariosTutoria (id_horario_tutoria, id_tutoria, dia_semana, hora_inicio, hora_fin, id_aula) VALUES (7002, 702, 'Viernes', '12:00', '14:00', 2)")

    conn.commit()
    print("\n¡Éxito! Base de datos reparada y datos de Promoción del Aprendizaje insertados correctamente.")

except sqlite3.Error as e:
    print(f"Error fatal en la base de datos: {e}")
    conn.rollback()
finally:
    conn.close()