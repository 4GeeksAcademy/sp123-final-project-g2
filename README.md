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
pipenv run flask shell

# WebApp boilerplate with React JS and Flask API

Build web applications using React.js for the front end and python/flask for your backend API.

- Documentation can be found here: https://4geeks.com/docs/start/react-flask-template
- Here is a video on [how to use this template](https://www.loom.com/share/f37c6838b3f1496c95111e515e83dd9b)
- Integrated with Pipenv for package managing.
- Fast deployment to Render [in just a few steps here](https://4geeks.com/docs/start/deploy-to-render-com).
- Use of .env file.
- SQLAlchemy integration for database abstraction.

### 1) Installation:

> If you use Github Codespaces (recommended) or Gitpod this template will already come with Python, Node and the Posgres Database installed. If you are working locally make sure to install Python 3.10, Node 

It is recomended to install the backend first, make sure you have Python 3.10, Pipenv and a database engine (Posgress recomended)

1. Install the python packages: `$ pipenv install`
2. Create a .env file based on the .env.example: `$ cp .env.example .env`
3. Install your database engine and create your database, depending on your database you have to create a DATABASE_URL variable with one of the possible values, make sure you replace the valudes with your database information:

| Engine    | DATABASE_URL                                        |
| --------- | --------------------------------------------------- |
| SQLite    | sqlite:////test.db                                  |
| MySQL     | mysql://username:password@localhost:port/example    |
| Postgress | postgres://username:password@localhost:5432/example |

4. Migrate the migrations: `$ pipenv run migrate` (skip if you have not made changes to the models on the `./src/api/models.py`)
5. Run the migrations: `$ pipenv run upgrade`
6. Run the application: `$ pipenv run start`

> Note: Codespaces users can connect to psql by typing: `psql -h localhost -U gitpod example`

### Undo a migration

You are also able to undo a migration by running

```sh
$ pipenv run downgrade
```

### Backend Populate Table Users

To insert test users in the database execute the following command:

```sh
$ flask insert-test-users 5
```

And you will see the following message:

```
  Creating test users
  test_user1@test.com created.
  test_user2@test.com created.
  test_user3@test.com created.
  test_user4@test.com created.
  test_user5@test.com created.
  Users created successfully!
```

### **Important note for the database and the data inside it**

Every Github codespace environment will have **its own database**, so if you're working with more people eveyone will have a different database and different records inside it. This data **will be lost**, so don't spend too much time manually creating records for testing, instead, you can automate adding records to your database by editing ```commands.py``` file inside ```/src/api``` folder. Edit line 32 function ```insert_test_data``` to insert the data according to your model (use the function ```insert_test_users``` above as an example). Then, all you need to do is run ```pipenv run insert-test-data```.

### Front-End Manual Installation:

-   Make sure you are using node version 20 and that you have already successfully installed and runned the backend.

1. Install the packages: `$ npm install`
2. Start coding! start the webpack dev server `$ npm run start`

## Publish your website!

This boilerplate it's 100% read to deploy with Render.com and Heroku in a matter of minutes. Please read the [official documentation about it](https://4geeks.com/docs/start/deploy-to-render-com).

### Contributors

This template was built as part of the 4Geeks Academy [Coding Bootcamp](https://4geeksacademy.com/us/coding-bootcamp) by [Alejandro Sanchez](https://twitter.com/alesanchezr) and many other contributors. Find out more about our [Full Stack Developer Course](https://4geeksacademy.com/us/coding-bootcamps/part-time-full-stack-developer), and [Data Science Bootcamp](https://4geeksacademy.com/us/coding-bootcamps/datascience-machine-learning).

You can find other templates and resources like this at the [school github page](https://github.com/4geeksacademy/).
