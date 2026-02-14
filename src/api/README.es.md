# 🌱 Proyecto Flask - Guía Completa de Usuarios de Prueba y Reset de Base de Datos

---

## 📋 Tabla de Contenidos
- [Usuarios de Prueba](#-usuarios-de-prueba)
- [Comandos para Reiniciar la Base de Datos](#-comandos-para-reiniciar-la-base-de-datos)
- [Comandos para Repoblar Datos (sin migrar)](#-comandos-para-repoblar-datos-sin-migrar)
- [Comandos para Migrar sin Perder Datos](#-comandos-para-migrar-sin-perder-datos)
- [Verificación de Datos](#-verificación-de-datos)
- [Solución de Problemas Comunes](#-solución-de-problemas-comunes)
- [Resumen de Datos Generados](#-resumen-de-datos-generados)
- [Flujo de Trabajo Recomendado](#-flujo-de-trabajo-recomendado)
- [Notas Importantes](#-notas-importantes)
- [Configuración del Pipfile](#-configuración-del-pipfile)

---

## 👥 Usuarios de Prueba

La semilla crea **9 usuarios** con diferentes roles. Todos tienen la misma contraseña para facilitar las pruebas: **`Password123!`**

| # | Rol | Nombre | Email | Puntos | Admin | Trial |
|---|-----|--------|-------|--------|-------|-------|
| 1 | 👑 **Admin** | Admin Principal | admin1@example.com | 5000 | ✅ Sí | N/A |
| 2 | 👑 **Admin** | Admin Secundario | admin2@example.com | 3500 | ✅ Sí | N/A |
| 3 | 👨‍🏫 **Teacher** | Carlos Rodríguez | carlos.rodriguez@example.com | 1200 | ❌ No | N/A |
| 4 | 👩‍🏫 **Teacher** | Laura Martínez | laura.martinez@example.com | 950 | ❌ No | N/A |
| 5 | 🧑‍🎓 **Student** | Ana García | ana.garcia@example.com | 450 | ❌ No | N/A |
| 6 | 👨‍🎓 **Student** | Miguel Sánchez | miguel.sanchez@example.com | 220 | ❌ No | N/A |
| 7 | 🆓 **Demo** | Pedro Demo | pedro.demo@example.com | 0 | ❌ No | 4 días |
| 8 | 🆓 **Demo** | María Demo | maria.demo@example.com | 0 | ❌ No | 1 día |
| 9 | ⚰️ **Inactivo** | Usuario Inactivo | deleted_user@example.com | 100 | ❌ No | N/A |

---

## 🔄 Comandos para Reiniciar la Base de Datos

### Reset Completo (Recomendada)
Este comando hace **TODO** en uno: migra, actualiza y repuebla la base de datos.

pipenv run reset-db

### Reset Datos 
Este comando repuebla la base de datos.

pipenv run seed

### Reset Sin perder Datos
Este comando hace **TODO** en uno: migra, actualiza sin datos.

pipenv run migrate && pipenv run upgrade

### Reset separado
Este comando hace **TODO** en uno: migra, actualiza y repuebla la base de datos.

# Crear una nueva migración
pipenv run migrate

# Aplicar la migración
pipenv run upgrade

```


