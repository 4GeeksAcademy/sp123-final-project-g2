# 🌱 Proyecto Flask - Guía Completa de Usuarios de Prueba y Reset de Base de Datos

---

## 📋 Tabla de Contenidos
- [Usuarios de Prueba](#-usuarios-de-prueba)
- [Todos los Comandos Disponibles](#-todos-los-comandos-disponibles)
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
| 1 | 👑 **Admin** | Admin Señas | admin1@lenguaseñas.com | 5000 | ✅ Sí | N/A |
| 2 | 👑 **Admin** | Admin Inclusivo | admin2@lenguaseñas.com | 3500 | ✅ Sí | N/A |
| 3 | 👨‍🏫 **Teacher** | María Sordomuda | maria.sordomuda@example.com | 1200 | ❌ No | N/A |
| 4 | 👩‍🏫 **Teacher** | Carlos Intérprete | carlos.interprete@example.com | 950 | ❌ No | N/A |
| 5 | 🧑‍🎓 **Student** | Ana Aprende | ana.aprende@example.com  | 450 | ❌ No | N/A |
| 6 | 👨‍🎓 **Student** | Miguel Silente | miguel.silente@example.com | 220 | ❌ No | N/A |
| 7 | 🆓 **Demo** | Pedro DemoSeñas | pedro.demo@lenguaseñas.com | 0 | ❌ No | 4 días |
| 8 | 🆓 **Demo** | María DemoSeñas | maria.demo@lenguaseñas.com | 0 | ❌ No | 1 día |
| 9 | ⚰️ **Inactivo** | Usuario Inactivo | deleted@lenguaseñas.com | 100 | ❌ No | N/A |

---

## 🚀 Todos los Comandos Disponibles

### Comandos de Reset y Datos
| Comando | Descripción |
|---------|-------------|
| `pipenv run reset-db` | **Reset completo**: migrate + upgrade + seed (TODO EN UNO) |
| `pipenv run seed` | Ejecuta solo la semilla (repuebla datos sin migrar) |
| `pipenv run insert-test-data` | Comando alternativo para insertar datos de prueba |

### Comandos de Migraciones
| Comando | Descripción |
|---------|-------------|
| `pipenv run init` | Inicializa migraciones (solo primera vez) |
| `pipenv run migrate` | Crea una nueva migración |
| `pipenv run upgrade` | Aplica todas las migraciones pendientes |
| `pipenv run downgrade` | Revierte la última migración |

### Comandos del Servidor
| Comando | Descripción |
|---------|-------------|
| `pipenv run start` | Inicia el servidor Flask en puerto 3001 |
| `pipenv run local` | Inicia el servidor con heroku local |

### Comandos de Utilidades
| Comando | Descripción |
|---------|-------------|
| `pipenv run reset_db` | Ejecuta script bash para reset de migraciones |
| `pipenv run deploy` | Muestra instrucciones para desplegar |

### Comandos Flask Directos
| Comando | Descripción |
|---------|-------------|
| `pipenv run flask shell` | Abre el shell interactivo de Flask |
| `pipenv run flask db migrate -m "mensaje"` | Crear migración con mensaje descriptivo |
| `pipenv run flask db downgrade <revision>` | Revertir a una versión específica |
| `pipenv run flask db current` | Muestra la migración actual |
| `pipenv run flask db history` | Muestra el historial de migraciones |

### Comandos de Python Directos
| Comando | Descripción |
|---------|-------------|
| `pipenv run python src/api/seed.py` | Ejecuta la semilla directamente |
| `PYTHONPATH=. pipenv run python src/api/seed.py` | Ejecuta semilla con path explícito |

## ✅ Verificación de Datos

### Verificar Usuarios
    `pipenv run flask shell`
---

# LISTADO COMPLETO DE RUTAS - SISTEMA EDUCATIVO LSE

**Base URL:** `/api`

---

## 1. AUTENTICACIÓN Y USUARIOS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| POST | `/register` | Registrar nuevo usuario demo | Público |
| POST | `/login` | Iniciar sesión | Público |
| GET | `/protected` | Verificar token y obtener datos del usuario | Usuario autenticado |
| POST | `/change-password` | Cambiar contraseña del usuario autenticado | Usuario autenticado |
| POST | `/delete-my-account` | Eliminar cuenta propia (desactivación lógica) | Usuario autenticado |
| GET | `/users` | Listar usuarios (admin ve todos, teacher ve sus estudiantes) | Admin, Teacher |
| GET | `/users/<user_id>` | Ver detalles de un usuario específico | Según permisos |
| PUT | `/users/<user_id>` | Actualizar datos de usuario | Según permisos |
| DELETE | `/users/<user_id>` | Eliminar usuario (solo admin) | Admin |

---

## 2. CURSOS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/courses-public` | Listar cursos públicos (solo activos) | Público |
| GET | `/courses-private` | Listar todos los cursos | Usuario autenticado |
| POST | `/courses-private` | Crear nuevo curso | Admin, Teacher |
| GET | `/courses-private/<course_id>` | Ver detalles de un curso | Usuario autenticado |
| PUT | `/courses-private/<course_id>` | Actualizar curso | Admin, Teacher (propios) |
| DELETE | `/courses-private/<course_id>` | Eliminar curso | Admin, Teacher (propios) |

---

## 3. MÓDULOS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/modules-public` | Listar módulos públicos | Público |
| GET | `/modules-private` | Listar todos los módulos | Usuario autenticado |
| POST | `/modules-private` | Crear nuevo módulo | Admin, Teacher |
| GET | `/modules-private/<module_id>` | Ver detalles de un módulo | Usuario autenticado |
| PUT | `/modules-private/<module_id>` | Actualizar módulo | Admin, Teacher (propios) |
| DELETE | `/modules-private/<module_id>` | Eliminar módulo | Admin, Teacher (propios) |

---

## 4. LECCIONES

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/lessons-public` | Listar lecciones públicas | Público |
| GET | `/lessons-private` | Listar todas las lecciones (con multimedia) | Usuario autenticado |
| POST | `/lessons-private` | Crear nueva lección (JSON o multipart) | Admin, Teacher |
| GET | `/lessons-private/<lesson_id>` | Ver detalles de una lección (con multimedia) | Usuario autenticado |
| PUT | `/lessons-private/<lesson_id>` | Actualizar lección | Admin, Teacher (propios) |
| DELETE | `/lessons-private/<lesson_id>` | Eliminar lección | Admin, Teacher (propios) |

---

## 5. COMPRAS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| POST | `/purchases-public` | Verificar curso para compra (info previa) | Público |
| GET | `/purchases-private` | Listar compras del usuario | Usuario autenticado |
| POST | `/purchases-private` | Procesar compra de curso (gratis o pago) | Usuario autenticado |
| GET | `/purchases/<purchase_id>` | Ver detalles de una compra | Según permisos |
| PUT | `/purchases/<purchase_id>` | Actualizar compra (admin) | Admin |
| DELETE | `/purchases/<purchase_id>` | Eliminar compra (admin) | Admin |

---

## 6. PUNTOS Y RANKING

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/points-ranking` | Ver ranking de puntos | Usuario autenticado |
| GET | `/user-points` | Listar registros de puntos | Según permisos |
| POST | `/user-points` | Crear registro de puntos | Admin, Teacher |
| GET | `/user-points/<point_id>` | Ver detalle de punto | Según permisos |
| PUT | `/user-points/<point_id>` | Actualizar punto | Admin, Teacher |
| DELETE | `/user-points/<point_id>` | Eliminar punto | Admin, Teacher |

---

## 7. PROGRESO DE USUARIO

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/userprogress` | Listar progreso de usuarios | Según permisos |
| POST | `/userprogress` | Crear registro de progreso | Admin, Teacher |
| GET | `/userprogress/<progress_id>` | Ver detalle de progreso | Según permisos |
| PUT | `/userprogress/<progress_id>` | Actualizar progreso | Admin, Teacher |
| DELETE | `/userprogress/<progress_id>` | Eliminar progreso | Admin |

---

## 8. LOGROS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/achievements` | Listar todos los logros | Usuario autenticado |
| POST | `/achievements` | Crear nuevo logro | Admin |
| GET | `/achievements/<achievement_id>` | Ver detalle de logro | Usuario autenticado |
| PUT | `/achievements/<achievement_id>` | Actualizar logro | Admin |
| DELETE | `/achievements/<achievement_id>` | Eliminar logro | Admin |
| GET | `/user-achievements` | Listar logros obtenidos por usuarios | Según permisos |
| POST | `/user-achievements` | Asignar logro a usuario | Admin, Teacher |
| GET | `/user-achievements/<user_achievement_id>` | Ver detalle de asignación | Según permisos |
| PUT | `/user-achievements/<user_achievement_id>` | Actualizar asignación | Admin, Teacher |
| DELETE | `/user-achievements/<user_achievement_id>` | Eliminar asignación | Admin |

---

## 9. RECURSOS MULTIMEDIA

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/multimedia-resources` | Listar todos los recursos multimedia | Usuario autenticado |
| POST | `/multimedia-resources` | Crear recurso multimedia | Admin, Teacher |
| GET | `/multimedia-resources/<resource_id>` | Ver detalle de recurso | Usuario autenticado |
| PUT | `/multimedia-resources/<resource_id>` | Actualizar recurso | Admin, Teacher |
| DELETE | `/multimedia-resources/<resource_id>` | Eliminar recurso | Admin |

---

## 10. WEBHOOKS

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| POST | `/stripe-webhook` | Webhook para eventos de Stripe | Público (verificado por firma) |

---
```bash


