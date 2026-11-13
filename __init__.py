"""Capa de dominio: clases del negocio (POO pura, sin SQL)."""
from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.persona import Persona
from dominio.proyecto import Proyecto
from dominio.reportable import Reportable

__all__ = ["Departamento", "Empleado", "Persona", "Proyecto", "Reportable"]
