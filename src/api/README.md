# 🤟 +Vocal - Guía Completa de Usuarios de Prueba y Documentación de API

Este repositorio contiene el núcleo lógico de **+Vocal**, una plataforma educativa diseñada para enseñar lengua de señas con enfoque regional y gramatical, permitiendo la inclusión real en servicios de atención al público.

---

## 📋 Tabla de Contenidos
- [Usuarios de Prueba](#-usuarios-de-prueba)
- [Todos los Comandos Disponibles](#-todos-los-comandos-disponibles)
- [Verificación de Datos](#-verificación-de-datos)
- [Listado completo de rutas - Sistema educativo LSE](#-listado-completo-de-rutas---sistema-educativo-lse)
- [Flujo de Trabajo (Workflow)](#-flujo-de-trabajo-workflow)

---

## 👥 Usuarios de Prueba

La semilla crea **9 usuarios** con diferentes roles para testear el ecosistema. Todos comparten la misma contraseña: **`Password123!`**

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
| `pipenv run reset-db` | **Reset completo**: migrate + upgrade + seed (Limpieza total) |
| `pipenv run seed` | Ejecuta solo la semilla (repuebla datos sin migrar) |
| `pipenv run insert-test-data` | Comando alternativo para insertar datos de prueba |

### Comandos de Migraciones
| Comando | Descripción |
|---------|-------------|
| `pipenv run init` | Inicializa migraciones (solo primera vez) |
| `pipenv run migrate` | Crea una nueva migración detectando cambios en modelos |
| `pipenv run upgrade` | Aplica todas las migraciones pendientes a la base de datos |
| `pipenv run downgrade` | Revierte la última migración aplicada |

### Comandos del Servidor y Utilidades
| Comando | Descripción |
|---------|-------------|
| `pipenv run start` | Inicia el servidor Flask en puerto **3001** |
| `pipenv run flask shell` | Abre el shell interactivo de Flask |
| `pipenv run flask db history` | Muestra el historial cronológico de cambios |

---

## ✅ Verificación de Datos

### Verificar Usuarios mediante Shell
Para asegurar que los 9 usuarios fueron cargados correctamente:
1. Ejecuta: `pipenv run flask shell`
2. En la consola: `from api.models import User; print(User.query.all())`

---

# ✅ LISTADO COMPLETO DE RUTAS - SISTEMA EDUCATIVO LSE

**Base URL:** `/api`

---

## 1. AUTENTICACIÓN Y USUARIOS
| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| POST | `/register` | Registrar nuevo usuario demo | Público |
| POST | `/login` | Iniciar sesión (Retorna JWT) | Público |
| GET | `/protected` | Verificar token y obtener datos del usuario | Autenticado |
| POST | `/delete-my-account` | Desactivación lógica de cuenta | Autenticado |
| GET | `/users` | Listar usuarios (según permisos) | Admin, Teacher |
| DELETE | `/users/<user_id>` | Eliminar usuario definitivamente | Solo Admin |

## 2. CURSOS Y MÓDULOS
| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/courses-public` | Listar catálogo de cursos activos | Público |
| POST | `/courses-private` | Crear nuevo curso educativo | Admin, Teacher |
| POST | `/modules-private` | Crear nuevo módulo dentro de un curso | Admin, Teacher |
| DELETE | `/modules-private/<module_id>` | Eliminar módulo | Admin, Teacher |

## 3. LECCIONES Y MULTIMEDIA
| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/lessons-private` | Listar todas las lecciones y gramática | Autenticado |
| POST | `/lessons-private` | Cargar nueva lección (Video/Señas) | Admin, Teacher |
| POST | `/multimedia-resources` | Subir nuevo recurso de interpretación | Admin, Teacher |

## 4. GAMIFICACIÓN Y COMPRAS
| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/points-ranking` | Ver tabla de posiciones global | Autenticado |
| POST | `/purchases-private` | Procesar transacción (Stripe/Gratis) | Autenticado |
| POST | `/stripe-webhook` | Procesar eventos automáticos de Stripe | Público (Firma Stripe) |

---

## 🔄 Flujo de Trabajo (Workflow)

Para entender cómo opera **+Vocal**, el ciclo de vida de un usuario es el siguiente:

1.  **Registro:** El usuario se registra como perfil `Demo` (Acceso limitado).
2.  **Exploración:** Accede a las rutas `-public` para ver el catálogo disponible.
3.  **Conversión:** Realiza una compra vía `/purchases-private`. El `Stripe-Webhook` detecta el pago exitoso y actualiza su rol a `Student`.
4.  **Aprendizaje:** El estudiante consume lecciones y módulos. Al completar cada uno, el endpoint `/user-points` le asigna puntaje basado en su desempeño.
5.  **Competencia:** El usuario escala en el `/points-ranking` y desbloquea insignias en `/achievements`.
6.  **Certificación:** Al completar el flujo, el usuario está capacitado para actuar como intérprete en contextos regionales específicos.

***
*Documentación generada para el equipo de desarrollo de +Vocal.*
