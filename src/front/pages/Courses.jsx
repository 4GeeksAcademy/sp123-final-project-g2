import { useEffect, useMemo, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";
import { Link } from "react-router-dom";
 
 
const apiFetchJson = (url, options) => {
  return fetch(url, options).then((res) =>
    res
      .json()
      .catch(() => null)
      .then((data) => ({ ok: res.ok, status: res.status, data }))
  );
};
 
// Acepta: array directamente, o { courses: [...] }, o { data: [...] }
const normalizeCourses = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.courses)) return payload.courses;
  if (payload && Array.isArray(payload.data)) return payload.data;
  return [];
};
 
const formatDate = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? "—" : d.toLocaleDateString();
};
 
const formatPrice = (n) => {
  const num = Number(n);
  if (Number.isNaN(num)) return "—";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(num);
};
 
export const Courses = () => {
  const { store } = useGlobalReducer();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
 
  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver el dashboard</h4>
      </div>
    );
  }
 
  const user = store.current_user || {};
  const role = String(user.role || "student").toLowerCase().trim();
  const isAdmin = role === "admin";
  const isTeacher = role === "teacher" || role === "tacher";
  // Evita dobles // al concatenar
  const base = (import.meta.env.VITE_BACKEND_URL || "").replace(/\/$/, "");
  const endpoint = `${base}/api/courses-private`;
 
  const loadCourses = () => {
    setLoading(true);
    setErrorMsg("");
 
    apiFetchJson(endpoint, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`,
      },
    })
      .then(({ ok, status, data }) => {
        // Logs útiles para detectar 403/401/ruta mal, etc.
        console.log("GET", endpoint, "->", status);
        console.log("Response data:", data);
        if (!ok) {
          setCourses([]);
 
          // Mensajes típicos para 401/403
          if (status === 401 || status === 422) {
            setErrorMsg("Token inválido o expirado. Vuelve a iniciar sesión.");
            return;
          }
          if (status === 403) {
            setErrorMsg(
              data?.msg ||
              "Acceso denegado (403). Revisa CORS/permisos del backend para este endpoint."
            );
            return;
          }
 
          setErrorMsg(data?.msg || "Error cargando cursos.");
          return;
        }
        if (data?.count === 0) {
          setCourses([]);
          setErrorMsg("No se encontraron cursos para este usuario.");
          return;
        }
        setCourses(normalizeCourses(data.results));
      })
      .catch(() => {
        setCourses([]);
        setErrorMsg("No se pudo conectar con el servidor.");
      })
      .finally(() => setLoading(false));
  };
 
  useEffect(() => {
    if (store.isLogged && store.token) loadCourses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [store.isLogged, store.token]);
 
  const subtitle = useMemo(() => {
    if (loading) return "Cargando…";
    if (errorMsg) return "No se pudieron cargar los cursos";
    return courses.length === 1 ? "1 curso" : `${courses.length} cursos`;
  }, [loading, errorMsg, courses.length]);
 
  if (!store.isLogged) {
    return (
      <div className="container py-5 text-center">
        <i className="bi bi-lock fs-1"></i>
        <h4 className="mt-3">Debes iniciar sesión para ver tus cursos</h4>
        <p className="text-secondary mb-0">Inicia sesión y vuelve a esta sección.</p>
      </div>
    );
  }
 
  return (
    <div className="container py-4">
      {/* Header */}
      <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mb-4">
        <div>
          <h1 className="h3 mb-1">
            <i className="bi bi-journal-bookmark-fill me-2"></i>
            Mis Cursos
          </h1>
          <div className="text-secondary">{subtitle}</div>
        </div>
 
        <button className="btn btn-outline-secondary" onClick={loadCourses} disabled={loading}>
          <i className="bi bi-arrow-clockwise me-2"></i>
          Recargar
        </button>
      </div>
 
      {/* Error */}
      {errorMsg && (
        <div className="alert alert-danger d-flex align-items-start" role="alert">
          <i className="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
          <div>
            <div className="fw-semibold">Ocurrió un problema</div>
            <div className="mb-2">{errorMsg}</div>
            <div className="small text-muted">
              Tip: abre <b>Network</b> y mira si el 403 es en <b>OPTIONS</b> (CORS) o en <b>GET</b> (permisos/JWT).
            </div>
          </div>
        </div>
      )}
 
      {/* Loading */}
      {loading && (
        <div className="d-flex justify-content-center py-5">
          <div className="text-center">
            <div className="spinner-border" role="status" aria-label="loading"></div>
            <div className="text-secondary mt-3">Cargando cursos…</div>
          </div>
        </div>
      )}
 
      {/* Empty */}
      {!loading && !errorMsg && courses.length === 0 && (
        <div className="text-center py-5 border rounded-4 bg-light">
          <i className="bi bi-inbox fs-1"></i>
          <h5 className="mt-3 mb-1">No hay cursos para mostrar</h5>
          <p className="text-secondary mb-0">Si existen en la BD, revisa permisos/CORS del endpoint.</p>
        </div>
      )}
 
      {/* Cards */}
{!loading && !errorMsg && courses.length > 0 && (
  <div className="row g-4 justify-content-center">
    {courses.map((course) => {
      const isActive = !!course.is_active;

      return (
        <div key={course.course_id} className="col-12 col-md-6 col-xl-5">
          <div
            className="card h-100 border-0 rounded-4 shadow-sm overflow-hidden"
            style={{
              minHeight: 360,
              background: "#ffffff",
              transition: "all .25s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-6px)";
              e.currentTarget.style.boxShadow = "0 20px 50px rgba(0,0,0,.12)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0px)";
              e.currentTarget.style.boxShadow = "";
            }}
          >
            {/* Barra superior */}
            <div
              style={{
                height: 8,
                background: isActive
                  ? "linear-gradient(90deg,#198754,#20c997)"
                  : "linear-gradient(90deg,#6c757d,#adb5bd)",
              }}
            />

            <div className="card-body d-flex flex-column p-4 pt-4">

              {/* HEADER */}
              <div className="d-flex justify-content-between align-items-start mb-3">

                <div className="d-flex align-items-center gap-3 min-w-0">
                  <div
                    className="rounded-4 d-flex align-items-center justify-content-center flex-shrink-0"
                    style={{
                      width: 56,
                      height: 56,
                      background:
                        "linear-gradient(135deg, rgba(13,110,253,.18), rgba(111,66,193,.18))",
                      border: "1px solid rgba(13,110,253,.15)",
                    }}
                  >
                    <i className="bi bi-mortarboard-fill fs-4"></i>
                  </div>

                  <div className="min-w-0">
                    <h5 className="fw-semibold mb-1 text-truncate" title={course.title}>
                      {course.title}
                    </h5>
                    <small className="text-secondary">
                      <i className="bi bi-hash me-1"></i>
                      {course.course_id}
                    </small>
                  </div>
                </div>

                {/* BADGE CORREGIDO */}
                <div className="ps-2">
                  <span
                    className={`badge ${
                      isActive ? "bg-success" : "bg-secondary"
                    }`}
                    style={{
                      borderRadius: 999,
                      padding: ".6rem .9rem",
                      fontSize: ".85rem",
                      whiteSpace: "nowrap",
                    }}
                  >
                    <i
                      className={`bi ${
                        isActive ? "bi-check-circle-fill" : "bi-pause-circle-fill"
                      } me-1`}
                    ></i>
                    {isActive ? "Activo" : "Inactivo"}
                  </span>
                </div>
              </div>

              {/* DESCRIPCIÓN */}
              <p className="text-secondary mb-3" style={{ minHeight: 70 }}>
                {course.description?.trim()
                  ? course.description
                  : "Sin descripción."}
              </p>

              {/* INFO CHIPS */}
              <div className="d-flex flex-wrap gap-2 mb-4">
                <span className="badge rounded-pill px-3 py-2 text-primary bg-primary-subtle fw-semibold">
                  <i className="bi bi-cash-coin me-1"></i>
                  {formatPrice(course.price)}
                </span>

                <span className="badge rounded-pill px-3 py-2 text-warning bg-warning-subtle fw-semibold">
                  <i className="bi bi-star-fill me-1"></i>
                  {course.points ?? 0} pts
                </span>

                <span
                  className="badge rounded-pill px-3 py-2 fw-semibold"
                  style={{ background: "#efe9ff", color: "#5a2ea6" }}
                >
                  <i className="bi bi-calendar-event me-1"></i>
                  {formatDate(course.creation_date)}
                </span>
              </div>

              {/* BOTONES */}
              <div className="mt-auto d-flex gap-2">
                <Link
                  className="btn w-100 text-white"
                  to={`/modules?course_id=${course.course_id}`}
                  style={{
                    borderRadius: 16,
                    background:
                      "linear-gradient(135deg,#0d6efd,#6f42c1)",
                    border: "none",
                    fontWeight: 500,
                  }}
                >
                  <i className="bi bi-eye me-2"></i>
                  Ver
                </Link>

                <button
                  className="btn btn-outline-secondary"
                  style={{ borderRadius: 16, width: 50 }}
                  disabled={!isAdmin && !isTeacher}
                  onClick={() => handleEditCourse?.(course)}
                >
                  <i className="bi bi-pencil-square"></i>
                </button>

                <button
                  className="btn btn-outline-danger"
                  style={{ borderRadius: 16, width: 50 }}
                  disabled={!isAdmin && !isTeacher}
                  onClick={() => handleDeleteCourse?.(course)}
                >
                  <i className="bi bi-trash"></i>
                </button>
              </div>

              {/* FOOTER */}
              <div className="mt-3 small text-muted d-flex align-items-center">
                <i className="bi bi-info-circle me-2"></i>
                Detalles claros de precio, puntos y fecha.
              </div>

            </div>
          </div>
        </div>
      );
    })}
  </div>
)}


    </div >
  );
};
 
 