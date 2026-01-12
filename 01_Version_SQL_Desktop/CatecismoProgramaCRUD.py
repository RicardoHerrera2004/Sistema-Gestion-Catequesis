import json
import pyodbc
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align

# --- CONFIGURACIÓN VISUAL (ESTILO WEB) ---
console = Console()

# Colores del tema (Coinciden con tu web)
C_PURPLE = "bold #6f42c1"  # Morado vibrante
C_ERROR = "bold red"
C_SUCCESS = "bold green"
C_TEXT = "white"

def crear_conexion():
    try:
        with open("configuracion.json", "r", encoding="utf-8") as f:
            datos_conexion = json.load(f)

        cfg = datos_conexion["sql_server"]
        connection_string = (
            f"DRIVER={cfg['controlador_odbc']};"
            f"SERVER={cfg['name_server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['user']};"
            f"PWD={cfg['password']}"
        )
        return pyodbc.connect(connection_string)
    except Exception as e:
        console.print(f"[{C_ERROR}]Error de conexión config: {e}[/]")
        return None

def mostrar_encabezado(titulo):
    """Crea un encabezado bonito tipo tarjeta web"""
    console.clear()
    console.print(
        Panel(
            Align.center(f"[bold white]{titulo}[/]"), 
            border_style="violet", 
            subtitle="[dim]Sistema de Gestión Pastoral[/]",
            padding=(1, 2)
        )
    )

def mostrar_menu():
    mostrar_encabezado("SISTEMA CATECISMO (SQL SERVER)")
    
    table = Table(box=box.SIMPLE, show_header=False, border_style="dim")
    table.add_column("Opción", style=C_PURPLE, justify="right")
    table.add_column("Descripción", style="white")

    table.add_row("1.", "Consultar Estudiantes")
    table.add_row("2.", "Insertar Nuevo Estudiante")
    table.add_row("3.", "Actualizar Datos")
    table.add_row("4.", "Eliminar Registro")
    table.add_row("5.", "[red]Salir del Sistema[/]")

    console.print(Align.center(table))
    console.print("\n")

def consultar_estudiantes(conexion):
    mostrar_encabezado("📋 LISTA DE ESTUDIANTES")

    try:
        SQL_QUERY = """
        SELECT PersonaID, Nombre, Apellido, Identificacion, Email, Telefono
        FROM Programas.VW_Estudiantes
        """
        cursor = conexion.cursor()
        cursor.execute(SQL_QUERY)
        records = cursor.fetchall()

        if not records:
            console.print(Panel("No hay estudiantes registrados.", style="yellow"))
            input("\nPresiona Enter para volver...")
            return

        # CREAMOS UNA TABLA MODERNA
        table = Table(title="Directorio de Alumnos", box=box.ROUNDED, header_style=C_PURPLE)

        table.add_column("ID", style="dim", justify="right")
        table.add_column("Nombres", style="bold white")
        table.add_column("Apellidos", style="bold white")
        table.add_column("Cédula", style="cyan")
        table.add_column("Email", style="blue")
        table.add_column("Teléfono", style="green")

        for r in records:
            table.add_row(
                str(r.PersonaID), 
                r.Nombre, 
                r.Apellido, 
                r.Identificacion, 
                r.Email or "--", 
                r.Telefono or "--"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[{C_ERROR}]Error al consultar: {e}[/]")
    
    input("\nPresiona Enter para volver...")

def insertar_estudiante(conexion):
    mostrar_encabezado("➕ NUEVO ESTUDIANTE")
    console.print("[dim]Ingresa los datos solicitados. Presiona Enter para omitir opcionales.[/]\n")

    try:
        # Usamos Prompt de Rich para que se vea mejor
        nombre = Prompt.ask(f"[{C_PURPLE}]Nombre[/]")
        apellido = Prompt.ask(f"[{C_PURPLE}]Apellido[/]")
        tipo_doc = Prompt.ask(f"[{C_PURPLE}]Tipo Doc (CI/PAS)[/]", default="CI")
        nro_doc = Prompt.ask(f"[{C_PURPLE}]N° Documento[/]")
        fecha_nac = Prompt.ask(f"[{C_PURPLE}]Fecha Nacimiento (AAAA-MM-DD)[/]")
        telefono = Prompt.ask(f"[{C_PURPLE}]Teléfono[/]")
        email = Prompt.ask(f"[{C_PURPLE}]Email[/]")
        
        console.print("[dim]--- Opcionales ---[/]")
        fecha_bautismo = Prompt.ask("Fecha Bautismo") or None
        lugar_bautismo = Prompt.ask("Lugar Bautismo") or None
        observacion = Prompt.ask("Observación") or None

        cursor = conexion.cursor()
        SENTENCIA_SQL = "EXEC Programas.SP_InsertarEstudiante ?,?,?,?,?,?,?,?,?,?"
        
        cursor.execute(SENTENCIA_SQL, (nombre, apellido, tipo_doc, nro_doc, fecha_nac, telefono, email, fecha_bautismo, lugar_bautismo, observacion))
        resultado = cursor.fetchone()
        conexion.commit()

        # Feedback visual bonito
        if resultado:
             # Ajuste por si devuelve objeto o tupla
            pid = getattr(resultado, 'PersonaIdCreada', resultado[0])
            console.print(Panel(f"✅ Estudiante guardado con éxito.\nID Generado: [bold]{pid}[/]", style=C_SUCCESS))
        else:
            console.print(Panel("✅ Estudiante guardado (Sin ID retornado).", style=C_SUCCESS))

    except Exception as e:
        console.print(Panel(f"❌ Error al guardar: {e}", style=C_ERROR))
    
    input("\nPresiona Enter para volver...")

def actualizar_estudiante(conexion):
    mostrar_encabezado("✏️ ACTUALIZAR ESTUDIANTE")

    try:
        persona_id = int(Prompt.ask(f"[{C_PURPLE}]Ingrese ID del Estudiante[/]"))
        
        console.print(f"\n[dim]Ingrese nuevos datos para el ID {persona_id}:[/]")
        nombre = Prompt.ask("Nuevo Nombre")
        apellido = Prompt.ask("Nuevo Apellido")
        nro_doc = Prompt.ask("Nuevo N° Doc")
        telefono = Prompt.ask("Nuevo Teléfono")
        email = Prompt.ask("Nuevo Email")

        cursor = conexion.cursor()
        SENTENCIA_SQL = "EXEC Programas.SP_ActualizarEstudiante ?,?,?,?,?,?"
        cursor.execute(SENTENCIA_SQL, (persona_id, nombre, apellido, nro_doc, telefono, email))
        conexion.commit()

        console.print(Panel("✅ Datos actualizados correctamente.", style=C_SUCCESS))

    except Exception as e:
        console.print(Panel(f"❌ Error al actualizar: {e}", style=C_ERROR))

    input("\nPresiona Enter para volver...")

def eliminar_estudiante(conexion):
    mostrar_encabezado("🗑️ ELIMINAR ESTUDIANTE")

    try:
        persona_id = int(Prompt.ask(f"[{C_PURPLE}]ID del Estudiante a eliminar[/]"))
        
        # Confirmación de seguridad estilo web
        if Confirm.ask(f"[bold red]¿Estás seguro de eliminar al ID {persona_id}?[/]"):
            cursor = conexion.cursor()
            cursor.execute("EXEC Programas.SP_EliminarEstudiante ?", (persona_id,))
            conexion.commit()
            console.print(Panel("🗑️ Estudiante eliminado permanentemente.", style="bold orange1"))
        else:
            console.print("[dim]Operación cancelada.[/]")

    except Exception as e:
        console.print(Panel(f"❌ Error al eliminar: {e}", style=C_ERROR))

    input("\nPresiona Enter para volver...")

def main():
    with console.status("[bold violet]Conectando a SQL Server...[/]", spinner="dots"):
        conexion = crear_conexion()

    if not conexion:
        return # Salir si falló la conexión

    # Bucle Principal
    while True:
        mostrar_menu()
        opcion = Prompt.ask(f"[{C_PURPLE}]Seleccione una opción[/]", choices=["1", "2", "3", "4", "5"])

        if opcion == '1':
            consultar_estudiantes(conexion)
        elif opcion == '2':
            insertar_estudiante(conexion)
        elif opcion == '3':
            actualizar_estudiante(conexion)
        elif opcion == '4':
            eliminar_estudiante(conexion)
        elif opcion == '5':
            console.print(Panel("👋 ¡Hasta luego! Cerrando sistema...", style="violet"))
            break
    
    if conexion:
        conexion.close()

if __name__ == "__main__":
    main()