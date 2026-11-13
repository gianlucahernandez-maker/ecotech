"""Capa de persistencia: conexión y repositorios (todo el SQL vive aquí)."""
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio

__all__ = ["DepartamentoRepositorio", "EmpleadoRepositorio", "ProyectoRepositorio"]
