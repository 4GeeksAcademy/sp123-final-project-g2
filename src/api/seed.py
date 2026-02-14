"""
Script para poblar la base de datos con datos de prueba
Ejecutar con: flask shell < api/seed.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timezone, timedelta
import random
from werkzeug.security import generate_password_hash

from api.models import db, Users, Courses, Modules, Lessons, MultimediaResources
from api.models import Purchases, Achievements, UserPoints, UserProgress, UserAchievements

from src.app import app




class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def clear_tables():
    print_info("Limpiando tablas existentes...")
    MultimediaResources.query.delete()
    UserProgress.query.delete()
    UserPoints.query.delete()
    UserAchievements.query.delete()
    Purchases.query.delete()
    Lessons.query.delete()
    Modules.query.delete()
    Courses.query.delete()
    Achievements.query.delete()
    Users.query.delete()
    db.session.commit()
    print_success("Tablas limpiadas")

# EJECUTAR CON: flask shell < api/seed.py
with app.app_context():
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}🌱 INICIANDO SEMILLA DE BASE DE DATOS{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    # Limpiar datos existentes
    clear_tables()
    
    # --- PASO 2: Usuarios ---
    print_info("Creando usuarios...")
    common_password = generate_password_hash("Password123!")
    usuarios = []
    
    # 2 Administradores
    admin1 = Users(first_name="Admin", last_name="Principal", email="admin1@example.com",
                   password_hash=common_password, role="teacher", is_admin=True, is_active=True,
                   current_points=5000, registration_date=datetime.now(timezone.utc) - timedelta(days=180))
    usuarios.append(admin1)
    
    admin2 = Users(first_name="Admin", last_name="Secundario", email="admin2@example.com",
                   password_hash=common_password, role="teacher", is_admin=True, is_active=True,
                   current_points=3500, registration_date=datetime.now(timezone.utc) - timedelta(days=90))
    usuarios.append(admin2)
    
    # 2 Profesores
    teacher1 = Users(first_name="Carlos", last_name="Rodríguez", email="carlos.rodriguez@example.com",
                     password_hash=common_password, role="teacher", is_admin=False, is_active=True,
                     current_points=1200, registration_date=datetime.now(timezone.utc) - timedelta(days=60))
    usuarios.append(teacher1)
    
    teacher2 = Users(first_name="Laura", last_name="Martínez", email="laura.martinez@example.com",
                     password_hash=common_password, role="teacher", is_admin=False, is_active=True,
                     current_points=950, registration_date=datetime.now(timezone.utc) - timedelta(days=45))
    usuarios.append(teacher2)
    
    # 2 Estudiantes
    student1 = Users(first_name="Ana", last_name="García", email="ana.garcia@example.com",
                     password_hash=common_password, role="student", is_admin=False, is_active=True,
                     current_points=450, registration_date=datetime.now(timezone.utc) - timedelta(days=30))
    usuarios.append(student1)
    
    student2 = Users(first_name="Miguel", last_name="Sánchez", email="miguel.sanchez@example.com",
                     password_hash=common_password, role="student", is_admin=False, is_active=True,
                     current_points=220, registration_date=datetime.now(timezone.utc) - timedelta(days=15))
    usuarios.append(student2)
    
    # 2 Usuarios Demo
    demo1 = Users(first_name="Pedro", last_name="Demo", email="pedro.demo@example.com",
                  password_hash=common_password, role="demo", is_admin=False, is_active=True,
                  current_points=0, registration_date=datetime.now(timezone.utc) - timedelta(days=3),
                  trial_end_date=datetime.now(timezone.utc) + timedelta(days=4))
    usuarios.append(demo1)
    
    demo2 = Users(first_name="María", last_name="Demo", email="maria.demo@example.com",
                  password_hash=common_password, role="demo", is_admin=False, is_active=True,
                  current_points=0, registration_date=datetime.now(timezone.utc) - timedelta(days=6),
                  trial_end_date=datetime.now(timezone.utc) + timedelta(days=1))
    usuarios.append(demo2)
    
    # 1 Usuario inactivo
    inactive_user = Users(first_name="Usuario", last_name="Inactivo", email="deleted_user@example.com",
                          password_hash=common_password, role="student", is_admin=False, is_active=False,
                          current_points=100, registration_date=datetime.now(timezone.utc) - timedelta(days=100),
                          deleted_at=datetime.now(timezone.utc) - timedelta(days=10),
                          original_email="original@example.com", deletion_uuid="abc12345")
    usuarios.append(inactive_user)
    
    for user in usuarios:
        db.session.add(user)
    db.session.commit()
    print_success(f"{len(usuarios)} usuarios creados")
    
    admin_ids = [admin1.user_id, admin2.user_id]
    teacher_ids = [teacher1.user_id, teacher2.user_id]
    student_ids = [student1.user_id, student2.user_id]
    demo_ids = [demo1.user_id, demo2.user_id]
    
    # --- PASO 3: Cursos ---
    print_info("Creando cursos...")
    cursos = []
    
    curso1_teacher1 = Courses(title="Python desde Cero", description="Aprende Python desde lo más básico.",
                              price=49.99, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=50),
                              points=500, created_by=teacher_ids[0])
    cursos.append(curso1_teacher1)
    
    curso2_teacher1 = Courses(title="Flask Avanzado", description="Domina Flask y crea APIs profesionales.",
                              price=79.99, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=30),
                              points=750, created_by=teacher_ids[0])
    cursos.append(curso2_teacher1)
    
    curso3_teacher1 = Courses(title="SQL para Desarrolladores", description="Aprende SQL desde cero.",
                              price=39.99, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=20),
                              points=400, created_by=teacher_ids[0])
    cursos.append(curso3_teacher1)
    
    curso1_teacher2 = Courses(title="React Moderno", description="Aprende React con Hooks y Context API.",
                              price=89.99, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=40),
                              points=800, created_by=teacher_ids[1])
    cursos.append(curso1_teacher2)
    
    curso2_teacher2 = Courses(title="TypeScript Total", description="TypeScript desde cero hasta avanzado.",
                              price=69.99, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=25),
                              points=600, created_by=teacher_ids[1])
    cursos.append(curso2_teacher2)
    
    curso_gratis = Courses(title="HTML y CSS para Principiantes", description="Curso gratuito de fundamentos.",
                           price=0.00, is_active=True, creation_date=datetime.now(timezone.utc) - timedelta(days=60),
                           points=300, created_by=teacher_ids[1])
    cursos.append(curso_gratis)
    
    curso_inactivo = Courses(title="Curso Descontinuado", description="Curso inactivo.",
                             price=29.99, is_active=False, creation_date=datetime.now(timezone.utc) - timedelta(days=200),
                             points=200, created_by=teacher_ids[0])
    cursos.append(curso_inactivo)
    
    for curso in cursos:
        db.session.add(curso)
    db.session.commit()
    print_success(f"{len(cursos)} cursos creados")
    
    # --- PASO 4: Módulos ---
    print_info("Creando módulos...")
    modulos = []
    
    def crear_modulos_para_curso(curso_id, titulos, puntos=None):
        if puntos is None:
            puntos = [100] * len(titulos)
        for i, titulo in enumerate(titulos, 1):
            modulos.append(Modules(title=titulo, order=i, points=puntos[min(i-1, len(puntos)-1)],
                                    is_active=True, course_id=curso_id))
    
    crear_modulos_para_curso(curso1_teacher1.course_id,
        ["Introducción", "Variables", "Estructuras", "Funciones", "Listas", "Archivos"],
        [50, 75, 100, 125, 150, 200])
    
    crear_modulos_para_curso(curso2_teacher1.course_id,
        ["Introducción", "Rutas", "BD SQLAlchemy", "JWT", "APIs REST", "Despliegue"],
        [80, 100, 150, 200, 250, 300])
    
    crear_modulos_para_curso(curso1_teacher2.course_id,
        ["Fundamentos", "Componentes", "Estado", "Hooks Básicos", "Hooks Avanzados", "Context", "Router", "Optimización"],
        [60, 80, 100, 120, 150, 180, 200, 220])
    
    crear_modulos_para_curso(curso_gratis.course_id,
        ["HTML Intro", "Etiquetas", "CSS Básico", "Flexbox"], [50, 75, 100, 125])
    
    for modulo in modulos:
        db.session.add(modulo)
    db.session.commit()
    print_success(f"{len(modulos)} módulos creados")
    
    # --- PASO 5: Lecciones ---
    print_info("Creando lecciones...")
    lecciones = []
    
    def crear_lecciones_para_modulo(module_id, num_lecciones=4, trial_visible=False):
        for i in range(1, num_lecciones + 1):
            lecciones.append(Lessons(
                title=f"Lección {i} del Módulo",
                content="Contenido detallado de la lección con ejemplos y ejercicios.",
                learning_objective="Objetivo de aprendizaje de esta lección.",
                signs_taught=f"Concepto {i}, Ejemplo {i}",
                order=i, trial_visible=trial_visible and i <= 2,
                is_active=True, module_id=module_id))
    
    modulos_por_curso = {}
    for m in modulos:
        modulos_por_curso.setdefault(m.course_id, []).append(m)
    
    for course_id, modulos_del_curso in modulos_por_curso.items():
        es_gratis = any(c.price == 0 for c in cursos if c.course_id == course_id)
        for modulo in modulos_del_curso:
            crear_lecciones_para_modulo(modulo.module_id, random.randint(3, 5),
                                        trial_visible=(es_gratis or modulo.order == 1))
    
    for leccion in lecciones:
        db.session.add(leccion)
    db.session.commit()
    print_success(f"{len(lecciones)} lecciones creadas")
    
    # --- PASO 6: Recursos Multimedia ---
    print_info("Creando recursos multimedia...")
    recursos = []
    urls = {'video': ["vid1.mp4", "vid2.mp4"], 'image': ["img1.jpg", "img2.jpg", "img3.jpg"],
            'gif': ["gif1.gif", "gif2.gif"], 'document': ["doc1.pdf", "doc2.docx"]}
    
    for leccion in random.sample(lecciones, min(15, len(lecciones))):
        tipos_usados = []
        for i in range(random.randint(1, 3)):
            tipo = random.choice([t for t in ['video', 'image', 'gif', 'document'] if t not in tipos_usados] or ['image'])
            tipos_usados.append(tipo)
            recursos.append(MultimediaResources(
                lesson_id=leccion.lesson_id, resource_type=tipo,
                url=f"https://ejemplo.com/{random.choice(urls[tipo])}",
                duration_seconds=random.choice([60, 120, 300]) if tipo == 'video' else None,
                description=f"Recurso {tipo}", order=i+1))
    
    for recurso in recursos:
        db.session.add(recurso)
    db.session.commit()
    print_success(f"{len(recursos)} recursos creados")
    
    # --- PASO 7: Compras ---
    print_info("Creando compras...")
    compras = []
    
    curso_python = next(c for c in cursos if c.title == "Python desde Cero")
    compras.append(Purchases(purchase_date=datetime.now(timezone.utc)-timedelta(days=25),
                             price=curso_python.price, total=curso_python.price, status='paid',
                             start_date=datetime.now(timezone.utc)-timedelta(days=25),
                             course_id=curso_python.course_id, user_id=student_ids[0]))
    
    compras.append(Purchases(purchase_date=datetime.now(timezone.utc)-timedelta(days=10),
                             price=0, total=0, status='paid',
                             start_date=datetime.now(timezone.utc)-timedelta(days=10),
                             course_id=curso_gratis.course_id, user_id=student_ids[0]))
    
    curso_react = next(c for c in cursos if c.title == "React Moderno")
    compras.append(Purchases(purchase_date=datetime.now(timezone.utc)-timedelta(days=5),
                             price=curso_react.price, total=curso_react.price, status='paid',
                             start_date=datetime.now(timezone.utc)-timedelta(days=5),
                             course_id=curso_react.course_id, user_id=student_ids[1]))
    
    compras.append(Purchases(purchase_date=datetime.now(timezone.utc)-timedelta(hours=2),
                             price=79.99, total=79.99, status='pending', start_date=None,
                             course_id=curso_react.course_id, user_id=student_ids[0],
                             stripe_payment_intent_id="pi_test_pending_123456"))
    
    for compra in compras:
        db.session.add(compra)
    db.session.commit()
    print_success(f"{len(compras)} compras creadas")
    
    # --- PASO 8: Puntos de Usuario ---
    print_info("Creando historial de puntos...")
    puntos = []
    
    for leccion in random.sample(lecciones, 8):
        puntos.append(UserPoints(user_id=student_ids[0], points=random.choice([10,20,30]),
                                 point_type='lesson', event_description=f"Lección: {leccion.title[:30]}",
                                 date=datetime.now(timezone.utc)-timedelta(days=random.randint(1,20))))
    
    for leccion in random.sample(lecciones, 5):
        puntos.append(UserPoints(user_id=student_ids[1], points=random.choice([10,20]),
                                 point_type='lesson', event_description=f"Lección: {leccion.title[:30]}",
                                 date=datetime.now(timezone.utc)-timedelta(days=random.randint(1,10))))
    
    puntos.append(UserPoints(user_id=teacher_ids[0], points=500, point_type='course',
                             event_description="Creación: Python desde Cero",
                             date=datetime.now(timezone.utc)-timedelta(days=50)))
    
    puntos.append(UserPoints(user_id=teacher_ids[1], points=800, point_type='course',
                             event_description="Creación: React Moderno",
                             date=datetime.now(timezone.utc)-timedelta(days=40)))
    
    for punto in puntos:
        db.session.add(punto)
    db.session.commit()
    
    for uid in student_ids + teacher_ids:
        total = db.session.query(db.func.sum(UserPoints.points)).filter(UserPoints.user_id == uid).scalar() or 0
        Users.query.get(uid).current_points = total
    db.session.commit()
    print_success(f"{len(puntos)} puntos creados")
    
    # --- PASO 9: Progreso de Usuarios ---
    print_info("Creando progreso...")
    progresos = []
    
    lecciones_python = [l for l in lecciones if l.module_id in [m.module_id for m in modulos_por_curso[curso_python.course_id]]]
    for i, l in enumerate(lecciones_python[:10]):
        prog = i < 8
        progresos.append(UserProgress(user_id=student_ids[0], lesson_id=l.lesson_id, completed=prog,
                                      start_date=datetime.now(timezone.utc)-timedelta(days=20+i),
                                      completion_date=datetime.now(timezone.utc)-timedelta(days=15+i) if prog else None))
    
    lecciones_react = [l for l in lecciones if l.module_id in [m.module_id for m in modulos_por_curso[curso_react.course_id]]]
    for i, l in enumerate(lecciones_react[:6]):
        prog = i < 4
        progresos.append(UserProgress(user_id=student_ids[1], lesson_id=l.lesson_id, completed=prog,
                                      start_date=datetime.now(timezone.utc)-timedelta(days=10+i),
                                      completion_date=datetime.now(timezone.utc)-timedelta(days=8+i) if prog else None))
    
    for prog in progresos:
        db.session.add(prog)
    db.session.commit()
    print_success(f"{len(progresos)} progresos creados")
    
    # --- PASO 10: Logros ---
    print_info("Creando logros...")
    logros = []
    datos_logros = [
        ("Primeros Pasos", "Completa tu primera lección", 10, "🏁"),
        ("Estudiante Constante", "Completa 10 lecciones", 100, "📚"),
        ("Maestro del Python", "Completa el curso de Python", 500, "🐍"),
        ("Experto en React", "Completa el curso de React", 800, "⚛️"),
        ("Coleccionista", "Acumula 1000 puntos", 1000, "⭐"),
        ("Profesor Destacado", "Crea un curso exitoso", 1000, "👨‍🏫"),
        ("Madrugador", "Regístrate temprano", 50, "🌅"),
        ("Explorador", "Prueba todos los recursos", 200, "🧭")
    ]
    
    for nombre, desc, pts, icono in datos_logros:
        logros.append(Achievements(name=nombre, description=desc, required_points=pts, icon=icono))
    
    for logro in logros:
        db.session.add(logro)
    db.session.commit()
    print_success(f"{len(logros)} logros creados")
    
    # --- PASO 11: Asignar Logros ---
    print_info("Asignando logros...")
    asignaciones = []
    
    logro1 = next(l for l in logros if l.name == "Primeros Pasos")
    logro2 = next(l for l in logros if l.name == "Estudiante Constante")
    logro3 = next(l for l in logros if l.name == "Madrugador")
    logro4 = next(l for l in logros if l.name == "Profesor Destacado")
    
    asignaciones.extend([
        UserAchievements(user_id=student_ids[0], achievement_id=logro1.achievement_id,
                        obtained_date=datetime.now(timezone.utc)-timedelta(days=25)),
        UserAchievements(user_id=student_ids[0], achievement_id=logro2.achievement_id,
                        obtained_date=datetime.now(timezone.utc)-timedelta(days=10)),
        UserAchievements(user_id=student_ids[0], achievement_id=logro3.achievement_id,
                        obtained_date=datetime.now(timezone.utc)-timedelta(days=30)),
        UserAchievements(user_id=student_ids[1], achievement_id=logro1.achievement_id,
                        obtained_date=datetime.now(timezone.utc)-timedelta(days=12)),
        UserAchievements(user_id=teacher_ids[0], achievement_id=logro4.achievement_id,
                        obtained_date=datetime.now(timezone.utc)-timedelta(days=30))
    ])
    
    for asig in asignaciones:
        db.session.add(asig)
    db.session.commit()
    print_success(f"{len(asignaciones)} logros asignados")
    
    # --- FINAL ---
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ SEMILLA COMPLETADA EXITOSAMENTE{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")