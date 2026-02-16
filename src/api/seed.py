"""
Script para poblar la base de datos con datos de prueba - LENGUA DE SEÑAS
"""
import sys
import os
from datetime import datetime, timezone, timedelta
import random
from werkzeug.security import generate_password_hash




# Obtener la ruta absoluta 
current_dir = os.path.dirname(os.path.abspath(__file__))  # src/api/
parent_dir = os.path.dirname(current_dir)                  # src/
root_dir = os.path.dirname(parent_dir)                     # raíz del proyecto

# Agregar TODAS las rutas necesarias al path de Python
sys.path.insert(0, root_dir)      # Para importar src
sys.path.insert(0, parent_dir)     # Para importar api
sys.path.insert(0, current_dir)    # Para importar desde api/

# Ahora intentamos importar la app
try:
    from src.app import app
    print("✅ App importada correctamente")
except ImportError as e:
    print(f"⚠️ Error en primer intento: {e}")
    try:
        import sys
        sys.path.insert(0, os.path.join(root_dir, 'src'))
        from app import app
        print("✅ App importada (segundo intento)")
    except ImportError as e2:
        print(f"❌ Error importando app: {e2}")
        sys.exit(1)

# Importar modelos directamente desde los archivos
from api.models import db, Users, Courses, Modules, Lessons, MultimediaResources
from api.models import Purchases, Achievements, UserPoints, UserProgress, UserAchievements

# Colores para prints
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
    """Limpia todas las tablas en orden correcto (respetando FK)"""
    print_info("Limpiando tablas existentes...")
    
    # Orden correcto para eliminar (hijos primero)
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

def run_seed():
    """Función principal que ejecuta la semilla"""
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}🌱 INICIANDO SEMILLA DE LENGUA DE SEÑAS{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    # Limpiar datos existentes
    clear_tables()
    
    # --- PASO 2: Usuarios ---
    print_info("Creando usuarios...")
    common_password = generate_password_hash("Password123!")
    usuarios = []
    
    # 2 Administradores
    admin1 = Users(
        first_name="Admin", 
        last_name="Señas", 
        email="admin1@lenguaseñas.com",
        password_hash=common_password, 
        role="teacher", 
        is_admin=True, 
        is_active=True,
        current_points=5000, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=180)
    )
    usuarios.append(admin1)
    
    admin2 = Users(
        first_name="Admin", 
        last_name="Inclusivo", 
        email="admin2@lenguaseñas.com",
        password_hash=common_password, 
        role="teacher", 
        is_admin=True, 
        is_active=True,
        current_points=3500, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=90)
    )
    usuarios.append(admin2)
    
    # 2 Profesores (Intérpretes)
    teacher1 = Users(
        first_name="María", 
        last_name="Sordomuda", 
        email="maria.sordomuda@example.com",
        password_hash=common_password, 
        role="teacher", 
        is_admin=False, 
        is_active=True,
        current_points=1200, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=60)
    )
    usuarios.append(teacher1)
    
    teacher2 = Users(
        first_name="Carlos", 
        last_name="Intérprete", 
        email="carlos.interprete@example.com",
        password_hash=common_password, 
        role="teacher", 
        is_admin=False, 
        is_active=True,
        current_points=950, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=45)
    )
    usuarios.append(teacher2)
    
    # 2 Estudiantes
    student1 = Users(
        first_name="Ana", 
        last_name="Aprende", 
        email="ana.aprende@example.com",
        password_hash=common_password, 
        role="student", 
        is_admin=False, 
        is_active=True,
        current_points=450, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=30)
    )
    usuarios.append(student1)
    
    student2 = Users(
        first_name="Miguel", 
        last_name="Silente", 
        email="miguel.silente@example.com",
        password_hash=common_password, 
        role="student", 
        is_admin=False, 
        is_active=True,
        current_points=220, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=15)
    )
    usuarios.append(student2)
    
    # 2 Usuarios Demo
    demo1 = Users(
        first_name="Pedro", 
        last_name="DemoSeñas", 
        email="pedro.demo@lenguaseñas.com",
        password_hash=common_password, 
        role="demo", 
        is_admin=False, 
        is_active=True,
        current_points=0, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=3),
        trial_end_date=datetime.now(timezone.utc) + timedelta(days=4)
    )
    usuarios.append(demo1)
    
    demo2 = Users(
        first_name="María", 
        last_name="DemoSeñas", 
        email="maria.demo@lenguaseñas.com",
        password_hash=common_password, 
        role="demo", 
        is_admin=False, 
        is_active=True,
        current_points=0, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=6),
        trial_end_date=datetime.now(timezone.utc) + timedelta(days=1)
    )
    usuarios.append(demo2)
    
    # 1 Usuario inactivo
    inactive_user = Users(
        first_name="Usuario", 
        last_name="InactivoSeñas", 
        email="deleted@lenguaseñas.com",
        password_hash=common_password, 
        role="student", 
        is_admin=False, 
        is_active=False,
        current_points=100, 
        registration_date=datetime.now(timezone.utc) - timedelta(days=100),
        deleted_at=datetime.now(timezone.utc) - timedelta(days=10),
        original_email="original@lenguaseñas.com", 
        deletion_uuid="abc12345"
    )
    usuarios.append(inactive_user)
    
    for user in usuarios:
        db.session.add(user)
    db.session.commit()
    print_success(f"{len(usuarios)} usuarios creados")
    
    admin_ids = [admin1.user_id, admin2.user_id]
    teacher_ids = [teacher1.user_id, teacher2.user_id]
    student_ids = [student1.user_id, student2.user_id]
    demo_ids = [demo1.user_id, demo2.user_id]
    
    # --- PASO 3: Cursos de Lengua de Señas ---
    print_info("Creando cursos de lengua de señas...")
    cursos = []
    
    # Curso 1: Nivel Básico (Profesor 1 - María Sordomuda)
    curso1 = Courses(
        title="Lengua de Señas Nivel Básico", 
        description="Aprende los fundamentos de la lengua de señas. Ideal para principiantes.",
        price=49.99, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=50),
        points=500, 
        created_by=teacher_ids[0]
    )
    cursos.append(curso1)
    
    # Curso 2: Nivel Intermedio (Profesor 1 - María Sordomuda)
    curso2 = Courses(
        title="Lengua de Señas Nivel Intermedio", 
        description="Amplía tu vocabulario y mejora tu fluidez en conversaciones cotidianas.",
        price=79.99, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=30),
        points=750, 
        created_by=teacher_ids[0]
    )
    cursos.append(curso2)
    
    # Curso 3: Nivel Avanzado (Profesor 1 - María Sordomuda)
    curso3 = Courses(
        title="Lengua de Señas Nivel Avanzado", 
        description="Domina estructuras complejas y expresiones idiomáticas en lengua de señas.",
        price=99.99, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=20),
        points=900, 
        created_by=teacher_ids[0]
    )
    cursos.append(curso3)
    
    # Curso 4: Vocabulario por Temas (Profesor 2 - Carlos Intérprete)
    curso4 = Courses(
        title="Vocabulario de Señas: Familia y Hogar", 
        description="Aprende señas relacionadas con la familia, el hogar y la vida diaria.",
        price=39.99, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=40),
        points=400, 
        created_by=teacher_ids[1]
    )
    cursos.append(curso4)
    
    # Curso 5: Vocabulario Profesional (Profesor 2 - Carlos Intérprete)
    curso5 = Courses(
        title="Lengua de Señas para el Trabajo", 
        description="Vocabulario profesional para entornos laborales y entrevistas.",
        price=59.99, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=25),
        points=550, 
        created_by=teacher_ids[1]
    )
    cursos.append(curso5)
    
    # Curso 6: Curso Gratuito Básico (Profesor 2 - Carlos Intérprete)
    curso_gratis = Courses(
        title="Introducción a la Lengua de Señas", 
        description="Curso gratuito para conocer el alfabeto manual y saludos básicos.",
        price=0.00, 
        is_active=True, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=60),
        points=300, 
        created_by=teacher_ids[1]
    )
    cursos.append(curso_gratis)
    
    # Curso inactivo
    curso_inactivo = Courses(
        title="Curso Antiguo de Señas (Descontinuado)", 
        description="Versión anterior del curso, ya no está disponible.",
        price=29.99, 
        is_active=False, 
        creation_date=datetime.now(timezone.utc) - timedelta(days=200),
        points=200, 
        created_by=teacher_ids[0]
    )
    cursos.append(curso_inactivo)
    
    for curso in cursos:
        db.session.add(curso)
    db.session.commit()
    print_success(f"{len(cursos)} cursos creados")
    
    # --- PASO 4: Módulos ---
    print_info("Creando módulos de lengua de señas...")
    modulos = []
    
    def crear_modulos_para_curso(curso_id, titulos, puntos=None):
        if puntos is None:
            puntos = [100] * len(titulos)
        for i, titulo in enumerate(titulos, 1):
            modulos.append(Modules(
                title=titulo, 
                order=i, 
                points=puntos[min(i-1, len(puntos)-1)],
                is_active=True, 
                course_id=curso_id
            ))
    
    # Módulos para Curso Básico
    crear_modulos_para_curso(curso1.course_id,
        ["Alfabeto Manual", "Saludos y Presentaciones", "Números y Colores", "Familia", "Emociones", "Preguntas Básicas"],
        [50, 75, 100, 125, 150, 200])
    
    # Módulos para Curso Intermedio
    crear_modulos_para_curso(curso2.course_id,
        ["Verbos Comunes", "Tiempos Verbales", "Descripciones", "Alimentos y Bebidas", "Ropa y Accesorios", "Lugares y Direcciones"],
        [80, 100, 120, 150, 180, 200])
    
    # Módulos para Curso Avanzado
    crear_modulos_para_curso(curso3.course_id,
        ["Expresiones Idiomáticas", "Conversaciones Complejas", "Narrativa en Señas", "Interpretación Simultánea", "Matices Culturales", "Ética del Intérprete"],
        [100, 120, 150, 180, 200, 220])
    
    # Módulos para Vocabulario: Familia
    crear_modulos_para_curso(curso4.course_id,
        ["Miembros de la Familia", "Actividades del Hogar", "Mascotas", "Celebraciones", "Rutinas Diarias"], 
        [50, 60, 70, 80, 90])
    
    # Módulos para Vocabulario Profesional
    crear_modulos_para_curso(curso5.course_id,
        ["Entrevistas Laborales", "Reuniones de Trabajo", "Vocabulario Técnico", "Atención al Cliente", "Presentaciones"], 
        [60, 80, 100, 100, 120])
    
    # Módulos para Curso Gratuito
    crear_modulos_para_curso(curso_gratis.course_id,
        ["Alfabeto Manual Básico", "Saludos Esenciales", "Presentación Personal"], 
        [50, 75, 100])
    
    for modulo in modulos:
        db.session.add(modulo)
    db.session.commit()
    print_success(f"{len(modulos)} módulos creados")
    
    # --- PASO 5: Lecciones de Señas ---
    print_info("Creando lecciones con vocabulario de señas...")
    lecciones = []
    
    def crear_lecciones_para_modulo(module_id, titulos_lecciones, senas_dict, trial_visible=False):
        for i, (titulo, senas) in enumerate(zip(titulos_lecciones, senas_dict), 1):
            # Crear un signs_taught ÚNICO
            signs = f"M{module_id}_L{i}: {senas}"
            
            lecciones.append(Lessons(
                title=titulo,
                content=f"Aprende las siguientes señas: {senas}. Cada seña incluye descripción detallada del movimiento de manos, expresión facial y contexto de uso.",
                learning_objective=f"Al finalizar esta lección, podrás realizar correctamente las señas de {titulo}.",
                signs_taught=signs,
                order=i, 
                trial_visible=trial_visible and i <= 2,
                is_active=True, 
                module_id=module_id
            ))
    
    # Diccionarios de lecciones por módulo
    modulos_por_curso = {}
    for m in modulos:
        modulos_por_curso.setdefault(m.course_id, []).append(m)
    
    # Lecciones para Curso Básico - Módulo 1: Alfabeto Manual
    modulo_alfabeto = next(m for m in modulos if m.title == "Alfabeto Manual")
    titulos_alfabeto = ["Vocales A-E-I-O-U", "Consonantes B,C,D,F,G", "Consonantes H,J,K,L,M", "Consonantes N,Ñ,P,Q,R", "Consonantes S,T,V,W,X,Y,Z", "Señas con Dos Manos"]
    senas_alfabeto = ["A, E, I, O, U", "B, C, D, F, G", "H, J, K, L, M", "N, Ñ, P, Q, R", "S, T, V, W, X, Y, Z", "CH, LL, RR"]
    crear_lecciones_para_modulo(modulo_alfabeto.module_id, titulos_alfabeto, senas_alfabeto, trial_visible=True)
    
    # Lecciones para Curso Básico - Módulo 2: Saludos
    modulo_saludos = next(m for m in modulos if m.title == "Saludos y Presentaciones")
    titulos_saludos = ["Saludos Básicos", "Presentarse", "Preguntar cómo está alguien", "Despedidas", "Cortesía: Por favor y Gracias", "Frases de cortesía"]
    senas_saludos = ["Hola, Buenos días, Buenas tardes", "Me llamo, Mi nombre es, Soy", "¿Cómo estás?, ¿Qué tal?", "Adiós, Hasta luego, Nos vemos", "Por favor, Gracias, De nada", "Permiso, Lo siento, Salud"]
    crear_lecciones_para_modulo(modulo_saludos.module_id, titulos_saludos, senas_saludos, trial_visible=True)
    
    # Lecciones para Curso Básico - Módulo 3: Números y Colores
    modulo_numeros = next(m for m in modulos if m.title == "Números y Colores")
    titulos_numeros = ["Números del 0 al 10", "Números del 11 al 20", "Decenas y Centenas", "Colores Primarios", "Colores Secundarios", "Describir objetos con color y número"]
    senas_numeros = ["0,1,2,3,4,5,6,7,8,9,10", "11,12,13,14,15,16,17,18,19,20", "30,40,50,60,70,80,90,100", "Rojo, Azul, Amarillo", "Verde, Naranja, Morado, Rosa", "Grande/Pequeño, Claro/Oscuro"]
    crear_lecciones_para_modulo(modulo_numeros.module_id, titulos_numeros, senas_numeros, trial_visible=True)
    
    # Lecciones para Curso Intermedio - Verbos
    modulo_verbos = next(m for m in modulos if m.title == "Verbos Comunes")
    titulos_verbos = ["Verbos de Movimiento", "Verbos de Comunicación", "Verbos Cotidianos", "Verbos de Emoción", "Verbos de Percepción", "Verbos Modales"]
    senas_verbos = ["Ir, Venir, Llegar, Salir", "Hablar, Preguntar, Responder, Explicar", "Comer, Beber, Dormir, Trabajar", "Amar, Gustar, Querer, Sentir", "Ver, Oír, Sentir, Saber", "Poder, Deber, Querer, Necesitar"]
    crear_lecciones_para_modulo(modulo_verbos.module_id, titulos_verbos, senas_verbos, trial_visible=True)
    
    # Lecciones para Curso Gratuito
    modulo_gratis = next(m for m in modulos if m.title == "Alfabeto Manual Básico")
    titulos_gratis = ["Vocales", "Consonantes básicas", "Tu nombre en señas"]
    senas_gratis = ["A, E, I, O, U", "M, P, T, L, S", "Practica deletrear tu nombre"]
    crear_lecciones_para_modulo(modulo_gratis.module_id, titulos_gratis, senas_gratis, trial_visible=True)
    
    # Continuar con más lecciones para otros módulos...
    # (Por brevedad, incluyo solo ejemplos representativos)
    
    for leccion in lecciones:
        db.session.add(leccion)
    db.session.commit()
    print_success(f"{len(lecciones)} lecciones creadas")
    
    # --- PASO 6: Recursos Multimedia (Videos de Señass) ---
    print_info("Creando recursos multimedia de señas...")
    recursos = []
    
    # URLs de ejemplo (en producción, serían URLs reales de Cloudinary)
    urls_videos = [
        "https://res.cloudinary.com/ejemplo/videos/senas/alfabeto.mp4",
        "https://res.cloudinary.com/ejemplo/videos/senas/saludos.mp4",
        "https://res.cloudinary.com/ejemplo/videos/senas/numeros.mp4",
        "https://res.cloudinary.com/ejemplo/videos/senas/colores.mp4",
        "https://res.cloudinary.com/ejemplo/videos/senas/familia.mp4",
        "https://res.cloudinary.com/ejemplo/videos/senas/verbos.mp4"
    ]
    
    urls_imagenes = [
        "https://res.cloudinary.com/ejemplo/imagenes/senas/diagrama-alfabeto.jpg",
        "https://res.cloudinary.com/ejemplo/imagenes/senas/posicion-manos.jpg",
        "https://res.cloudinary.com/ejemplo/imagenes/senas/expresiones-faciales.jpg"
    ]
    
    urls_gifs = [
        "https://res.cloudinary.com/ejemplo/gifs/senas/movimiento-letra-a.gif",
        "https://res.cloudinary.com/ejemplo/gifs/senas/movimiento-hola.gif",
        "https://res.cloudinary.com/ejemplo/gifs/senas/movimiento-gracias.gif"
    ]
    
    for leccion in random.sample(lecciones, min(20, len(lecciones))):
        # Cada lección tiene al menos un video demostrativo
        recursos.append(MultimediaResources(
            lesson_id=leccion.lesson_id,
            resource_type='video',
            url=random.choice(urls_videos),
            duration_seconds=random.choice([60, 90, 120, 180]),
            description=f"Video demostrativo: {leccion.title}",
            order=1
        ))
        
        # Algunas lecciones tienen imágenes explicativas
        if random.random() > 0.5:
            recursos.append(MultimediaResources(
                lesson_id=leccion.lesson_id,
                resource_type='image',
                url=random.choice(urls_imagenes),
                duration_seconds=None,
                description=f"Diagrama: {leccion.title}",
                order=2
            ))
        
        # Lecciones de alfabeto tienen GIFs animados
        if "Alfabeto" in leccion.title or "Vocales" in leccion.title:
            recursos.append(MultimediaResources(
                lesson_id=leccion.lesson_id,
                resource_type='gif',
                url=random.choice(urls_gifs),
                duration_seconds=None,
                description=f"Animación: movimiento de manos",
                order=3
            ))
    
    for recurso in recursos:
        db.session.add(recurso)
    db.session.commit()
    print_success(f"{len(recursos)} recursos multimedia creados")
    
    # --- PASO 7: Compras ---
    print_info("Creando compras de cursos...")
    compras = []
    
    # Ana compra Curso Básico
    compras.append(Purchases(
        purchase_date=datetime.now(timezone.utc)-timedelta(days=25),
        price=curso1.price, 
        total=curso1.price, 
        status='paid',
        start_date=datetime.now(timezone.utc)-timedelta(days=25),
        course_id=curso1.course_id, 
        user_id=student_ids[0]
    ))
    
    # Ana también compra el curso gratuito
    compras.append(Purchases(
        purchase_date=datetime.now(timezone.utc)-timedelta(days=10),
        price=0, 
        total=0, 
        status='paid',
        start_date=datetime.now(timezone.utc)-timedelta(days=10),
        course_id=curso_gratis.course_id, 
        user_id=student_ids[0]
    ))
    
    # Miguel compra Curso de Vocabulario: Familia
    compras.append(Purchases(
        purchase_date=datetime.now(timezone.utc)-timedelta(days=5),
        price=curso4.price, 
        total=curso4.price, 
        status='paid',
        start_date=datetime.now(timezone.utc)-timedelta(days=5),
        course_id=curso4.course_id, 
        user_id=student_ids[1]
    ))
    
    # Compra pendiente (para pruebas)
    compras.append(Purchases(
        purchase_date=datetime.now(timezone.utc)-timedelta(hours=2),
        price=curso2.price, 
        total=curso2.price, 
        status='pending', 
        start_date=None,
        course_id=curso2.course_id, 
        user_id=student_ids[0],
        stripe_payment_intent_id="pi_test_pending_123456"
    ))
    
    for compra in compras:
        db.session.add(compra)
    db.session.commit()
    print_success(f"{len(compras)} compras creadas")
    
    # --- PASO 8: Puntos de Usuario ---
    print_info("Creando historial de puntos por aprendizaje...")
    puntos = []
    
    # Ana ha completado lecciones de señas
    for leccion in random.sample(lecciones, 10):
        puntos.append(UserPoints(
            user_id=student_ids[0], 
            points=random.choice([10,15,20]),
            point_type='lesson', 
            event_description=f"Aprendió: {leccion.title[:50]}",
            date=datetime.now(timezone.utc)-timedelta(days=random.randint(1,20))
        ))
    
    # Miguel ha completado menos lecciones
    for leccion in random.sample(lecciones, 6):
        puntos.append(UserPoints(
            user_id=student_ids[1], 
            points=random.choice([10,15]),
            point_type='lesson', 
            event_description=f"Aprendió: {leccion.title[:50]}",
            date=datetime.now(timezone.utc)-timedelta(days=random.randint(1,10))
        ))
    
    # Profesores ganan puntos por crear cursos
    puntos.append(UserPoints(
        user_id=teacher_ids[0], 
        points=500, 
        point_type='course',
        event_description="Creación: Curso Básico de Señas",
        date=datetime.now(timezone.utc)-timedelta(days=50)
    ))
    
    puntos.append(UserPoints(
        user_id=teacher_ids[1], 
        points=400, 
        point_type='course',
        event_description="Creación: Vocabulario Familia",
        date=datetime.now(timezone.utc)-timedelta(days=40)
    ))
    
    for punto in puntos:
        db.session.add(punto)
    db.session.commit()
    
    # Actualizar puntos totales
    for uid in student_ids + teacher_ids:
        total = db.session.query(db.func.sum(UserPoints.points)).filter(UserPoints.user_id == uid).scalar() or 0
        Users.query.get(uid).current_points = total
    db.session.commit()
    print_success(f"{len(puntos)} puntos creados")
    
    # --- PASO 9: Progreso de Usuarios ---
    print_info("Creando progreso de aprendizaje...")
    progresos = []
    
    # Ana ha progresado en Curso Básico
    lecciones_curso1 = [l for l in lecciones if l.module_id in [m.module_id for m in modulos_por_curso[curso1.course_id]]]
    for i, leccion in enumerate(lecciones_curso1[:12]):
        completada = i < 10  # 10 completadas, 2 en progreso
        progresos.append(UserProgress(
            user_id=student_ids[0], 
            lesson_id=leccion.lesson_id, 
            completed=completada,
            start_date=datetime.now(timezone.utc)-timedelta(days=24-i),
            completion_date=datetime.now(timezone.utc)-timedelta(days=20-i) if completada else None
        ))
    
    # Miguel ha progresado en Vocabulario Familia
    lecciones_curso4 = [l for l in lecciones if l.module_id in [m.module_id for m in modulos_por_curso[curso4.course_id]]]
    for i, leccion in enumerate(lecciones_curso4[:8]):
        completada = i < 6  # 6 completadas, 2 en progreso
        progresos.append(UserProgress(
            user_id=student_ids[1], 
            lesson_id=leccion.lesson_id, 
            completed=completada,
            start_date=datetime.now(timezone.utc)-timedelta(days=10-i),
            completion_date=datetime.now(timezone.utc)-timedelta(days=8-i) if completada else None
        ))
    
    for prog in progresos:
        db.session.add(prog)
    db.session.commit()
    print_success(f"{len(progresos)} progresos creados")
    
    # --- PASO 10: Logros adaptados a lengua de señas ---
    print_info("Creando logros para estudiantes de señas...")
    logros = []
    datos_logros = [
        ("Primeras Señas", "Completa tu primera lección de lengua de señas", 10, "🖐️"),
        ("Deletreo Experto", "Domina el alfabeto manual completo", 100, "🔤"),
        ("Saludador Profesional", "Aprende todos los saludos básicos", 50, "👋"),
        ("Vocabulario Familiar", "Completa el módulo de familia", 150, "👪"),
        ("Intérprete en Progreso", "Completa 20 lecciones", 200, "📹"),
        ("Conversador Fluido", "Completa el nivel intermedio", 400, "💬"),
        ("Profesor de Señas", "Crea un curso con más de 10 estudiantes", 500, "👨‍🏫"),
        ("Explorador Cultural", "Aprende sobre la cultura sorda", 100, "🌍"),
        ("Comunicador Inclusivo", "Completa 50 lecciones", 500, "🤝"),
        ("Maestro Intérprete", "Domina todos los niveles", 1000, "🏆")
    ]
    
    for nombre, desc, pts, icono in datos_logros:
        logros.append(Achievements(
            name=nombre, 
            description=desc, 
            required_points=pts, 
            icon=icono
        ))
    
    for logro in logros:
        db.session.add(logro)
    db.session.commit()
    print_success(f"{len(logros)} logros creados")
    
    # --- PASO 11: Asignar Logros a Usuarios ---
    print_info("Asignando logros a usuarios...")
    asignaciones = []
    
    # Buscar logros por nombre
    logro_primeras = next(l for l in logros if l.name == "Primeras Señas")
    logro_deletreo = next(l for l in logros if l.name == "Deletreo Experto")
    logro_saludos = next(l for l in logros if l.name == "Saludador Profesional")
    logro_profesor = next(l for l in logros if l.name == "Profesor de Señas")
    
    # Ana tiene varios logros
    asignaciones.extend([
        UserAchievements(
            user_id=student_ids[0], 
            achievement_id=logro_primeras.achievement_id,
            obtained_date=datetime.now(timezone.utc)-timedelta(days=24)
        ),
        UserAchievements(
            user_id=student_ids[0], 
            achievement_id=logro_deletreo.achievement_id,
            obtained_date=datetime.now(timezone.utc)-timedelta(days=15)
        ),
        UserAchievements(
            user_id=student_ids[0], 
            achievement_id=logro_saludos.achievement_id,
            obtained_date=datetime.now(timezone.utc)-timedelta(days=20)
        )
    ])
    
    # Miguel tiene el logro de primeras señas
    asignaciones.append(UserAchievements(
        user_id=student_ids[1], 
        achievement_id=logro_primeras.achievement_id,
        obtained_date=datetime.now(timezone.utc)-timedelta(days=8)
    ))
    
    # Profesora María tiene logro de profesor
    asignaciones.append(UserAchievements(
        user_id=teacher_ids[0], 
        achievement_id=logro_profesor.achievement_id,
        obtained_date=datetime.now(timezone.utc)-timedelta(days=30)
    ))
    
    for asig in asignaciones:
        db.session.add(asig)
    db.session.commit()
    print_success(f"{len(asignaciones)} logros asignados")
    
    # --- FINAL ---
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ SEMILLA DE LENGUA DE SEÑAS COMPLETADA{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    print(f"{Colors.BLUE}📊 Resumen:{Colors.END}")
    print(f"   - {len(cursos)} cursos")
    print(f"   - {len(modulos)} módulos")
    print(f"   - {len(lecciones)} lecciones")
    print(f"   - {len(recursos)} recursos multimedia")
    print(f"   - {len(logros)} logros disponibles")

# ============================================
# EJECUTAR LA SEMILLA
# ============================================
if __name__ == "__main__":
    with app.app_context():
        run_seed()