import sqlite3
import os

db_filename = 'EDDI.db'
if os.path.exists(db_filename): os.remove(db_filename)

conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Recreando BD con Jefa de Desarrollo Académico...")

sql_script = """
-- (TABLAS IGUALES QUE ANTES) --
CREATE TABLE Departamentos (id_departamento INT PRIMARY KEY, nombre VARCHAR(150) NOT NULL UNIQUE);
CREATE TABLE Instituciones (id_institucion INT PRIMARY KEY, nombre_institucion VARCHAR(255) NOT NULL UNIQUE);
CREATE TABLE Plazas (id_plaza INT PRIMARY KEY, nombre_plaza VARCHAR(150) NOT NULL UNIQUE, clave_presupuestal VARCHAR(50));

CREATE TABLE Docentes (
    id_docente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_ingreso DATE,
    id_departamento INT NOT NULL,
    registro_cvu VARCHAR(50) NULL UNIQUE,
    id_plaza INT NOT NULL,
    id_institucion INT NOT NULL,
    rfc VARCHAR(13) UNIQUE,
    curp VARCHAR(18) UNIQUE,
    sueldo_bruto DECIMAL(10,2),
    sueldo_letra VARCHAR(255),
    horario VARCHAR(255),
    estatus VARCHAR(50),
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento),
    FOREIGN KEY (id_plaza) REFERENCES Plazas(id_plaza),
    FOREIGN KEY (id_institucion) REFERENCES Instituciones(id_institucion)
);

CREATE TABLE PuestosAdministrativos (
    id_puesto INT PRIMARY KEY,
    nombre_puesto VARCHAR(255) NOT NULL UNIQUE,
    id_departamento INT NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento)
);

CREATE TABLE AsignacionPuestos (
    id_asignacion INT PRIMARY KEY,
    id_puesto INT NOT NULL,
    id_docente INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    FOREIGN KEY (id_puesto) REFERENCES PuestosAdministrativos(id_puesto),
    FOREIGN KEY (id_docente) REFERENCES Docentes(id_docente)
);

CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY, 
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    ruta_firma VARCHAR(255), 
    ruta_sello VARCHAR(255),
    CONSTRAINT FK_Usuario_Docente FOREIGN KEY (id_usuario) REFERENCES Docentes(id_docente) 
);

CREATE TABLE SolicitudesDocumentos (
    id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente_solicitante INT NOT NULL,
    id_usuario_destinatario INT NOT NULL,
    tipo_documento VARCHAR(50) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente', 
    fecha_solicitud DATE DEFAULT (date('now')),
    fecha_firma DATETIME,
    motivo_rechazo TEXT,
    FOREIGN KEY (id_docente_solicitante) REFERENCES Docentes(id_docente),
    FOREIGN KEY (id_usuario_destinatario) REFERENCES Usuarios(id_usuario)
);

-- INSERTS --
INSERT INTO Instituciones VALUES (1, 'TECNOLOGICO NACIONAL DE MEXICO'), (2, 'INSTITUTO TECNOLOGICO DE CULIACAN');

-- DEPARTAMENTOS (Agregamos Desarrollo Académico)
INSERT INTO Departamentos VALUES (1, 'Departamento de Sistemas y Computación');
INSERT INTO Departamentos VALUES (5, 'Departamento de Recursos Humanos');
INSERT INTO Departamentos VALUES (3, 'Departamento de Desarrollo Académico'); -- NUEVO

INSERT INTO Plazas VALUES (1, 'PROFESOR DE CARRERA TITULAR "C"', 'E3817'); 
INSERT INTO Plazas VALUES (4, 'PROFESOR INVESTIGADOR', 'E3815');

-- DOCENTES
-- 1. José (Docente)
INSERT INTO Docentes VALUES (101, 'JOSÉ ENRIQUE', 'ESPÍNDOLA LEYVA', '2020-08-15', 1, 'CVU-001', 1, 2, 'EILJ900815XX1', 'EILJ900815HSRNNS01', 25000.00, 'VEINTICINCO MIL PESOS 00/100 M.N.', 'LUNES A VIERNES DE 7:00 A 15:00 HORAS', 'BASE');

-- 2. María Elena (Jefa RH)
INSERT INTO Docentes VALUES (999, 'MARÍA ELENA', 'SÁNCHEZ RUIZ', '2010-01-01', 5, NULL, 4, 2, 'SARM800101XXA', NULL, 0, '', '', 'BASE');

-- 3. Yareli (Jefa Desarrollo Académico) - NUEVA
INSERT INTO Docentes VALUES (998, 'YARELI', 'LÓPEZ GARCÍA', '2015-01-01', 3, NULL, 4, 2, 'LOGY850101XXB', NULL, 0, '', '', 'BASE');


-- PUESTOS
INSERT INTO PuestosAdministrativos VALUES (10, 'Jefa del Departamento de Administracion de Recursos Humanos', 5);
INSERT INTO PuestosAdministrativos VALUES (11, 'Jefa del Departamento de Desarrollo Académico', 3); -- NUEVO

-- ASIGNACIONES
INSERT INTO AsignacionPuestos VALUES (1, 10, 999, '2023-01-01', NULL); -- María a RH
INSERT INTO AsignacionPuestos VALUES (2, 11, 998, '2024-01-01', NULL); -- Yareli a Desarrollo

-- USUARIOS
-- José (Docente)
INSERT INTO Usuarios VALUES (101, '123', 'docente', NULL, NULL);

-- María (Jefa RH)
INSERT INTO Usuarios VALUES (999, '123', 'jefe', 'static/firmas/firma.jpg', 'static/firmas/sello.jpg'); 

-- Yareli (Jefa Desarrollo) - NUEVA
-- Nota: Usa su propia firma, pero el MISMO sello institucional
INSERT INTO Usuarios VALUES (998, '123', 'jefe', 'static/firmas/firma_yareli.jpg', 'static/firmas/sello.jpg'); 

"""
cursor.executescript(sql_script)
conn.close()
print("BD Actualizada con Yareli (Desarrollo Académico).")