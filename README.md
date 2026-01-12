# ✝️ Sistema de Gestión de Catequesis (Proyecto Integrador)

Este repositorio contiene la evolución del sistema de gestión pastoral, demostrando la implementación tanto en arquitectura **SQL Tradicional** como en **NoSQL Moderna**.

## Estructura del Proyecto

### 1. Versión de Escritorio (SQL)
Ubicación: `/01_Version_SQL_Desktop`
* **Tecnología:** Python + SQL Server (PyODBC).
* **Interfaz:** Consola Interactiva (CLI) con diseño moderno usando `Rich`.
* **Base de Datos:** Relacional (Tablas, Stored Procedures).

### 2. Versión Web (NoSQL)
Ubicación: `/02_Version_NoSQL_Web`
* **Tecnología:** Python Flask + MongoDB Atlas.
* **Interfaz:** Web App Responsive con Bootstrap 5 (Diseño Purple/Dark).
* **Base de Datos:** Documental (JSON/BSON), flexible y escalable.

## Cómo ejecutar

### Versión Web
1. Entrar a la carpeta: `cd 02_Version_NoSQL_Web`
2. Instalar dependencias: `pip install flask pymongo`
3. Ejecutar: `python app.py`

### Versión Escritorio
1. Entrar a la carpeta: `cd 01_Version_SQL_Desktop`
2. Instalar dependencias: `pip install pyodbc rich`
3. Ejecutar: `python CatecismoProgramaCRUD.py`

---
Desarrollado por: **Ricardo Herrera, Pablo Vargas y Daniel Sierra**
