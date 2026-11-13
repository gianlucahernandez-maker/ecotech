# EcoTech Solutions — Sistema de Gestión de Empleados (ES2 · TI3021)

Aplicación de consola en Python que gestiona **empleados, departamentos y proyectos**
con Programación Orientada a Objetos y una base de datos **SQLite** (librería oficial `sqlite3`).

## Requisitos
- Python 3.10 o superior (usa la sintaxis `str | None`).

## Cómo ejecutar
```bash
python -m venv venv
venv\Scripts\activate            # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # Linux/Mac: cp .env.example .env
python main.py
```
La primera vez el programa crea las tablas y ofrece cargar datos de ejemplo.

Para crear solo las tablas:
```bash
python -c "from repositorio.conexion import inicializar_bd; inicializar_bd()"
```

## Pruebas automáticas
```bash
python -m unittest discover -s pruebas -t . -v
```
Incluyen: validaciones del dominio, CRUD de las 3 entidades, prueba de inyección SQL
(`' OR '1'='1`), rollback de la transacción y una auditoría que revisa que ninguna
consulta del repositorio se arme con f-strings, `+` o `%`.

## Estructura
```
ecotech_es2/
├── dominio/            Clases del negocio (POO pura, sin SQL)
│   ├── reportable.py   Interfaz abstracta Reportable (polimorfismo)
│   ├── persona.py      Clase abstracta Persona
│   ├── empleado.py     Empleado(Persona)
│   ├── departamento.py Departamento
│   ├── proyecto.py     Proyecto
│   ├── validaciones.py Validaciones reutilizables (RUT módulo 11, email, fechas)
│   └── excepciones.py  Excepciones propias del dominio
├── repositorio/        Capa de persistencia (todo el SQL vive aquí)
│   ├── conexion.py     Conexión sqlite3 + variables de entorno
│   ├── base.py         Transacciones (commit/rollback) y traducción de errores
│   ├── empleado_repo.py, departamento_repo.py, proyecto_repo.py
├── datos/schema.sql    DDL con llaves primarias y foráneas
├── pruebas/            Pruebas unittest
├── main.py             Menú por consola
├── requirements.txt, .env.example, .gitignore
```
