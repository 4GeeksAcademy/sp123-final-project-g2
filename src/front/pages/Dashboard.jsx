import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Link } from "react-router-dom";

export const Dashboard = () => {
  const { store, dispatch } = useGlobalReducer();

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver el dashboard</h4>
      </div>
    );
  }

  const user = store.current_user || {};

  const planRaw = user.plan || user.subscription || user.membership || "FREE";
  const plan = String(planRaw).toUpperCase();

  const role = String(user.role || "student").toLowerCase().trim();
  const isAdmin = role === "admin";
  const isTeacher = role === "teacher" || role === "tacher";
  const isDemo = role === "demo";
  const isStudent = !isAdmin && !isTeacher && !isDemo;

  const myProgress = Array.isArray(store.my_progress) ? store.my_progress : [];
  const completedCourses = myProgress.filter(p => p?.completed === true).length;
  const totalCourses = myProgress.length;
  const progressPct = totalCourses > 0 ? Math.round((completedCourses / totalCourses) * 100) : 0;

  const achievementsCount = Array.isArray(store.achievements) ? store.achievements.length : 0;

  // ================= DEMO =================
  if (isDemo) {
    return (
      <div className="container mt-4">
        <div className="p-5 mb-4 rounded-4 demo-hero text-center">
          <i className="bi bi-stars display-4 text-primary"></i>
          <h1 className="fw-bold mt-3">Estás en modo Demo</h1>
          <p className="text-muted">Explora la plataforma antes de registrarte</p>
          <Link to="/register" className="btn btn-primary btn-lg mt-2">
            <i className="bi bi-person-plus-fill me-2"></i> Crear cuenta
          </Link>
        </div>

        <div className="row g-4">
          <DemoCard icon="bi-collection-play" title="Explorar cursos" to="/courses-card" />
          <DemoCard icon="bi-credit-card" title="Ver planes" to="/planes" />
          <DemoCard icon="bi-info-circle" title="Cómo funciona" to="/about" />
          <DemoCard
            icon="bi-chat-dots"
            title="Contacto"
            onClick={() => dispatch({ type: "open_contact" })}
          />
        </div>
      </div>
    );
  }

  // ================= NORMAL =================
  return (
    <div className="container mt-4">
      {/* HERO */}
      <div className="dashboard-hero mb-4">
        <div>
          <h2 className="fw-bold mb-1">
            <i className="bi bi-mortarboard-fill me-2"></i>
            Hola {user.first_name || "usuario"}
          </h2>
          <div className="text-muted">Bienvenido a tu panel</div>
        </div>

        <div className="text-end">
          <div className="badge bg-primary fs-6 p-2">
            <i className="bi bi-star-fill me-1"></i> {plan}
          </div>
          <div className="small text-muted mt-1">
            <i className="bi bi-lightning-charge-fill text-warning"></i> {user.current_points || 0} pts
          </div>
        </div>
      </div>

      {/* CARDS */}
      <div className="row g-4">
        <DashCard icon="bi-credit-card" title="Suscripción" value={plan} to="/suscripciones" />

        {!isTeacher && (
          <DashCard
            icon="bi-mortarboard"
            title="Cursos completados"
            value={`${completedCourses}/${totalCourses}`}
            to="/my-progress"
          />
        )}

        {!isTeacher && (
          <DashCard
            icon="bi-graph-up"
            title="Progreso"
            value={`${progressPct}%`}
            to="/my-progress"
          />
        )}

        <DashCard icon="bi-trophy" title="Logros" value={achievementsCount} to="/achievements" />

        {isTeacher && (
          <DashCard
            icon="bi-cloud-arrow-up"
            title="Subir vídeos"
            value="Gestionar contenido"
            to="/upload-videos"
            highlight
          />
        )}

        {isAdmin && (
          <DashCard icon="bi-gear" title="Panel admin" value="Administrar plataforma" to="/admin" highlight />
        )}

        {isStudent && (
          <DashCard icon="bi-people" title="Explorar cursos" value="Explorar catálogo" to="/courses" />
        )}

        {isTeacher && (
          <DashCard icon="bi-people" title="Explorar tus cursos" value="Explorar catálogo" to="/courses" />
        )}
      </div>
    </div>
  );
};

// ---------- COMPONENTES ----------
const DashCard = ({ icon, title, value, to, highlight }) => (
  <div className="col-12 col-md-6">
    <Link to={to} className="text-decoration-none">
      <div className={`card dash-card h-100 ${highlight ? "dash-highlight" : ""}`}>
        <div className="card-body d-flex justify-content-between align-items-center">
          <div>
            <div className="text-muted small">{title}</div>
            <div className="fs-4 fw-bold">{value}</div>
          </div>
          <i className={`bi ${icon} dash-card-icon`}></i>
        </div>
      </div>
    </Link>
  </div>
);

const DemoCard = ({ icon, title, to, onClick }) => (
  <div className="col-12 col-md-6">
    {onClick ? (
      <div
        className="text-decoration-none"
        onClick={onClick}
        style={{ cursor: "pointer" }}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " " ? onClick() : null)}
      >
        <div className="card dash-card h-100 text-center p-4">
          <i className={`bi ${icon} display-5 text-primary`}></i>
          <h5 className="mt-3">{title}</h5>
        </div>
      </div>
    ) : (
      <Link to={to} className="text-decoration-none">
        <div className="card dash-card h-100 text-center p-4">
          <i className={`bi ${icon} display-5 text-primary`}></i>
          <h5 className="mt-3">{title}</h5>
        </div>
      </Link>
    )}
  </div>
);
