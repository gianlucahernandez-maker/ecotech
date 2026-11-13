-- Esquema relacional de EcoTech Solutions (SQLite 3)
-- Se ejecuta con inicializar_bd(); es seguro correrlo varias veces (IF NOT EXISTS).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departamento (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL UNIQUE,
    presupuesto  REAL    NOT NULL CHECK (presupuesto >= 0)
);

-- Persona (padre) y Empleado (hijo) reflejan la herencia del diagrama UML
CREATE TABLE IF NOT EXISTS persona (
    rut       TEXT PRIMARY KEY,
    nombre    TEXT NOT NULL,
    email     TEXT NOT NULL,
    telefono  TEXT
);

CREATE TABLE IF NOT EXISTS empleado (
    rut              TEXT    PRIMARY KEY,
    cargo            TEXT    NOT NULL,
    sueldo_base      REAL    NOT NULL CHECK (sueldo_base > 0),
    fecha_ingreso    TEXT    NOT NULL,
    departamento_id  INTEGER,
    activo           INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    FOREIGN KEY (rut)             REFERENCES persona(rut),
    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);

CREATE TABLE IF NOT EXISTS proyecto (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL UNIQUE,
    descripcion   TEXT,
    fecha_inicio  TEXT NOT NULL
);

-- Tabla intermedia de la relación muchos-a-muchos Empleado <-> Proyecto
CREATE TABLE IF NOT EXISTS asignacion (
    rut_empleado  TEXT    NOT NULL,
    proyecto_id   INTEGER NOT NULL,
    PRIMARY KEY (rut_empleado, proyecto_id),
    FOREIGN KEY (rut_empleado) REFERENCES empleado(rut),
    FOREIGN KEY (proyecto_id)  REFERENCES proyecto(id)
);
