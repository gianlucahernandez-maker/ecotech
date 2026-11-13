"""Excepciones propias del dominio EcoTech.

Todas heredan de EcoTechError, así el menú puede capturar cualquier error
del negocio con un solo except y mostrar un mensaje claro al usuario.
"""


class EcoTechError(Exception):
    """Excepción base para todos los errores del sistema EcoTech."""


class DatoInvalidoError(EcoTechError, ValueError):
    """Un dato ingresado no cumple las reglas del negocio (texto vacío, email mal escrito, etc.)."""


class RutInvalidoError(DatoInvalidoError):
    """El RUT no tiene formato válido o su dígito verificador no corresponde."""


class SueldoInvalidoError(DatoInvalidoError):
    """El sueldo no es un número mayor que cero."""


class RegistroDuplicadoError(EcoTechError):
    """Se intenta guardar un registro que ya existe (RUT o nombre repetido)."""


class RegistroNoEncontradoError(EcoTechError):
    """El registro buscado no existe en la base de datos."""


class ReferenciaInvalidaError(EcoTechError):
    """Se rompe la integridad referencial (ej. departamento inexistente o con empleados)."""


class PersistenciaError(EcoTechError):
    """Falla técnica de la base de datos (conexión, archivo bloqueado, SQL inválido)."""
