import { useEffect, useMemo, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Link } from "react-router-dom";

// ===== Helpers =====
const clamp = (n) => Math.max(0, Math.min(100, Number.isFinite(n) ? n : 0));

const getPct = (p) => {
  // Soporta: progress_percentage, percentage, progress, etc.
  if (p?.progress_percentage !== undefined) return clamp(Number(p.progress_percentage));
  if (p?.percentage !== undefined) return clamp(Number(p.percentage));
  if (p?.progress !== undefined) return clamp(Number(p.progress));
  // Si no hay % pero está completed
  if (p?.completed === true) return 100;
  return 0;
};

const getCourseKey = (p) => p?.course_id ?? p?.course_title ?? "Sin curso";

// ===== Card individual =====
const ProgressCard = ({ progress }) => {
  const pct = getPct(progress);

  return (
    <div className="card progress-card shadow-sm">
      <div className="card-body">
        <div className="d-flex align-items-start justify-content-between">
          <div>
            <div className="progress-card-kicker">
              <i className="bi bi-journal-bookmark-fill me-2"></i>
              Curso
            </div>
            <h5 className="progress-card-title mb-1">{progress.course_title}</h5>
            <div className="text-muted small">
              <div className="mb-1">
                <i className="bi bi-layers me-2"></i>
                <strong>Módulo:</strong> {progress.module_title}
              </div>
              <div>
                <i className="bi bi-play-btn-fill me-2"></i>
                <strong>Lección:</strong> {progress.lesson_title}
              </div>
            </div>
          </div>

          <span
            className={`badge ${
              progress.completed ? "text-bg-success" : "text-bg-warning"
            }`}
          >
            <i className={`bi ${progress.completed ? "bi-check2-circle" : "bi-hourglass-split"} me-1`}></i>
            {progress.completed ? "Completado" : "En progreso"}
          </span>
        </div>

        <div className="mt-3 d-flex align-items-center justify-content-between">
          <div className="progress-card-pct">
            <i className="bi bi-graph-up-arrow me-2"></i>
            {pct}%
          </div>

          {/* Si tienes ruta a curso, cámbiala aquí */}
          <Link to="/cursos" className="btn btn-outline-primary btn-sm">
            Ver curso <i className="bi bi-arrow-right ms-1"></i>
          </Link>
        </div>

        <div className="progress progress-modern mt-2">
          <div
            className="progress-bar"
            role="progressbar"
            style={{ width: `${pct}%` }}
            aria-valuenow={pct}
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>
      </div>
    </div>
  );
};

export const MyProgress = () => {
  const { store, dispatch } = useGlobalReducer();
  const progressList = store.my_progress || [];

  // búsqueda simple
  const [q, setQ] = useState("");

  useEffect(() => {
    const getProgress = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress`, {
          headers: { Authorization: `Bearer ${store.token}` },
        });

        if (!res.ok) {
          const text = await res.text();
          console.error("Respuesta backend NO OK:", text);
          dispatch({ type: "set_my_progress", payload: [] });
          return;
        }

        const data = await res.json();
        const arrayData = Array.isArray(data) ? data : data.progress || data.results || [];
        dispatch({ type: "set_my_progress", payload: arrayData });
      } catch (error) {
        console.error("Error cargando progreso:", error);
        dispatch({ type: "set_my_progress", payload: [] });
      }
    };

    if (store.isLogged) getProgress();
  }, [store.isLogged, store.token, dispatch]);

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver tu progreso</h4>
      </div>
    );
  }

  // ===== métricas y agrupación por curso =====
  const {
    totalItems,
    completedItems,
    overallPct,
    coursesCount,
    grouped,
    filteredGrouped,
  } = useMemo(() => {
    const list = Array.isArray(progressList) ? progressList : [];
    const total = list.length;
    const completed = list.filter((p) => p?.completed === true || p?.status === "completed").length;

    // porcentaje medio (si hay %) o por completados
    const pcts = list.map(getPct);
    const avgPct = total > 0 ? Math.round(pcts.reduce((a, b) => a + b, 0) / total) : 0;

    // agrupar por curso
    const map = new Map();
    for (const p of list) {
      const k = getCourseKey(p);
      if (!map.has(k)) map.set(k, []);
      map.get(k).push(p);
    }

    const groups = Array.from(map.entries()).map(([courseKey, items]) => ({
      courseKey,
      courseTitle: items?.[0]?.course_title || String(courseKey),
      items,
    }));

    // filtro
    const qq = q.trim().toLowerCase();
    const filtered =
      qq.length === 0
        ? groups
        : groups
            .map((g) => ({
              ...g,
              items: g.items.filter((p) => {
                const text = `${p.course_title || ""} ${p.module_title || ""} ${p.lesson_title || ""}`.toLowerCase();
                return text.includes(qq);
              }),
            }))
            .filter((g) => g.items.length > 0);

    return {
      totalItems: total,
      completedItems: completed,
      overallPct: avgPct,
      coursesCount: groups.length,
      grouped: groups,
      filteredGrouped: filtered,
    };
  }, [progressList, q]);

  return (
    <div className="container mt-4">
      {/* HERO estilo dashboard */}
      <div className="dashboard-hero mb-4">
        <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
          <div>
            <h1 className="dashboard-hero-title mb-1">
              <i className="bi bi-bar-chart-line-fill me-2"></i>
              Mi Progreso
            </h1>
            <p className="dashboard-hero-subtitle mb-0">
              Revisa tus cursos, módulos y lecciones completadas.
            </p>
          </div>

          <div className="dashboard-hero-icon">
            <i className="bi bi-graph-up-arrow"></i>
          </div>
        </div>
      </div>

      {/* STATS (como la imagen del dashboard) */}
      <div className="row g-4 mb-4">
        <div className="col-12 col-md-4">
          <div className="card dashboard-stat-card">
            <div className="card-body">
              <i className="bi bi-check2-circle dashboard-icon"></i>
              <div className="dashboard-label mt-2">Completadas</div>
              <div className="dashboard-big">
                {completedItems}
                <span className="dashboard-big-suffix"> / {totalItems}</span>
              </div>
              <div className="dashboard-subtext">Lecciones registradas</div>
            </div>
          </div>
        </div>

        <div className="col-12 col-md-4">
          <div className="card dashboard-stat-card">
            <div className="card-body">
              <i className="bi bi-journal-bookmark-fill dashboard-icon"></i>
              <div className="dashboard-label mt-2">Cursos</div>
              <div className="dashboard-big">{coursesCount}</div>
              <div className="dashboard-subtext">Con actividad</div>
            </div>
          </div>
        </div>

        <div className="col-12 col-md-4">
          <div className="card dashboard-stat-card">
            <div className="card-body">
              <i className="bi bi-graph-up-arrow dashboard-icon"></i>
              <div className="dashboard-label mt-2">Progreso</div>
              <div className="dashboard-big">{overallPct}%</div>
              <div className="progress dashboard-progress mt-2">
                <div className="progress-bar" style={{ width: `${overallPct}%` }} />
              </div>
              <div className="dashboard-subtext">Promedio general</div>
            </div>
          </div>
        </div>
      </div>

      {/* BUSCADOR + CTA */}
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <div className="progress-search">
          <i className="bi bi-search"></i>
          <input
            className="form-control"
            placeholder="Buscar curso, módulo o lección..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        <Link to="/cursos" className="btn btn-outline-primary">
          <i className="bi bi-journal-text me-2"></i>
          Ir a cursos
        </Link>
      </div>

      {/* LISTADO */}
      {progressList.length === 0 ? (
        <div className="text-center text-muted py-5">
          <i className="bi bi-emoji-frown fs-1 d-block mb-2"></i>
          Aún no tienes progreso registrado
        </div>
      ) : filteredGrouped.length === 0 ? (
        <div className="text-center text-muted py-5">
          <i className="bi bi-search fs-1 d-block mb-2"></i>
          No hay resultados para “{q}”
        </div>
      ) : (
        filteredGrouped.map((group) => (
          <div key={group.courseKey} className="mb-4">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <h4 className="m-0 progress-group-title">
                <i className="bi bi-folder2-open me-2"></i>
                {group.courseTitle}
              </h4>
              <span className="text-muted small">
                {group.items.length} items
              </span>
            </div>

            <div className="row g-3">
              {group.items.map((item, index) => (
                <div className="col-12 col-lg-6" key={item.progress_id || `${group.courseKey}-${index}`}>
                  <ProgressCard progress={item} />
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

