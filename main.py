"""Sistema de Gestión de Empleados - EcoTech Solutions (menú por consola).

Ejecutar con:  python main.py
"""
import logging
import sqlite3
import sys

from dominio import Departamento, Empleado, Proyecto, Reportable
from dominio.excepciones import EcoTechError, PersistenciaError
from repositorio import DepartamentoRepositorio, EmpleadoRepositorio, ProyectoRepositorio
from repositorio.conexion import cargar_variables_entorno, inicializar_bd, obtener_conexion


# =====================================================================
# Lectura segura de datos por teclado: nunca dejan caer el programa
# =====================================================================
def pedir_texto(mensaje: str, obligatorio: bool = True, actual: str | None = None) -> str:
    """Si se pasa 'actual', presionar Enter conserva ese valor (modo edición)."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        if actual is not None:
            return actual
        if not obligatorio:
            return ""
        print("  ! Este dato es obligatorio.")


def pedir_entero(mensaje: str, minimo: int = 0, permitir_vacio: bool = False) -> int | None:
    while True:
        texto = input(mensaje).strip()
        if not texto and permitir_vacio:
            return None
        try:
            valor = int(texto)
        except ValueError:
            print("  ! Debe ingresar un número entero.")
            continue
        if valor < minimo:
            print(f"  ! El número debe ser mayor o igual a {minimo}.")
            continue
        return valor


def pedir_monto(mensaje: str, actual: float | None = None) -> float:
    """Acepta '850000', '850.000' o '$850.000' (montos en pesos, sin decimales)."""
    while True:
        texto = input(mensaje).strip().replace("$", "").replace(".", "").replace(" ", "")
        if not texto and actual is not None:
            return actual
        try:
            return float(int(texto))
        except ValueError:
            print("  ! Ingrese un monto en pesos, solo números (ej. 850000).")


def pedir_confirmacion(mensaje: str) -> bool:
    return input(f"{mensaje} (s/n): ").strip().lower() in ("s", "si", "sí")


def titulo(texto: str) -> None:
    print("\n" + "=" * 60)
    print(f" {texto}")
    print("=" * 60)


# =====================================================================
# Aplicación de consola
# =====================================================================
class SistemaEcoTech:
    """Orquesta el menú. No contiene SQL: todo pasa por los repositorios."""

    def __init__(self, conexion: sqlite3.Connection):
        self.empleados = EmpleadoRepositorio(conexion)
        self.departamentos = DepartamentoRepositorio(conexion)
        self.proyectos = ProyectoRepositorio(conexion)

    def ejecutar(self) -> None:
        self._ofrecer_datos_de_ejemplo()
        opciones = {
            "1": self.menu_empleados,
            "2": self.menu_departamentos,
            "3": self.menu_proyectos,
            "4": self.reporte_general,
        }
        while True:
            titulo("EcoTech Solutions - Gestión de Empleados")
            print(" 1. Empleados\n 2. Departamentos\n 3. Proyectos\n 4. Reporte general\n 0. Salir")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                print("Hasta luego.")
                return
            accion = opciones.get(opcion)
            if accion is None:
                print("  ! Opción no válida.")
                continue
            accion()

    def _ejecutar_seguro(self, accion) -> None:
        """Ejecuta una acción del menú y muestra cualquier error del negocio sin cerrar el programa."""
        try:
            accion()
        except EcoTechError as error:
            print(f"  ! {error}")

    def _submenu(self, nombre: str, opciones: dict) -> None:
        while True:
            titulo(nombre)
            for clave, (texto, _) in opciones.items():
                print(f" {clave}. {texto}")
            print(" 0. Volver")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                return
            if opcion not in opciones:
                print("  ! Opción no válida.")
                continue
            self._ejecutar_seguro(opciones[opcion][1])

    # ------------------------- EMPLEADOS -------------------------
    def menu_empleados(self) -> None:
        self._submenu("Empleados", {
            "1": ("Registrar empleado", self.registrar_empleado),
            "2": ("Listar empleados activos", self.listar_empleados),
            "3": ("Buscar por RUT", self.buscar_empleado_rut),
            "4": ("Buscar por nombre", self.buscar_empleado_nombre),
            "5": ("Actualizar empleado", self.actualizar_empleado),
            "6": ("Desvincular empleado", self.desvincular_empleado),
        })

    def registrar_empleado(self) -> None:
        rut = pedir_texto("RUT (ej. 12.345.678-5): ")
        nombre = pedir_texto("Nombre completo: ")
        email = pedir_texto("Email: ")
        telefono = pedir_texto("Teléfono (opcional): ", obligatorio=False)
        cargo = pedir_texto("Cargo: ")
        sueldo = pedir_monto("Sueldo base: $")
        departamento_id = self._elegir_departamento()
        # El constructor valida todo; si algo está mal lanza DatoInvalidoError
        empleado = Empleado(rut, nombre, email, cargo, sueldo,
                            departamento_id=departamento_id, telefono=telefono)
        self.empleados.guardar(empleado)
        print(f"  Empleado {empleado.rut} registrado. Sueldo líquido estimado: ${empleado.calcular_sueldo_liquido():,.0f}")

    def listar_empleados(self) -> None:
        empleados = self.empleados.listar_activos()
        if not empleados:
            print("  No hay empleados activos.")
        for empleado in empleados:
            print(" ", empleado)

    def buscar_empleado_rut(self) -> None:
        print(" ", self.empleados.obtener_por_rut(pedir_texto("RUT: ")))

    def buscar_empleado_nombre(self) -> None:
        resultados = self.empleados.buscar_por_nombre(pedir_texto("Nombre o parte del nombre: "))
        print(f"  {len(resultados)} resultado(s).")
        for empleado in resultados:
            print(" ", empleado)

    def actualizar_empleado(self) -> None:
        empleado = self.empleados.obtener_por_rut(pedir_texto("RUT del empleado a actualizar: "))
        print("  Presione Enter para conservar el valor actual.")
        empleado.nombre = pedir_texto(f"Nombre [{empleado.nombre}]: ", actual=empleado.nombre)
        empleado.email = pedir_texto(f"Email [{empleado.email}]: ", actual=empleado.email)
        empleado.telefono = pedir_texto(f"Teléfono [{empleado.telefono}]: ", actual=empleado.telefono)
        empleado.cargo = pedir_texto(f"Cargo [{empleado.cargo}]: ", actual=empleado.cargo)
        empleado.sueldo_base = pedir_monto(f"Sueldo base [${empleado.sueldo_base:,.0f}]: $", actual=empleado.sueldo_base)
        if pedir_confirmacion("¿Cambiar de departamento?"):
            empleado.departamento_id = self._elegir_departamento()
        self.empleados.actualizar(empleado)
        print("  Empleado actualizado.")

    def desvincular_empleado(self) -> None:
        rut = pedir_texto("RUT del empleado a desvincular: ")
        empleado = self.empleados.obtener_por_rut(rut)
        if pedir_confirmacion(f"¿Desvincular a {empleado.nombre}?"):
            self.empleados.eliminar(empleado.rut)
            print("  Empleado desvinculado (borrado lógico, se conserva el historial).")

    def _elegir_departamento(self) -> int | None:
        departamentos = self.departamentos.listar_todos()
        for departamento in departamentos:
            print(f"   {departamento.id}. {departamento.nombre}")
        return pedir_entero("Id de departamento (Enter = sin departamento): ", minimo=1, permitir_vacio=True)

    # ----------------------- DEPARTAMENTOS -----------------------
    def menu_departamentos(self) -> None:
        self._submenu("Departamentos", {
            "1": ("Crear departamento", self.crear_departamento),
            "2": ("Listar departamentos", self.listar_departamentos),
            "3": ("Ver empleados de un departamento", self.empleados_de_departamento),
            "4": ("Actualizar departamento", self.actualizar_departamento),
            "5": ("Eliminar departamento", self.eliminar_departamento),
        })

    def crear_departamento(self) -> None:
        departamento = Departamento(pedir_texto("Nombre: "), pedir_monto("Presupuesto anual: $"))
        nuevo_id = self.departamentos.guardar(departamento)
        print(f"  Departamento creado con id {nuevo_id}.")

    def listar_departamentos(self) -> None:
        departamentos = self.departamentos.listar_todos()
        if not departamentos:
            print("  No hay departamentos registrados.")
        for departamento in departamentos:
            print(" ", departamento)

    def empleados_de_departamento(self) -> None:
        departamento = self.departamentos.obtener_por_id(pedir_entero("Id de departamento: ", minimo=1))
        empleados = self.empleados.listar_por_departamento(departamento.id)
        print(f"  {departamento.nombre}: {len(empleados)} empleado(s) activo(s)")
        for empleado in empleados:
            print(" ", empleado)

    def actualizar_departamento(self) -> None:
        departamento = self.departamentos.obtener_por_id(pedir_entero("Id de departamento: ", minimo=1))
        departamento.nombre = pedir_texto(f"Nombre [{departamento.nombre}]: ", actual=departamento.nombre)
        departamento.presupuesto = pedir_monto(f"Presupuesto [${departamento.presupuesto:,.0f}]: $",
                                               actual=departamento.presupuesto)
        self.departamentos.actualizar(departamento)
        print("  Departamento actualizado.")

    def eliminar_departamento(self) -> None:
        departamento = self.departamentos.obtener_por_id(pedir_entero("Id de departamento: ", minimo=1))
        if pedir_confirmacion(f"¿Eliminar el departamento '{departamento.nombre}'?"):
            self.departamentos.eliminar(departamento.id)
            print("  Departamento eliminado.")

    # ------------------------- PROYECTOS -------------------------
    def menu_proyectos(self) -> None:
        self._submenu("Proyectos", {
            "1": ("Crear proyecto", self.crear_proyecto),
            "2": ("Listar proyectos", self.listar_proyectos),
            "3": ("Asignar empleado a proyecto", self.asignar_empleado),
            "4": ("Quitar empleado de proyecto", self.quitar_empleado),
            "5": ("Actualizar proyecto", self.actualizar_proyecto),
            "6": ("Eliminar proyecto", self.eliminar_proyecto),
        })

    def crear_proyecto(self) -> None:
        proyecto = Proyecto(
            nombre=pedir_texto("Nombre: "),
            descripcion=pedir_texto("Descripción (opcional): ", obligatorio=False),
            fecha_inicio=pedir_texto("Fecha de inicio AAAA-MM-DD (Enter = hoy): ", obligatorio=False) or None,
        )
        nuevo_id = self.proyectos.guardar(proyecto)
        print(f"  Proyecto creado con id {nuevo_id}.")

    def listar_proyectos(self) -> None:
        proyectos = self.proyectos.listar_todos()
        if not proyectos:
            print("  No hay proyectos registrados.")
        for proyecto in proyectos:
            print(" ", proyecto)
            for rut in proyecto.ruts_asignados:
                print(f"      - {rut}")

    def asignar_empleado(self) -> None:
        id_proyecto = pedir_entero("Id de proyecto: ", minimo=1)
        self.proyectos.asignar_empleado(id_proyecto, pedir_texto("RUT del empleado: "))
        print("  Empleado asignado al proyecto.")

    def quitar_empleado(self) -> None:
        id_proyecto = pedir_entero("Id de proyecto: ", minimo=1)
        self.proyectos.quitar_empleado(id_proyecto, pedir_texto("RUT del empleado: "))
        print("  Empleado quitado del proyecto.")

    def actualizar_proyecto(self) -> None:
        proyecto = self.proyectos.obtener_por_id(pedir_entero("Id de proyecto: ", minimo=1))
        proyecto.nombre = pedir_texto(f"Nombre [{proyecto.nombre}]: ", actual=proyecto.nombre)
        proyecto.descripcion = pedir_texto(f"Descripción [{proyecto.descripcion}]: ", actual=proyecto.descripcion)
        proyecto.fecha_inicio = pedir_texto(f"Fecha de inicio [{proyecto.fecha_inicio}]: ", actual=proyecto.fecha_inicio)
        self.proyectos.actualizar(proyecto)
        print("  Proyecto actualizado.")

    def eliminar_proyecto(self) -> None:
        proyecto = self.proyectos.obtener_por_id(pedir_entero("Id de proyecto: ", minimo=1))
        if pedir_confirmacion(f"¿Eliminar el proyecto '{proyecto.nombre}' y sus asignaciones?"):
            self.proyectos.eliminar(proyecto.id)
            print("  Proyecto eliminado.")

    # ---------------------- REPORTE GENERAL ----------------------
    def reporte_general(self) -> None:
        """Polimorfismo: una sola lista con objetos de 3 clases distintas.

        No se pregunta el tipo de cada objeto (sin if/isinstance): cada uno
        sabe cómo resumirse porque todos cumplen la interfaz Reportable.
        """
        try:
            empleados = self.empleados.listar_activos()
            entidades: list[Reportable] = [
                *self.departamentos.listar_todos(),
                *empleados,
                *self.proyectos.listar_todos(),
            ]
        except EcoTechError as error:
            print(f"  ! {error}")
            return
        titulo("Reporte general")
        for entidad in entidades:
            print(entidad.resumen())
        total_liquido = sum(e.calcular_sueldo_liquido() for e in empleados)
        print("-" * 60)
        print(f"Total sueldos líquidos del mes: ${total_liquido:,.0f}")

    # --------------------- DATOS DE EJEMPLO ----------------------
    def _ofrecer_datos_de_ejemplo(self) -> None:
        try:
            vacio = not self.departamentos.listar_todos() and not self.empleados.listar_activos()
            if vacio and pedir_confirmacion("La base de datos está vacía. ¿Cargar datos de ejemplo?"):
                self.cargar_datos_de_ejemplo()
                print("  Datos de ejemplo cargados.")
        except EcoTechError as error:
            print(f"  ! No se pudieron cargar los datos de ejemplo: {error}")

    def cargar_datos_de_ejemplo(self) -> None:
        ti = self.departamentos.guardar(Departamento("Tecnología", 120_000_000))
        rrhh = self.departamentos.guardar(Departamento("Recursos Humanos", 45_000_000))
        sus = self.departamentos.guardar(Departamento("Sustentabilidad", 60_000_000))
        datos = [
            ("12.345.678-5", "Camila Rojas", "camila.rojas@ecotech.cl", "Gerente de TI", 2_400_000, "2019-03-01", ti),
            ("15.678.234-3", "Diego Muñoz", "diego.munoz@ecotech.cl", "Desarrollador", 1_350_000, "2021-07-15", ti),
            ("18.234.567-9", "Valentina Soto", "valentina.soto@ecotech.cl", "Analista RR.HH.", 1_100_000, "2022-01-10", rrhh),
            ("19.876.543-0", "Matías Fuentes", "matias.fuentes@ecotech.cl", "Ingeniero Ambiental", 1_500_000, "2023-05-02", sus),
        ]
        for rut, nombre, email, cargo, sueldo, ingreso, depto in datos:
            self.empleados.guardar(Empleado(rut, nombre, email, cargo, sueldo, ingreso, depto))
        self.proyectos.guardar(Proyecto("Paneles Solares Planta Sur", "Instalación de energía solar", "2026-08-01",
                                        ruts_asignados=["15.678.234-3", "19.876.543-0"]))


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")
    cargar_variables_entorno()
    try:
        conexion = obtener_conexion()
        inicializar_bd(conexion)
    except PersistenciaError as error:
        print(f"No se pudo iniciar el sistema: {error}")
        return 1
    try:
        SistemaEcoTech(conexion).ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo del sistema...")
    finally:
        conexion.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
