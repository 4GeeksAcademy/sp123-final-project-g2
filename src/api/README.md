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

---

## ✅ Verificación de Datos

### Verificar Usuarios
```bash
#pipenv run flask shell
