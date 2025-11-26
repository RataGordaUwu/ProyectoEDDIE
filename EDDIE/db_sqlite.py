import sqlite3
import os

db_filename = 'EDDI.db'
if os.path.exists(db_filename):
    os.remove(db_filename)

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Recreando BD con esquema extendido (Fusionado)...")

# ==========================================
# 1. TABLAS DEL SISTEMA ACTUAL (PRESERVADAS)
# ==========================================

# Departamentos (Fusionamos las definiciones)
cursor.execute("""
CREATE TABLE Departamentos (
    id_departamento INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
""")

# Instituciones
cursor.execute("""
CREATE TABLE Instituciones (
    id_institucion INTEGER PRIMARY KEY,
    nombre_institucion TEXT NOT NULL UNIQUE
);
""")

# Plazas
cursor.execute("""
CREATE TABLE Plazas (
    id_plaza INTEGER PRIMARY KEY,
    nombre_plaza TEXT NOT NULL UNIQUE,
    clave_presupuestal TEXT
);
""")

# Docentes (ESTRUCTURA ORIGINAL MANTENIDA para compatibilidad con app.py)
cursor.execute("""
CREATE TABLE Docentes (
    id_docente INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_ingreso TEXT,
    id_departamento INTEGER NOT NULL,
    registro_cvu TEXT NULL UNIQUE,
    id_plaza INTEGER NOT NULL,
    id_institucion INTEGER NOT NULL,
    rfc TEXT UNIQUE,
    curp TEXT UNIQUE,
    sueldo_bruto DECIMAL(10,2),
    sueldo_letra TEXT,
    horario TEXT,
    estatus TEXT,
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento),
    FOREIGN KEY (id_plaza) REFERENCES Plazas(id_plaza),
    FOREIGN KEY (id_institucion) REFERENCES Instituciones(id_institucion)
);
""")

# Puestos Administrativos
cursor.execute("""
CREATE TABLE PuestosAdministrativos (
    id_puesto INTEGER PRIMARY KEY,
    nombre_puesto TEXT NOT NULL UNIQUE,
    id_departamento INTEGER NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento)
);
""")

# AsignacionPuestos
cursor.execute("""
CREATE TABLE AsignacionPuestos (
    id_asignacion INTEGER PRIMARY KEY,
    id_puesto INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT,
    FOREIGN KEY (id_puesto) REFERENCES PuestosAdministrativos(id_puesto),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente)
);
""")

# Usuarios (ESTRUCTURA ORIGINAL MANTENIDA)
cursor.execute("""
CREATE TABLE Usuarios (
    id_usuario INTEGER PRIMARY KEY, 
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL,
    ruta_firma TEXT, 
    ruta_sello TEXT,
    CONSTRAINT FK_Usuario_Docente FOREIGN KEY (id_usuario) REFERENCES Docentes(id_docente) 
);
""")

# Solicitudes (ESTRUCTURA ORIGINAL)
cursor.execute("""
CREATE TABLE SolicitudesDocumentos (
    id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente_solicitante INTEGER NOT NULL,
    id_usuario_destinatario INTEGER NOT NULL,
    tipo_documento TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente', 
    fecha_solicitud TEXT DEFAULT (date('now')),
    fecha_firma TEXT,
    motivo_rechazo TEXT,
    FOREIGN KEY (id_docente_solicitante) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_usuario_destinatario) REFERENCES Usuarios(id_usuario)
);
""")

# ==========================================
# 2. NUEVAS TABLAS (DEL SCRIPT SQL ADAPTADO)
# ==========================================

cursor.executescript("""
CREATE TABLE Aulas (
    id_aula INTEGER PRIMARY KEY,
    nombre_aula TEXT NOT NULL UNIQUE
);

CREATE TABLE Escolaridades (
    id_escolaridad INTEGER PRIMARY KEY,
    nombre_titulo TEXT NOT NULL UNIQUE
);

CREATE TABLE Posgrados (
    id_posgrado INTEGER PRIMARY KEY,
    nombre_posgrado TEXT NOT NULL UNIQUE
);

CREATE TABLE Carreras (
    id_carrera INTEGER PRIMARY KEY,
    nombre_carrera TEXT NOT NULL UNIQUE,
    nivel TEXT NOT NULL
);

CREATE TABLE PeriodosEscolares (
    id_periodo INTEGER PRIMARY KEY,
    nombre_periodo TEXT NOT NULL UNIQUE,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    tipo_periodo TEXT NOT NULL
);

CREATE TABLE Organismos (
    id_organismo INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE TiposLicencia (
    id_tipo_licencia INTEGER PRIMARY KEY,
    nombre_licencia TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE OrganismosAcademicos (
    id_organismo_acad INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL
);

CREATE TABLE TiposEvaluacion (
    id_tipo_evaluacion INTEGER PRIMARY KEY,
    nombre_evaluacion TEXT NOT NULL UNIQUE,
    aplica_a_nivel TEXT NOT NULL
);

CREATE TABLE OrganismosAcreditadores (
    id_org_acreditador INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    siglas TEXT
);

CREATE TABLE TiposEstrategiaDidactica (
    id_tipo_estrategia INTEGER PRIMARY KEY,
    nombre_estrategia TEXT NOT NULL UNIQUE,
    producto_obtenido TEXT NOT NULL
);

CREATE TABLE OpcionesTitulacion (
    id_opcion_titulacion INTEGER PRIMARY KEY,
    nombre_opcion TEXT NOT NULL UNIQUE
);

CREATE TABLE EventosAcademicos (
    id_evento_acad INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    siglas TEXT,
    organizador TEXT NOT NULL,
    ambito TEXT NOT NULL
);

CREATE TABLE Asignaturas (
    clave_asignatura TEXT PRIMARY KEY,
    nombre_asignatura TEXT NOT NULL,
    id_carrera INTEGER NOT NULL,
    plan_estudio TEXT NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);

CREATE TABLE Alumnos (
    id_alumno INTEGER PRIMARY KEY,
    numero_control TEXT UNIQUE,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    id_institucion INTEGER NOT NULL,
    FOREIGN KEY (id_institucion) REFERENCES Instituciones(id_institucion)
);

CREATE TABLE ProyectosInvestigacion (
    id_proyecto INTEGER PRIMARY KEY,
    nombre_proyecto TEXT NOT NULL,
    fecha_registro TEXT NOT NULL,
    fecha_inicio_vigencia TEXT NOT NULL,
    fecha_fin_vigencia TEXT NOT NULL,
    id_organismo_registro INTEGER NOT NULL,
    id_organismo_aprobador INTEGER,
    FOREIGN KEY (id_organismo_registro) REFERENCES Organismos(id_organismo),
    FOREIGN KEY (id_organismo_aprobador) REFERENCES Organismos(id_organismo)
);

CREATE TABLE ProgramasAsesoria (
    id_programa_asesoria INTEGER PRIMARY KEY,
    nombre_programa TEXT NOT NULL,
    id_depto_origen INTEGER NOT NULL,
    id_depto_registro INTEGER NOT NULL,
    fecha_registro TEXT NOT NULL,
    FOREIGN KEY (id_depto_origen) REFERENCES Departamentos(id_departamento),
    FOREIGN KEY (id_depto_registro) REFERENCES Departamentos(id_departamento)
);

CREATE TABLE ConveniosColaboracion (
    id_convenio INTEGER PRIMARY KEY,
    id_institucion_externa INTEGER NOT NULL,
    nombre_convenio TEXT NOT NULL,
    fecha_firma TEXT NOT NULL,
    fecha_inicio_vigencia TEXT NOT NULL,
    fecha_fin_vigencia TEXT NOT NULL,
    FOREIGN KEY (id_institucion_externa) REFERENCES Instituciones(id_institucion)
);

CREATE TABLE Docente_Escolaridad (
    id_docente INTEGER,
    id_escolaridad INTEGER,
    PRIMARY KEY (id_docente, id_escolaridad),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_escolaridad) REFERENCES Escolaridades(id_escolaridad)
);

CREATE TABLE Docente_Posgrado (
    id_docente INTEGER,
    id_posgrado INTEGER,
    PRIMARY KEY (id_docente, id_posgrado),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_posgrado) REFERENCES Posgrados(id_posgrado)
);

CREATE TABLE Grupos (
    id_grupo INTEGER PRIMARY KEY,
    clave_grupo TEXT NOT NULL,
    clave_asignatura TEXT NOT NULL,
    id_docente INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    modalidad TEXT NOT NULL,
    FOREIGN KEY (clave_asignatura) REFERENCES Asignaturas(clave_asignatura),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE HorariosClase (
    id_horario INTEGER PRIMARY KEY,
    id_grupo INTEGER NOT NULL,
    dia_semana TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL,
    id_aula INTEGER NOT NULL,
    FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo),
    FOREIGN KEY (id_aula) REFERENCES Aulas(id_aula)
);

CREATE TABLE Docente_Proyecto (
    id_docente INTEGER NOT NULL,
    id_proyecto INTEGER NOT NULL,
    rol TEXT NOT NULL,
    PRIMARY KEY (id_docente, id_proyecto),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_proyecto) REFERENCES ProyectosInvestigacion(id_proyecto)
);

CREATE TABLE ConstanciasCVU (
    id_constancia INTEGER PRIMARY KEY,
    id_docente_certificado INTEGER NOT NULL,
    id_puesto_emisor INTEGER NOT NULL,
    fecha_emision TEXT NOT NULL,
    anio_actualizacion INTEGER NOT NULL,
    FOREIGN KEY (id_docente_certificado) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_puesto_emisor) REFERENCES PuestosAdministrativos(id_puesto)
);

CREATE TABLE Inscripciones (
    id_inscripcion INTEGER PRIMARY KEY,
    id_alumno INTEGER NOT NULL,
    id_grupo INTEGER NOT NULL,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno),
    FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo)
);

CREATE TABLE ConstanciasAsignatura (
    id_constancia_asig INTEGER PRIMARY KEY,
    id_docente_certificado INTEGER NOT NULL,
    id_docente_emisor INTEGER NOT NULL,
    fecha_emision TEXT NOT NULL,
    anio_evaluado INTEGER NOT NULL,
    FOREIGN KEY (id_docente_certificado) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_docente_emisor) REFERENCES Docentes(id_docente)
);

CREATE TABLE Licencias (
    id_licencia INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_tipo_licencia INTEGER NOT NULL,
    numero_oficio TEXT NOT NULL UNIQUE,
    fecha_oficio TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_tipo_licencia) REFERENCES TiposLicencia(id_tipo_licencia)
);

CREATE TABLE EvidenciasProfesionales (
    id_evidencia INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    tipo_documento TEXT NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente)
);

CREATE TABLE ActividadesAcademicas (
    id_actividad_acad INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_organismo_acad INTEGER NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_organismo_acad) REFERENCES OrganismosAcademicos(id_organismo_acad)
);

CREATE TABLE EvaluacionesDocentes (
    id_evaluacion INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    id_tipo_evaluacion INTEGER NOT NULL,
    calificacion_global TEXT NOT NULL,
    fecha_evaluacion TEXT NOT NULL,
    alumnos_participantes INTEGER NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo),
    FOREIGN KEY (id_tipo_evaluacion) REFERENCES TiposEvaluacion(id_tipo_evaluacion)
);

CREATE TABLE LiberacionesAcademicas (
    id_liberacion INTEGER PRIMARY KEY,
    id_actividad_acad INTEGER NOT NULL UNIQUE,
    fecha_liberacion TEXT NOT NULL,
    FOREIGN KEY (id_actividad_acad) REFERENCES ActividadesAcademicas(id_actividad_acad)
);

CREATE TABLE Tutorias (
    id_tutoria INTEGER PRIMARY KEY,
    id_docente_tutor INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    FOREIGN KEY (id_docente_tutor) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE HorariosTutoria (
    id_horario_tutoria INTEGER PRIMARY KEY,
    id_tutoria INTEGER NOT NULL,
    dia_semana TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL,
    id_aula INTEGER NOT NULL,
    FOREIGN KEY (id_tutoria) REFERENCES Tutorias(id_tutoria)
);

CREATE TABLE Acreditaciones (
    id_acreditacion INTEGER PRIMARY KEY,
    id_carrera INTEGER NOT NULL,
    id_org_acreditador INTEGER NOT NULL,
    fecha_inicio_vigencia TEXT NOT NULL,
    fecha_fin_vigencia TEXT NOT NULL,
    numero_registro TEXT,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera),
    FOREIGN KEY (id_org_acreditador) REFERENCES OrganismosAcreditadores(id_org_acreditador)
);

CREATE TABLE ActividadesComplementarias (
    id_actividad_comp INTEGER PRIMARY KEY,
    numero_dictamen TEXT NOT NULL UNIQUE,
    nombre_actividad TEXT NOT NULL,
    creditos INTEGER NOT NULL,
    id_docente_responsable INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    FOREIGN KEY (id_docente_responsable) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE AlumnosActividadComp (
    id_inscripcion_ac INTEGER PRIMARY KEY,
    id_actividad_comp INTEGER NOT NULL,
    id_alumno INTEGER NOT NULL,
    obtuvo_credito INTEGER NOT NULL,
    FOREIGN KEY (id_actividad_comp) REFERENCES ActividadesComplementarias(id_actividad_comp),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno)
);

CREATE TABLE ProyectosIntegradores (
    id_proyecto_int INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    id_docente_creador INTEGER NOT NULL,
    FOREIGN KEY (id_docente_creador) REFERENCES Docentes(id_docente)
);

CREATE TABLE Proyecto_Asignatura (
    id_proyecto_int INTEGER NOT NULL,
    clave_asignatura TEXT NOT NULL,
    PRIMARY KEY (id_proyecto_int, clave_asignatura),
    FOREIGN KEY (id_proyecto_int) REFERENCES ProyectosIntegradores(id_proyecto_int),
    FOREIGN KEY (clave_asignatura) REFERENCES Asignaturas(clave_asignatura)
);

CREATE TABLE RecursosEducativosDigitales (
    id_red INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    clave_asignatura TEXT NOT NULL,
    id_docente_creador INTEGER NOT NULL,
    FOREIGN KEY (clave_asignatura) REFERENCES Asignaturas(clave_asignatura),
    FOREIGN KEY (id_docente_creador) REFERENCES Docentes(id_docente)
);

CREATE TABLE ManualesPracticas (
    id_manual INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    id_docente_creador INTEGER NOT NULL,
    clave_asignatura TEXT NOT NULL,
    FOREIGN KEY (id_docente_creador) REFERENCES Docentes(id_docente),
    FOREIGN KEY (clave_asignatura) REFERENCES Asignaturas(clave_asignatura)
);

CREATE TABLE ImplementacionesEstrategia (
    id_implementacion INTEGER PRIMARY KEY,
    id_grupo INTEGER NOT NULL,
    id_tipo_estrategia INTEGER NOT NULL,
    impacto_aprendizaje TEXT NOT NULL,
    FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo),
    FOREIGN KEY (id_tipo_estrategia) REFERENCES TiposEstrategiaDidactica(id_tipo_estrategia)
);

CREATE TABLE MaterialesDidacticosEnfoque (
    id_material_enfoque INTEGER PRIMARY KEY,
    nombre_material TEXT NOT NULL,
    id_docente_creador INTEGER NOT NULL,
    enfoque TEXT NOT NULL,
    productos_obtenidos TEXT NOT NULL,
    impacto_aprendizaje TEXT NOT NULL,
    id_periodo_creacion INTEGER NOT NULL,
    FOREIGN KEY (id_docente_creador) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo_creacion) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE CursosImpartidos (
    id_curso_impartido INTEGER PRIMARY KEY,
    id_docente_instructor INTEGER NOT NULL,
    nombre_curso TEXT NOT NULL,
    id_institucion_sede INTEGER NOT NULL,
    duracion_horas INTEGER NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    numero_oficio_comision TEXT NOT NULL,
    numero_registro_constancia TEXT NOT NULL,
    FOREIGN KEY (id_docente_instructor) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_institucion_sede) REFERENCES Instituciones(id_institucion)
);

CREATE TABLE ActasExamen (
    id_acta INTEGER PRIMARY KEY,
    id_alumno_titulado INTEGER NOT NULL,
    id_opcion_titulacion INTEGER NOT NULL,
    id_carrera INTEGER NOT NULL,
    nombre_trabajo TEXT NOT NULL,
    fecha_examen TEXT NOT NULL,
    FOREIGN KEY (id_alumno_titulado) REFERENCES Alumnos(id_alumno),
    FOREIGN KEY (id_opcion_titulacion) REFERENCES OpcionesTitulacion(id_opcion_titulacion),
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);

CREATE TABLE JuradoExamen (
    id_jurado INTEGER PRIMARY KEY,
    id_acta INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    rol TEXT NOT NULL,
    FOREIGN KEY (id_acta) REFERENCES ActasExamen(id_acta),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente)
);

CREATE TABLE AsesoriasExternas (
    id_asesoria_externa INTEGER PRIMARY KEY,
    id_docente_asesor INTEGER NOT NULL,
    nombre_alumno_externo TEXT NOT NULL,
    id_convenio INTEGER NOT NULL,
    numero_oficio_comision TEXT NOT NULL,
    nivel_academico TEXT NOT NULL,
    rol_docente TEXT NOT NULL,
    titulo_tesis TEXT NOT NULL,
    fecha_inicio_asesoria TEXT NOT NULL,
    fecha_fin_asesoria TEXT NOT NULL,
    FOREIGN KEY (id_docente_asesor) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_convenio) REFERENCES ConveniosColaboracion(id_convenio)
);

CREATE TABLE ParticipacionAsesoria (
    id_participacion INTEGER PRIMARY KEY,
    id_programa_asesoria INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    FOREIGN KEY (id_programa_asesoria) REFERENCES ProgramasAsesoria(id_programa_asesoria),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE AsesoriasEvento (
    id_asesoria_evento INTEGER PRIMARY KEY,
    id_docente_asesor INTEGER NOT NULL,
    id_evento_acad INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    nivel_participacion TEXT NOT NULL,
    lugar_obtenido TEXT NOT NULL,
    nombre_proyecto TEXT NOT NULL,
    FOREIGN KEY (id_docente_asesor) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_evento_acad) REFERENCES EventosAcademicos(id_evento_acad),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE AlumnosAsesoriaEvento (
    id_asesoria_evento INTEGER NOT NULL,
    id_alumno INTEGER NOT NULL,
    PRIMARY KEY (id_asesoria_evento, id_alumno),
    FOREIGN KEY (id_asesoria_evento) REFERENCES AsesoriasEvento(id_asesoria_evento),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno)
);

CREATE TABLE CoordinacionEventos (
    id_coordinacion INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_evento_acad INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    rol TEXT NOT NULL,
    numero_oficio_comision TEXT NOT NULL,
    actividades_desarrolladas TEXT,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_evento_acad) REFERENCES EventosAcademicos(id_evento_acad),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);

CREATE TABLE ParticipacionJuradoEvento (
    id_participacion_jurado INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_evento_acad INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,
    nivel_participacion TEXT NOT NULL,
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_evento_acad) REFERENCES EventosAcademicos(id_evento_acad),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo)
);
""")

# ==========================================
# 3. INSERCIÓN DE DATOS (FUSIONADOS)
# ==========================================

print("Insertando datos...")

script_inserts = """
-- INSTITUCIONES (Originales + Nuevas)
INSERT INTO Instituciones VALUES (1, 'TECNOLOGICO NACIONAL DE MEXICO');
INSERT INTO Instituciones VALUES (2, 'INSTITUTO TECNOLOGICO DE CULIACAN');

-- DEPARTAMENTOS (Todos los del script nuevo + originales)
INSERT INTO Departamentos VALUES (1, 'Departamento de Sistemas y Computación');
INSERT INTO Departamentos VALUES (2, 'Departamento de Ciencias Básicas');
INSERT INTO Departamentos VALUES (3, 'Departamento de Desarrollo Académico');
INSERT INTO Departamentos VALUES (4, 'División de Estudios de Posgrado e Investigación');
INSERT INTO Departamentos VALUES (5, 'Departamento de Recursos Humanos');

-- PLAZAS (Nuevo catálogo más completo)
INSERT INTO Plazas VALUES (1, 'Profesor de Carrera Titular "C" Tiempo Completo', 'E3817');
INSERT INTO Plazas VALUES (2, 'Profesor de Carrera Asociado "B" Tiempo Completo', 'E381X');
INSERT INTO Plazas VALUES (3, 'Técnico Docente Tiempo Completo', 'E3XXX');
INSERT INTO Plazas VALUES (4, 'PROFESOR INVESTIGADOR', 'E3815');

-- ORGANISMOS
INSERT INTO Organismos VALUES (1, 'SEP');
INSERT INTO Organismos VALUES (2, 'CONAHCYT');
INSERT INTO Organismos VALUES (3, 'TecNM');
INSERT INTO Organismos VALUES (4, 'PRODEP');

-- ESCOLARIDADES
INSERT INTO Escolaridades VALUES (1, 'Licenciatura');
INSERT INTO Escolaridades VALUES (2, 'Maestría');
INSERT INTO Escolaridades VALUES (3, 'Doctorado');

-- PERIODOS ESCOLARES
INSERT INTO PeriodosEscolares VALUES (1, 'Enero-Junio 2024', '2024-01-26', '2024-06-30', 'Semestral');
INSERT INTO PeriodosEscolares VALUES (2, 'Agosto-Diciembre 2024', '2024-08-21', '2024-12-15', 'Semestral');
INSERT INTO PeriodosEscolares VALUES (3, 'Enero-Junio 2025', '2025-01-27', '2025-06-27', 'Semestral');

-- CARRERAS
INSERT INTO Carreras VALUES (1, 'Ingeniería en Sistemas Computacionales', 'Licenciatura');
INSERT INTO Carreras VALUES (2, 'Ingeniería Mecatrónica', 'Licenciatura');
INSERT INTO Carreras VALUES (3, 'Maestría en Ciencias de la Computación', 'Posgrado');

-- TIPOS EVALUACION
INSERT INTO TiposEvaluacion VALUES (1, 'Evaluación Departamental', 'Licenciatura');
INSERT INTO TiposEvaluacion VALUES (2, 'Evaluación al Desempeño Docente (Alumnos)', 'Licenciatura');
INSERT INTO TiposEvaluacion VALUES (3, 'Autoevaluación', 'Ambos');

-- EVENTOS ACADEMICOS
INSERT INTO EventosAcademicos VALUES (1, 'Evento Nacional Estudiantil de Ciencias Básicas', 'ENECB', 'TecNM', 'Nacional');
INSERT INTO EventosAcademicos VALUES (2, 'Cumbre Nacional de Desarrollo Tecnológico, Investigación e Innovación', 'InnovaTecNM', 'TecNM', 'Nacional');
INSERT INTO EventosAcademicos VALUES (3, 'Concurso Internacional de Robótica', 'RoboGames', 'Independiente', 'Internacional');

-- OPCIONES TITULACION
INSERT INTO OpcionesTitulacion VALUES (1, 'Tesis Profesional');
INSERT INTO OpcionesTitulacion VALUES (2, 'Residencia Profesional');
INSERT INTO OpcionesTitulacion VALUES (3, 'Proyecto de Investigación');

-- TIPOS ESTRATEGIA
INSERT INTO TiposEstrategiaDidactica VALUES (1, 'Aprendizaje Basado en Proyectos (ABP)', 'Prototipo Funcional');
INSERT INTO TiposEstrategiaDidactica VALUES (2, 'Aula Invertida', 'Reporte de Análisis');
INSERT INTO TiposEstrategiaDidactica VALUES (3, 'Estudio de Casos', 'Reporte de Diagnóstico');

-- ORGANISMOS ACREDITADORES
INSERT INTO OrganismosAcreditadores VALUES (1, 'Consejo de Acreditación de la Enseñanza de la Ingeniería', 'CACEI');
INSERT INTO OrganismosAcreditadores VALUES (2, 'Consejo Nacional de Acreditación en Informática y Computación', 'CONAIC');

-- ORGANISMOS ACADEMICOS
INSERT INTO OrganismosAcademicos VALUES (1, 'Academia de Sistemas y Computación', 'Academia Local');
INSERT INTO OrganismosAcademicos VALUES (2, 'Consejo de Posgrado', 'Consejo');

-- PUESTOS ADMINISTRATIVOS
INSERT INTO PuestosAdministrativos VALUES (1, 'Jefe de Departamento Académico', 1);
INSERT INTO PuestosAdministrativos VALUES (2, 'Jefe de Desarrollo Académico', 3);
INSERT INTO PuestosAdministrativos VALUES (3, 'Coordinador de Carrera', 1);
INSERT INTO PuestosAdministrativos VALUES (4, 'Subdirector Académico', 1);
INSERT INTO PuestosAdministrativos VALUES (10, 'Jefa del Departamento de Administracion de Recursos Humanos', 5);
INSERT INTO PuestosAdministrativos VALUES (11, 'Jefa del Departamento de Desarrollo Académico', 3);

-- AULAS
INSERT INTO Aulas VALUES (1, 'Laboratorio C1');
INSERT INTO Aulas VALUES (2, 'Aula 22');
INSERT INTO Aulas VALUES (3, 'Sala Audiovisual');

-- TIPOS LICENCIA
INSERT INTO TiposLicencia VALUES (1, 'Periodo Sabático', 'Año sabático para investigación o docencia');
INSERT INTO TiposLicencia VALUES (2, 'Beca Comisión', 'Licencia para estudios de posgrado');
INSERT INTO TiposLicencia VALUES (3, 'Gravidez', 'Licencia por maternidad');

-- =============================================
-- DOCENTES (FUSION DE DATOS ORIGINALES + NUEVOS)
-- =============================================

-- 1. José (Usuario 101) - Datos completos para App
INSERT INTO Docentes VALUES (101, 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', '2020-08-15', 1, 'CVU-TEC-2024-001', 1, 2, 'EILJ900815XX1', 'EILJ900815HSRNNS01', 25000.00, 'VEINTICINCO MIL PESOS 00/100 M.N.', 'LUNES A VIERNES DE 7:00 A 15:00 HORAS', 'BASE');

-- 2. María Elena (Jefa RH - Usuario 999) - Datos sistema
INSERT INTO Docentes VALUES (999, 'MARÍA ELENA', 'SÁNCHEZ RUIZ', '2010-01-01', 5, NULL, 4, 2, 'SARM800101XXA', NULL, 0, '', '', 'BASE');

-- 3. Yareli (Jefa Desarrollo - Usuario 998) - Datos sistema
INSERT INTO Docentes VALUES (998, 'YARELI', 'LÓPEZ GARCÍA', '2015-01-01', 3, NULL, 4, 2, 'LOGY850101XXB', NULL, 0, '', '', 'BASE');

-- 4. Docentes Nuevos del Script (Con datos mínimos necesarios)
INSERT INTO Docentes VALUES (102, 'María', 'González Pérez', '2015-02-01', 2, 'CVU-TEC-2024-002', 2, 2, NULL, NULL, 0, NULL, NULL, 'BASE');
INSERT INTO Docentes VALUES (103, 'Roberto', 'Sánchez Ruiz', '2010-09-01', 1, 'CVU-TEC-2024-003', 4, 2, NULL, NULL, 0, NULL, NULL, 'BASE');


-- =============================================
-- ASIGNACIONES DE PUESTOS
-- =============================================
INSERT INTO AsignacionPuestos VALUES (1, 10, 999, '2023-01-01', NULL); -- María a RH
INSERT INTO AsignacionPuestos VALUES (2, 11, 998, '2024-01-01', NULL); -- Yareli a Desarrollo

-- =============================================
-- USUARIOS (PARA LOGIN)
-- =============================================
INSERT INTO Usuarios VALUES (101, '123', 'docente', NULL, NULL);
INSERT INTO Usuarios VALUES (999, '123', 'jefe', 'static/firmas/firma.png', 'static/firmas/sello.png');
INSERT INTO Usuarios VALUES (998, '123', 'jefe', 'static/firmas/firma_yareli.png', 'static/firmas/sello.png');

-- =============================================
-- DATOS ACADÉMICOS Y CURRICULARES (DEL SCRIPT NUEVO)
-- =============================================

-- Alumnos
INSERT INTO Alumnos VALUES (5001, '21170001', 'Ana', 'López', 2);
INSERT INTO Alumnos VALUES (5002, '21170002', 'Carlos', 'Méndez', 2);
INSERT INTO Alumnos VALUES (5003, '21170003', 'Luis', 'Ramírez', 2);

-- Asignaturas
INSERT INTO Asignaturas VALUES ('SCD-1011', 'Ingeniería de Software', 1, 'ISIC-2010-224');
INSERT INTO Asignaturas VALUES ('ACF-0901', 'Cálculo Diferencial', 1, 'ISIC-2010-224');
INSERT INTO Asignaturas VALUES ('SCC-1012', 'Inteligencia Artificial', 1, 'ISIC-2010-224');
INSERT INTO Asignaturas VALUES ('SCD-1008', 'Fundamentos de Bases de Datos', 1, 'ISIC-2010-224');

-- Proyectos Investigación
INSERT INTO ProyectosInvestigacion VALUES (1, 'Sistema Experto para Diagnóstico de Enfermedades Respiratorias', '2023-11-15', '2024-01-01', '2024-12-31', 3, 3);
INSERT INTO ProyectosInvestigacion VALUES (2, 'Implementación de Algoritmos A* en Logística', '2024-01-10', '2024-01-15', '2024-12-31', 2, 2);

-- Docente Escolaridad
INSERT INTO Docente_Escolaridad VALUES (101, 2);
INSERT INTO Docente_Escolaridad VALUES (103, 3);

-- Grupos
INSERT INTO Grupos VALUES (1, 'A', 'SCC-1012', 101, 1, 'Escolarizada');
INSERT INTO Grupos VALUES (2, 'B', 'SCD-1008', 101, 2, 'Escolarizada');
INSERT INTO Grupos VALUES (3, 'C', 'ACF-0901', 102, 1, 'Escolarizada');

-- Horarios Clase
INSERT INTO HorariosClase VALUES (1, 1, 'Lunes', '07:00:00', '09:00:00', 1);
INSERT INTO HorariosClase VALUES (2, 1, 'Miércoles', '07:00:00', '09:00:00', 1);
INSERT INTO HorariosClase VALUES (3, 2, 'Martes', '10:00:00', '12:00:00', 2);

-- Evaluaciones Docentes
INSERT INTO EvaluacionesDocentes VALUES (1, 101, 1, 2, '4.8', '2024-06-15', 30);
INSERT INTO EvaluacionesDocentes VALUES (2, 101, 2, 2, '4.9', '2024-12-10', 28);
INSERT INTO EvaluacionesDocentes VALUES (3, 101, 1, 1, 'Excelente', '2024-06-20', 0);

-- Docente Proyecto
INSERT INTO Docente_Proyecto VALUES (101, 1, 'Responsable Técnico');
INSERT INTO Docente_Proyecto VALUES (103, 2, 'Colaborador');

-- Tutorias
INSERT INTO Tutorias VALUES (1, 101, 1);
INSERT INTO Tutorias VALUES (2, 101, 2);

-- Actas Examen (Tesis)
INSERT INTO ActasExamen VALUES (1, 5001, 1, 1, 'Reconocimiento Facial con Raspberry Pi y OpenCV', '2024-11-20');

-- Jurado Examen
INSERT INTO JuradoExamen VALUES (1, 1, 101, 'Presidente');

-- Recursos Educativos
INSERT INTO RecursosEducativosDigitales VALUES (1, 'Curso Interactivo de SQL Avanzado', 'SCD-1008', 101);

-- Actividades Academicas
INSERT INTO ActividadesAcademicas VALUES (1, 101, 1, 'Activo');

-- Liberaciones Academicas
INSERT INTO LiberacionesAcademicas VALUES (1, 1, '2025-01-15');

-- Asesorias Evento
INSERT INTO AsesoriasEvento VALUES (1, 101, 2, 2, 'Nacional', '2o Lugar', 'Sistema de Recomendación Gastronómica con IA');

"""
cursor.executescript(script_inserts)

conn.commit()
conn.close()
print("Base de datos EDDI.db regenerada con éxito (Esquema Original + Extendido).")