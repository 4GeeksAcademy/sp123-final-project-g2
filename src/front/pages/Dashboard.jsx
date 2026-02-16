import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Link } from "react-router-dom";

export const Dashboard = () => {
  const { store } = useGlobalReducer();

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver el dashboard</h4>
      </div>
    );
  }

  // ===================== DATA =====================
  const user = store.current_user || {};

  const userEmail =
    user.email || user.username || user.user_email || store.email || "Sin email";

  const planRaw = user.plan || user.subscription || user.membership || "FREE";
  const plan = String(planRaw).toUpperCase();

  const achievementsCount = Array.isArray(store.achievements)
    ? store.achievements.length
    : 0;

  const myProgress = Array.isArray(store.my_progress) ? store.my_progress : [];

  const completedCourses = myProgress.filter(
    (p) => p?.status === "completed" || p?.completed === true
  ).length;

  const totalCourses =
    (Array.isArray(store.courses) && store.courses.length) ||
    (Array.isArray(store.all_courses) && store.all_courses.length) ||
    myProgress.length ||
    0;

  const progressPct =
    totalCourses > 0 ? Math.round((completedCourses / totalCourses) * 100) : 0;

  const planBadgeClass =
    plan.includes("PREMIUM")
      ? "badge-premium"
      : plan.includes("PRO")
      ? "badge-pro"
      : "badge-free";

  return (
    <div className="container mt-4">

      {/* HERO */}
      <div className="p-4 mb-4 rounded shadow-sm bg-light d-flex justify-content-between align-items-center flex-wrap">
        <div>
          <h1 className="fw-bold mb-1">
            <i className="bi bi-mortarboard-fill text-primary me-2"></i>
            ¡Bienvenidx, {user.first_name}!
          </h1>
          <p className="text-muted mb-0">
            Continúa tu aprendizaje donde lo dejaste
          </p>
        </div>
      </div>

      {/* DATOS USUARIO */}
      <div className="card shadow-sm mb-4">
        <div className="card-body d-flex justify-content-between align-items-center flex-wrap">

          <div>
            <h5 className="mb-3">
              <i className="bi bi-person-circle me-2 text-primary"></i>
              Datos de usuario
            </h5>

            <p className="mb-1">
              <i className="bi bi-envelope-fill me-2 text-secondary"></i>
              {userEmail}
            </p>

            <p className="mb-0">
              <i className="bi bi-shield-check me-2 text-secondary"></i>
              {user.role || "student"}
            </p>
          </div>

          <div className="text-end">
            <span className={`badge ${planBadgeClass} p-2`}>
              <i className="bi bi-star-fill me-1"></i>
              Plan {plan}
            </span>

            <div className="mt-2">
              <i className="bi bi-lightning-charge-fill text-warning me-1"></i>
              <strong>{user.current_points}</strong> puntos
            </div>
          </div>

        </div>
      </div>

      {/* CARDS */}
      <div className="row g-4">

        {/* PLAN */}
        <div className="col-12 col-md-6">
          <Link to="/suscripciones" className="text-decoration-none">
            <div className="card shadow-sm h-100 text-center p-4">
              <i className="bi bi-star-fill fs-1 text-primary"></i>
              <h5 className="mt-3">Plan seleccionado</h5>
              <h2 className="fw-bold text-primary">{plan}</h2>
              <p className="text-muted mb-0">Gestionar suscripción</p>
            </div>
          </Link>
        </div>

        {/* CURSOS */}
        <div className="col-12 col-md-6">
          <Link to="/my-progress" className="text-decoration-none">
            <div className="card shadow-sm h-100 text-center p-4">
              <i className="bi bi-mortarboard-fill fs-1 text-primary"></i>
              <h5 className="mt-3">Cursos completados</h5>
              <h2 className="fw-bold text-primary">
                {completedCourses}
                {totalCourses > 0 && (
                  <span className="fs-5 text-muted"> / {totalCourses}</span>
                )}
              </h2>
              <p className="text-muted mb-0">Ver progreso</p>
            </div>
          </Link>
        </div>

        {/* PROGRESO */}
        <div className="col-12 col-md-6">
          <Link to="/my-progress" className="text-decoration-none">
            <div className="card shadow-sm h-100 text-center p-4">
              <i className="bi bi-graph-up-arrow fs-1 text-primary"></i>
              <h5 className="mt-3">Progreso general</h5>
              <h2 className="fw-bold text-primary">{progressPct}%</h2>

              <div className="progress mt-3">
                <div
                  className="progress-bar bg-primary"
                  role="progressbar"
                  style={{ width: `${progressPct}%` }}
                ></div>
              </div>

              <p className="text-muted mt-2 mb-0">Ir a tu progreso</p>
            </div>
          </Link>
        </div>

        {/* LOGROS */}
        <div className="col-12 col-md-6">
          <Link to="/achievements" className="text-decoration-none">
            <div className="card shadow-sm h-100 text-center p-4">
              <i className="bi bi-trophy-fill fs-1 text-primary"></i>
              <h5 className="mt-3">Logros conseguidos</h5>
              <h2 className="fw-bold text-primary">{achievementsCount}</h2>
              <p className="text-muted mb-0">Ver tus logros</p>
            </div>
          </Link>
        </div>

      </div>
    </div>
  );
};
