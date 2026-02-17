import { useNavigate } from "react-router-dom";

export const QuienesSomos = () => {
  const navigate = useNavigate();

  const team = [
    {
      name: "Edgardo Salazar",
      role: "Full-Stack Developer Junior",
      meta: "26 años · Venezuela",
      desc: "Desarrollador full-stack junior. Apoya el desarrollo de interfaces y APIs, cuidando la claridad del código y la entrega constante.",
      img: "/img/ed4d4075-5ddf-4764-b618-f34575212b45.JPG",
      level: "Junior",
      position: "center 25%",
      icon: "bi-code-slash",
      skills: ["bi-filetype-js", "bi-braces", "bi-git"],
    },
    {
      name: "Andrea Sabater",
      role: "Full-Stack Developer Junior",
      meta: "25 años · Elche (España)",
      desc: "Desarrolladora full-stack junior. Enfocada en construir experiencias de usuario limpias y funcionales, con mentalidad de producto.",
      img: "/img/9FD5CACB-3DA6-43E3-8205-AC24B701A3B0 2.JPEG",
      level: "Junior",
      position: "center 30%",
      icon: "bi-laptop",
      skills: ["bi-bootstrap", "bi-palette", "bi-git"],
    },
    {
      name: "Gustavo Mesa",
      role: "Full-Stack Developer Senior",
      meta: "35 años · Colombia",
      desc: "Desarrollador full-stack senior. Aporta visión técnica, buenas prácticas y arquitectura para mantener el proyecto escalable y estable.",
      img: "https://via.placeholder.com/800x800.png?text=Gustavo+Mesa",
      level: "Senior",
      position: "center",
      icon: "bi-cpu",
      skills: ["bi-diagram-3", "bi-shield-check", "bi-git"],
    },
  ];

  const timeline = [
    { month: "Octubre 2025", title: "Inicio del proyecto", text: "Definición del alcance y planificación.", pct: 20 },
    { month: "Noviembre 2025", title: "Diseño", text: "Wireframes y arquitectura base.", pct: 40 },
    { month: "Diciembre 2025", title: "MVP", text: "Primer entregable funcional.", pct: 60 },
    { month: "Enero 2026", title: "Mejoras", text: "Optimización y refactor.", pct: 80 },
    { month: "Febrero 2026", title: "Entrega final", text: "Deploy y documentación.", pct: 100 },
  ];

  return (
    <div className="bg-white" style={{ minHeight: "100vh" }}>
      {/* HEADER / TITULO */}
      <header className="border-bottom">
        <div className="container py-5">
          <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div>
              <div className="text-uppercase text-primary fw-semibold small mb-2">
                <i className="bi bi-people-fill me-2"></i>
                Quiénes somos
              </div>
              <h1 className="display-6 fw-bold mb-2">Equipo +Vocal</h1>
              <p className="text-muted mb-0">
                Conoce al equipo y el avance del proyecto.
              </p>
            </div>

            <span className="badge text-bg-light border text-secondary rounded-pill px-3 py-2">
              <i className="bi bi-code-square me-2"></i>
              Full-Stack · UI · APIs
            </span>
          </div>
        </div>
      </header>

      {/* TEAM */}
      <section className="container py-5">
        <div className="row g-4">
          {team.map((m) => (
            <div key={m.name} className="col-12 col-md-6 col-lg-4">
              <div
                className="card border-0 shadow-sm h-100 text-center"
                style={{
                  borderRadius: 20,
                  overflow: "hidden",
                  transition: "transform .15s ease, box-shadow .15s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow = "0 .75rem 1.5rem rgba(0,0,0,.08)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "";
                }}
              >
                {/* FOTO */}
                <div style={{ height: 260, overflow: "hidden" }}>
                  <img
                    src={m.img}
                    alt={m.name}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      objectPosition: m.position,
                      transform: "scale(1.02)",
                    }}
                  />
                </div>

                <div className="card-body d-flex flex-column">
                  {/* NOMBRE + BADGE + ICONO */}
                  <div className="d-flex justify-content-center align-items-center gap-2 flex-wrap">
                    <span
                      className="d-inline-flex align-items-center justify-content-center rounded-circle bg-primary-subtle text-primary"
                      style={{ width: 38, height: 38 }}
                      title="Developer"
                    >
                      <i className={`bi ${m.icon} fs-5`}></i>
                    </span>

                    <h5 className="mb-0">{m.name}</h5>

                    <span
                      className={`badge rounded-pill ${
                        m.level === "Senior" ? "text-bg-dark" : "text-bg-primary"
                      }`}
                    >
                      {m.level}
                    </span>
                  </div>

                  <div className="text-primary fw-semibold mt-2">{m.role}</div>
                  <div className="text-muted small">{m.meta}</div>

                  {/* ICONOS DE SKILLS */}
                  <div className="d-flex justify-content-center gap-3 mt-3 text-secondary">
                    {m.skills.map((ic) => (
                      <span key={ic} className="border rounded-pill px-3 py-1 bg-light">
                        <i className={`bi ${ic} me-2`}></i>
                        <span className="small">Skill</span>
                      </span>
                    ))}
                  </div>

                  <p className="mt-3 text-secondary mb-0">{m.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* TIMELINE */}
      <section className="container pb-5">
        <div className="d-flex align-items-end justify-content-between flex-wrap gap-2 mb-3">
          <div>
            <h2 className="h4 fw-bold mb-1">
              <i className="bi bi-graph-up-arrow text-primary me-2"></i>
              Progreso del trabajo
            </h2>
            <p className="text-muted mb-0">Hitos del proyecto y porcentaje completado.</p>
          </div>
          <span className="badge text-bg-primary rounded-pill px-3 py-2">
            <i className="bi bi-check2-circle me-2"></i>
            Seguimiento
          </span>
        </div>

        <div className="row g-4">
          {timeline.map((t, i) => (
            <div key={i} className="col-12 col-md-6 col-lg-4">
              <div
                className="card border-0 shadow-sm h-100"
                style={{ borderRadius: 18 }}
              >
                <div className="card-body">
                  <div className="fw-bold text-primary">
                    <i className="bi bi-calendar-event me-2"></i>
                    {t.month}
                  </div>

                  <h5 className="mt-2">{t.title}</h5>
                  <p className="text-secondary mb-3">{t.text}</p>

                  {/* PORCENTAJE + PROGRESS */}
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span className="text-muted small">Completado</span>
                    <span className="fw-semibold small">{t.pct}%</span>
                  </div>

                  <div className="progress" style={{ height: 12, borderRadius: 999 }}>
                    <div
                      className="progress-bar progress-bar-striped progress-bar-animated"
                      role="progressbar"
                      style={{
                        width: `${t.pct}%`,
                        borderRadius: 999,
                      }}
                      aria-valuenow={t.pct}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    >
                      <span className="small fw-semibold">{t.pct}%</span>
                    </div>
                  </div>

                  {/* 0 - 100 */}
                  <div className="d-flex justify-content-between text-muted small mt-2">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-5">
          <button
            className="btn btn-outline-primary rounded-pill px-4"
            onClick={() => navigate(-1)}
          >
            <i className="bi bi-arrow-left me-2"></i>
            Volver atrás
          </button>
        </div>
      </section>
    </div>
  );
};

