import sqlite3
import os

db_filename = 'EDDI.db'
if os.path.exists(db_filename):
    os.remove(db_filename)

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Recreando BD con esquema extendido y compatibilidad app web...")

sql_script = """
-- =============================================
-- 1. TABLAS CATALOGO PRINCIPALES
-- =============================================

CREATE TABLE Departamentos (
    id_departamento INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE Instituciones (
    id_institucion INTEGER PRIMARY KEY,
    nombre_institucion TEXT NOT NULL UNIQUE
);

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
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    tipo_periodo TEXT NOT NULL
);

-- ADAPTADO: Se agrega clave_presupuestal para compatibilidad con PDF
CREATE TABLE Plazas (
    id_plaza INTEGER PRIMARY KEY,
    nombre_plaza TEXT NOT NULL UNIQUE,
    clave_presupuestal TEXT -- Requerido por la app
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

-- =============================================
-- 2. TABLAS OPERATIVAS
-- =============================================

CREATE TABLE Asignaturas (
    clave_asignatura TEXT PRIMARY KEY,
    nombre_asignatura TEXT NOT NULL,
    id_carrera INTEGER NOT NULL,
    plan_estudio TEXT NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);

-- ADAPTADO: Se agregan campos RFC, CURP, SUELDOS, ESTATUS para compatibilidad con PDF
CREATE TABLE Docentes (
    id_docente INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_ingreso DATE,
    id_departamento INTEGER NOT NULL,
    registro_cvu TEXT UNIQUE,
    id_plaza INTEGER NOT NULL,
    id_institucion INTEGER NOT NULL,
    
    -- Campos Legacy requeridos por la App Web
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

CREATE TABLE PuestosAdministrativos (
    id_puesto INTEGER PRIMARY KEY,
    nombre_puesto TEXT NOT NULL UNIQUE,
    id_departamento INTEGER NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento)
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
    fecha_registro DATE NOT NULL,
    fecha_inicio_vigencia DATE NOT NULL,
    fecha_fin_vigencia DATE NOT NULL,
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
    fecha_registro DATE NOT NULL,
    FOREIGN KEY (id_depto_origen) REFERENCES Departamentos(id_departamento),
    FOREIGN KEY (id_depto_registro) REFERENCES Departamentos(id_departamento)
);

CREATE TABLE ConveniosColaboracion (
    id_convenio INTEGER PRIMARY KEY,
    id_institucion_externa INTEGER NOT NULL,
    nombre_convenio TEXT NOT NULL,
    fecha_firma DATE NOT NULL,
    fecha_inicio_vigencia DATE NOT NULL,
    fecha_fin_vigencia DATE NOT NULL,
    FOREIGN KEY (id_institucion_externa) REFERENCES Instituciones(id_institucion)
);

-- Tablas de Relación N:M

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
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
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
    fecha_emision DATE NOT NULL,
    anio_actualizacion INTEGER NOT NULL,
    FOREIGN KEY (id_docente_certificado) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_puesto_emisor) REFERENCES PuestosAdministrativos(id_puesto)
);

-- ADAPTADO: Usamos definición similar
CREATE TABLE AsignacionPuestos (
    id_asignacion INTEGER PRIMARY KEY,
    id_puesto INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    FOREIGN KEY (id_puesto) REFERENCES PuestosAdministrativos(id_puesto),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente)
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
    fecha_emision DATE NOT NULL,
    anio_evaluado INTEGER NOT NULL,
    FOREIGN KEY (id_docente_certificado) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_docente_emisor) REFERENCES Docentes(id_docente)
);

CREATE TABLE Licencias (
    id_licencia INTEGER PRIMARY KEY,
    id_docente INTEGER NOT NULL,
    id_tipo_licencia INTEGER NOT NULL,
    numero_oficio TEXT NOT NULL UNIQUE,
    fecha_oficio DATE NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
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
    fecha_evaluacion DATE NOT NULL,
    alumnos_participantes INTEGER NOT NULL, 
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_periodo) REFERENCES PeriodosEscolares(id_periodo),
    FOREIGN KEY (id_tipo_evaluacion) REFERENCES TiposEvaluacion(id_tipo_evaluacion)
);

CREATE TABLE LiberacionesAcademicas (
    id_liberacion INTEGER PRIMARY KEY,
    id_actividad_acad INTEGER NOT NULL UNIQUE,
    fecha_liberacion DATE NOT NULL,
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
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    id_aula INTEGER NOT NULL,
    FOREIGN KEY (id_tutoria) REFERENCES Tutorias(id_tutoria) 
);

CREATE TABLE Acreditaciones (
    id_acreditacion INTEGER PRIMARY KEY,
    id_carrera INTEGER NOT NULL,
    id_org_acreditador INTEGER NOT NULL,
    fecha_inicio_vigencia DATE NOT NULL,
    fecha_fin_vigencia DATE NOT NULL,
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
    obtuvo_credito INTEGER NOT NULL, -- BIT -> INTEGER (0/1)
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
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
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
    fecha_examen DATE NOT NULL,
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
    fecha_inicio_asesoria DATE NOT NULL,
    fecha_fin_asesoria DATE NOT NULL,
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

-- ADAPTADO: Agregados campos rol, rutas para login y firma
CREATE TABLE Usuarios (
    id_usuario INTEGER PRIMARY KEY, 
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL,
    ruta_firma TEXT,
    ruta_sello TEXT,
    CONSTRAINT FK_Usuario_Docente FOREIGN KEY (id_usuario) REFERENCES Docentes(id_docente) 
);

-- =============================================
-- TABLA EXTRA DE LA APP (NO EN TU SQL PERO NECESARIA)
-- =============================================
CREATE TABLE SolicitudesDocumentos (
    id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente_solicitante INTEGER NOT NULL,
    id_usuario_destinatario INTEGER NOT NULL,
    tipo_documento TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente', 
    fecha_solicitud DATE DEFAULT (date('now')),
    fecha_firma DATETIME,
    motivo_rechazo TEXT,
    FOREIGN KEY (id_docente_solicitante) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_usuario_destinatario) REFERENCES Usuarios(id_usuario)
);

-- =============================================
-- 3. INSERTS (CATÁLOGOS)
-- =============================================

INSERT INTO Instituciones (id_institucion, nombre_institucion) VALUES
(1, 'Tecnológico Nacional de México'),
(2, 'INSTITUTO TECNOLOGICO DE CULIACAN'); -- Mayúsculas para coincidir con PDF

INSERT INTO Organismos (id_organismo, nombre) VALUES
(1, 'SEP'), (2, 'CONAHCYT'), (3, 'TecNM'), (4, 'PRODEP');

INSERT INTO Departamentos (id_departamento, nombre) VALUES
(1, 'Departamento de Sistemas y Computación'),
(2, 'Departamento de Ciencias Básicas'),
(3, 'Departamento de Desarrollo Académico'),
(4, 'División de Estudios de Posgrado e Investigación'),
(5, 'Departamento de Recursos Humanos');

-- PLAZAS (Con claves presupuestales para PDF)
INSERT INTO Plazas (id_plaza, nombre_plaza, clave_presupuestal) VALUES
(1, 'PROFESOR DE CARRERA TITULAR "C"', 'E3817'),
(2, 'PROFESOR DE CARRERA ASOCIADO "B"', 'E3816'),
(3, 'TECNICO DOCENTE', 'E3818'),
(4, 'PROFESOR INVESTIGADOR', 'E3815');

INSERT INTO Escolaridades (id_escolaridad, nombre_titulo) VALUES (1, 'Licenciatura'), (2, 'Maestría'), (3, 'Doctorado');

INSERT INTO PeriodosEscolares (id_periodo, nombre_periodo, fecha_inicio, fecha_fin, tipo_periodo) VALUES
(1, 'Enero-Junio 2024', '2024-01-26', '2024-06-30', 'Semestral'),
(2, 'Agosto-Diciembre 2024', '2024-08-21', '2024-12-15', 'Semestral'),
(3, 'Enero-Junio 2025', '2025-01-27', '2025-06-27', 'Semestral');

INSERT INTO Carreras (id_carrera, nombre_carrera, nivel) VALUES
(1, 'Ingeniería en Sistemas Computacionales', 'Licenciatura'),
(2, 'Ingeniería Mecatrónica', 'Licenciatura'),
(3, 'Maestría en Ciencias de la Computación', 'Posgrado');

INSERT INTO TiposEvaluacion (id_tipo_evaluacion, nombre_evaluacion, aplica_a_nivel) VALUES
(1, 'Evaluación Departamental', 'Licenciatura'), (2, 'Evaluación al Desempeño Docente', 'Licenciatura'), (3, 'Autoevaluación', 'Ambos');

INSERT INTO EventosAcademicos (id_evento_acad, nombre, siglas, organizador, ambito) VALUES
(1, 'Evento Nacional Estudiantil de Ciencias Básicas', 'ENECB', 'TecNM', 'Nacional'),
(2, 'Cumbre Nacional de Desarrollo Tecnológico', 'InnovaTecNM', 'TecNM', 'Nacional'),
(3, 'Concurso Internacional de Robótica', 'RoboGames', 'Independiente', 'Internacional');

INSERT INTO OpcionesTitulacion (id_opcion_titulacion, nombre_opcion) VALUES (1, 'Tesis Profesional'), (2, 'Residencia Profesional'), (3, 'Proyecto de Investigación');
INSERT INTO TiposEstrategiaDidactica (id_tipo_estrategia, nombre_estrategia, producto_obtenido) VALUES (1, 'ABP', 'Prototipo'), (2, 'Aula Invertida', 'Reporte'), (3, 'Estudio de Casos', 'Diagnóstico');
INSERT INTO OrganismosAcreditadores (id_org_acreditador, nombre, siglas) VALUES (1, 'CACEI', 'CACEI'), (2, 'CONAIC', 'CONAIC');
INSERT INTO OrganismosAcademicos (id_organismo_acad, nombre, tipo) VALUES (1, 'Academia de Sistemas', 'Academia'), (2, 'Consejo de Posgrado', 'Consejo');
INSERT INTO Aulas (id_aula, nombre_aula) VALUES (1, 'Laboratorio C1'), (2, 'Aula 22'), (3, 'Sala Audiovisual');
INSERT INTO TiposLicencia (id_tipo_licencia, nombre_licencia, descripcion) VALUES (1, 'Sabático', 'Investigación'), (2, 'Beca Comisión', 'Estudios'), (3, 'Gravidez', 'Maternidad');

INSERT INTO PuestosAdministrativos (id_puesto, nombre_puesto, id_departamento) VALUES
(1, 'Jefe de Departamento Académico', 1),
(2, 'Jefa del Departamento de Desarrollo Académico', 3), -- Yareli
(3, 'Coordinador de Carrera', 1),
(4, 'Subdirector Académico', 1),
(10, 'Jefa del Departamento de Administracion de Recursos Humanos', 5); -- María (Para firmas)

-- =============================================
-- 4. INSERTS (PERSONAS Y USUARIOS)
-- =============================================

-- 1. DOCENTE (José Enrique) - Datos completos para PDF
INSERT INTO Docentes (
    id_docente, nombre, apellidos, fecha_ingreso, id_departamento, registro_cvu, id_plaza, id_institucion,
    rfc, curp, sueldo_bruto, sueldo_letra, horario, estatus
) VALUES (
    101, 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', '2020-08-15', 1, 'CVU-TEC-2024-001', 1, 2,
    'EILJ900815XX1', 'EILJ900815HSRNNS01', 25000.00, 'VEINTICINCO MIL PESOS 00/100 M.N.', 'LUNES A VIERNES DE 7:00 A 15:00 HORAS', 'BASE'
);

-- 2. DOCENTE EXTRA
INSERT INTO Docentes (id_docente, nombre, apellidos, fecha_ingreso, id_departamento, registro_cvu, id_plaza, id_institucion, rfc, estatus)
VALUES (102, 'MARÍA', 'GONZÁLEZ PÉREZ', '2015-02-01', 2, 'CVU-TEC-2024-002', 2, 2, 'MGP150201XX1', 'BASE');

-- 3. DOCENTE INVESTIGADOR
INSERT INTO Docentes (id_docente, nombre, apellidos, fecha_ingreso, id_departamento, registro_cvu, id_plaza, id_institucion, rfc, estatus)
VALUES (103, 'ROBERTO', 'SÁNCHEZ RUIZ', '2010-09-01', 1, 'CVU-TEC-2024-003', 4, 2, 'RSR100901XX1', 'BASE');

-- 4. JEFA DE RH (Para firmas) - María Elena
INSERT INTO Docentes (id_docente, nombre, apellidos, fecha_ingreso, id_departamento, id_plaza, id_institucion, rfc, estatus)
VALUES (999, 'MARÍA ELENA', 'SÁNCHEZ RUIZ', '2010-01-01', 5, 4, 2, 'SARM800101XXA', 'BASE');

-- 5. JEFA DE DESARROLLO (Para futuras firmas) - Yareli
INSERT INTO Docentes (id_docente, nombre, apellidos, fecha_ingreso, id_departamento, id_plaza, id_institucion, rfc, estatus)
VALUES (998, 'YARELI', 'LÓPEZ GARCÍA', '2015-01-01', 3, 4, 2, 'LOGY850101XXB', 'BASE');


-- =============================================
-- 5. USUARIOS (LOGIN Y FIRMAS)
-- =============================================

-- José (Docente normal)
INSERT INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello) 
VALUES (101, '123', 'docente', NULL, NULL);

-- María Elena (Jefa RH) - CON FIRMA Y SELLO PNG (Arreglado)
INSERT INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello) 
VALUES (999, '123', 'jefe', 'static/firmas/firma.png', 'static/firmas/sello.png');

-- Yareli (Jefa Desarrollo)
INSERT INTO Usuarios (id_usuario, contrasena, rol, ruta_firma, ruta_sello) 
VALUES (998, '123', 'jefe', 'static/firmas/firma.png', 'static/firmas/sello.png');


-- =============================================
-- 6. ASIGNACIONES DE PUESTOS (VITAL PARA ENVIAR SOLICITUDES)
-- =============================================
INSERT INTO AsignacionPuestos (id_asignacion, id_puesto, id_docente, fecha_inicio, fecha_fin) VALUES
(1, 10, 999, '2023-01-01', NULL), -- María -> RH
(2, 2, 998, '2024-01-01', NULL);  -- Yareli -> Desarrollo Académico


-- =============================================
-- 7. DATOS ACADÉMICOS EXTRA (DE TU SQL)
-- =============================================

INSERT INTO Alumnos (id_alumno, numero_control, nombre, apellidos, id_institucion) VALUES
(5001, '21170001', 'Ana', 'López', 2), (5002, '21170002', 'Carlos', 'Méndez', 2), (5003, '21170003', 'Luis', 'Ramírez', 2);

INSERT INTO Asignaturas (clave_asignatura, nombre_asignatura, id_carrera, plan_estudio) VALUES
('SCD-1011', 'Ingeniería de Software', 1, 'ISIC-2010-224'),
('ACF-0901', 'Cálculo Diferencial', 1, 'ISIC-2010-224'),
('SCC-1012', 'Inteligencia Artificial', 1, 'ISIC-2010-224'),
('SCD-1008', 'Fundamentos de Bases de Datos', 1, 'ISIC-2010-224');

INSERT INTO ProyectosInvestigacion (id_proyecto, nombre_proyecto, fecha_registro, fecha_inicio_vigencia, fecha_fin_vigencia, id_organismo_registro, id_organismo_aprobador) VALUES
(1, 'Sistema Experto Diagnóstico', '2023-11-15', '2024-01-01', '2024-12-31', 3, 3),
(2, 'Algoritmos A* Logística', '2024-01-10', '2024-01-15', '2024-12-31', 2, 2);

INSERT INTO Docente_Escolaridad (id_docente, id_escolaridad) VALUES (101, 2), (103, 3);

INSERT INTO Grupos (id_grupo, clave_grupo, clave_asignatura, id_docente, id_periodo, modalidad) VALUES
(1, 'A', 'SCC-1012', 101, 1, 'Escolarizada'),
(2, 'B', 'SCD-1008', 101, 2, 'Escolarizada'),
(3, 'C', 'ACF-0901', 102, 1, 'Escolarizada');

INSERT INTO HorariosClase (id_horario, id_grupo, dia_semana, hora_inicio, hora_fin, id_aula) VALUES
(1, 1, 'Lunes', '07:00:00', '09:00:00', 1),
(2, 1, 'Miércoles', '07:00:00', '09:00:00', 1),
(3, 2, 'Martes', '10:00:00', '12:00:00', 2);

INSERT INTO EvaluacionesDocentes (id_evaluacion, id_docente, id_periodo, id_tipo_evaluacion, calificacion_global, fecha_evaluacion, alumnos_participantes) VALUES
(1, 101, 1, 2, '4.8', '2024-06-15', 30),
(2, 101, 2, 2, '4.9', '2024-12-10', 28);

INSERT INTO Docente_Proyecto (id_docente, id_proyecto, rol) VALUES (101, 1, 'Responsable Técnico'), (103, 2, 'Colaborador');
INSERT INTO Tutorias (id_tutoria, id_docente_tutor, id_periodo) VALUES (1, 101, 1), (2, 101, 2);

INSERT INTO ActasExamen (id_acta, id_alumno_titulado, id_opcion_titulacion, id_carrera, nombre_trabajo, fecha_examen) VALUES
(1, 5001, 1, 1, 'Reconocimiento Facial', '2024-11-20');
INSERT INTO JuradoExamen (id_jurado, id_acta, id_docente, rol) VALUES (1, 1, 101, 'Presidente');

INSERT INTO RecursosEducativosDigitales (id_red, nombre, clave_asignatura, id_docente_creador) VALUES (1, 'Curso SQL', 'SCD-1008', 101);
INSERT INTO ActividadesAcademicas (id_actividad_acad, id_docente, id_organismo_acad, estado) VALUES (1, 101, 1, 'Activo');
INSERT INTO LiberacionesAcademicas (id_liberacion, id_actividad_acad, fecha_liberacion) VALUES (1, 1, '2025-01-15');
INSERT INTO AsesoriasEvento (id_asesoria_evento, id_docente_asesor, id_evento_acad, id_periodo, nivel_participacion, lugar_obtenido, nombre_proyecto) VALUES
(1, 101, 2, 2, 'Nacional', '2o Lugar', 'Gastronomía IA');

"""
cursor.executescript(sql_script)
conn.commit()
conn.close()
print("Base de datos EDDI.db recreada exitosamente con todos los datos.")