export const QuienesSomos = () => {
    const team = [
        {
            name: "Edgardo Salazar",
            role: "Full-Stack Developer Junior",
            meta: "26 años · Venezuela",
            desc: "Desarrollador full-stack junior. Apoya el desarrollo de interfaces y APIs, cuidando la claridad del código y la entrega constante.",
            img: "https://via.placeholder.com/800x800.png?text=Edgardo+Salazar",
        },
        {
            name: "Andrea Sabater",
            role: "Full-Stack Developer Junior",
            meta: "25 años · Elche (España)",
            desc: "Desarrolladora full-stack junior. Enfocada en construir experiencias de usuario limpias y funcionales, con mentalidad de producto.",
            img: "https://via.placeholder.com/800x800.png?text=Andrea+Sabater",
        },
        {
            name: "Gustavo Mesa",
            role: "Full-Stack Developer Senior",
            meta: "35 años · Colombia",
            desc: "Desarrollador full-stack senior. Aporta visión técnica, buenas prácticas y arquitectura para mantener el proyecto escalable y estable.",
            img: "https://via.placeholder.com/800x800.png?text=Gustavo+Mesa",
        },
    ];

    const timeline = [
        {
            month: "Octubre 2025",
            title: "Inicio del proyecto",
            text: "Definición del alcance, objetivos, roles y planificación del roadmap.",
            badge: "Inicio",
            badgeClass: "text-bg-primary",
        },
        {
            month: "Noviembre 2025",
            title: "Diseño y arquitectura",
            text: "Wireframes, estructura de componentes, modelo de datos y endpoints base.",
            badge: "Base",
            badgeClass: "text-bg-info",
        },
        {
            month: "Diciembre 2025",
            title: "MVP funcional",
            text: "Primer entregable con autenticación, navegación y módulos principales.",
            badge: "MVP",
            badgeClass: "text-bg-success",
        },
        {
            month: "Enero 2026",
            title: "Iteración y mejoras",
            text: "Refactor, tests, accesibilidad y optimización de experiencia de usuario.",
            badge: "Mejoras",
            badgeClass: "text-bg-warning",
        },
        {
            month: "Febrero 2026",
            title: "Proyecto final",
            text: "Cierre del desarrollo, pulido visual, documentación y despliegue final.",
            badge: "Final",
            badgeClass: "text-bg-dark",
        },
    ];

    return (
        <div className="qs-page">
            {/* HERO */}
            <header className="qs-hero">
                <div className="container py-4">
                    <div className="d-flex align-items-center justify-content-between gap-3 flex-wrap">
                        <div className="d-flex align-items-baseline gap-2">
                            <span className="qs-plus">+</span>
                            <span className="qs-brand">vocal</span>
                        </div>

                    </div>

                    <div className="row align-items-center mt-4 g-4">
                        <div className="col-12 col-lg-7">
                            <h1 className="qs-title mb-2">Conoce al equipo de +vocal</h1>
                            <p className="qs-subtitle mb-4">
                                Construimos una plataforma clara, accesible y enfocada en el progreso. Este es el equipo detrás
                                del producto.
                            </p>

                            <div className="d-flex gap-2 flex-wrap">
                                <a href="#equipo" className="btn qs-btn-primary">
                                    Ver equipo
                                </a>
                                <a href="#timeline" className="btn qs-btn-outline">
                                    Ver línea de tiempo
                                </a>
                            </div>
                        </div>

                        <div className="col-12 col-lg-5">
                            <div className="qs-hero-card p-4">
                                <div className="d-flex align-items-center gap-3">
                                    <div className="qs-dot"></div>
                                    <div>
                                        <div className="qs-hero-card-title">Nuestra misión</div>
                                        <div className="qs-hero-card-text">
                                            Aprendizaje práctico, seguimiento del progreso y una experiencia visual limpia.
                                        </div>
                                    </div>
                                </div>

                                <hr className="my-4" />

                                <div className="row g-3">
                                    <div className="col-6">
                                        <div className="qs-mini">
                                            <div className="qs-mini-k">Equipo</div>
                                            <div className="qs-mini-v">3 devs</div>
                                        </div>
                                    </div>
                                    <div className="col-6">
                                        <div className="qs-mini">
                                            <div className="qs-mini-k">Roadmap</div>
                                            <div className="qs-mini-v">Oct 2025 → Feb 2026</div>
                                        </div>
                                    </div>
                                    <div className="col-12">
                                        <div className="qs-mini">
                                            <div className="qs-mini-k">Entrega</div>
                                            <div className="qs-mini-v">Proyecto final (Feb 2026)</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* TEAM */}
            <section id="equipo" className="container py-5">
                <div className="text-center mb-4">
                    <h2 className="qs-section-title">Nuestro equipo</h2>
                    <p className="qs-section-subtitle mb-0">
                        Personas reales, trabajo real. Tres perfiles complementarios para llevar +vocal a producción.
                    </p>
                </div>

                <div className="row g-4">
                    {team.map((m) => (
                        <div key={m.name} className="col-12 col-md-6 col-lg-4">
                            <div className="card qs-card h-100">
                                <img
                                    src={m.img}
                                    className="card-img-top qs-card-img"
                                    alt={m.name}
                                />
                                <div className="card-body d-flex flex-column">
                                    <div className="d-flex justify-content-between align-items-start gap-2">
                                        <h5 className="card-title mb-0">{m.name}</h5>
                                        <span className="badge rounded-pill text-bg-primary qs-badge">
                                            {m.role.includes("Senior") ? "Senior" : "Junior"}
                                        </span>
                                    </div>

                                    <div className="qs-meta mt-1">{m.role}</div>
                                    <div className="qs-meta-muted">{m.meta}</div>

                                    <p className="card-text mt-3 mb-0">{m.desc}</p>

                                    <div className="mt-auto pt-3">
                                        <div className="qs-divider"></div>
                                        <div className="d-flex gap-2 mt-3 flex-wrap">
                                            <span className="btn btn-sm qs-chip">Full-Stack</span>
                                            <span className="btn btn-sm qs-chip">Producto</span>
                                            <span className="btn btn-sm qs-chip">Calidad</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* TIMELINE */}
            <section id="timeline" className="qs-soft-section py-5">
                <div className="container">
                    <div className="text-center mb-4">
                        <h2 className="qs-section-title">Línea de tiempo</h2>
                        <p className="qs-section-subtitle mb-0">
                            Desde Octubre de 2025 hasta Febrero de 2026, terminando con el proyecto final.
                        </p>
                    </div>

                    <div className="row g-4">
                        {timeline.map((t, idx) => (
                            <div key={t.month} className="col-12 col-md-6 col-lg-4">
                                <div className="card qs-timeline-card h-100">
                                    <div className="card-body">
                                        <div className="d-flex align-items-center justify-content-between gap-2">
                                            <div className="qs-time">{t.month}</div>
                                            <span className={`badge ${t.badgeClass} rounded-pill`}>{t.badge}</span>
                                        </div>

                                        <h5 className="mt-3 mb-2">{t.title}</h5>
                                        <p className="mb-0 text-secondary">{t.text}</p>

                                        {/* detalle visual de progreso */}
                                        <div className="qs-progress mt-4">
                                            <div className="qs-progress-track">
                                                <div
                                                    className="qs-progress-fill"
                                                    style={{ width: `${Math.round(((idx + 1) / timeline.length) * 100)}%` }}
                                                />
                                            </div>
                                            <div className="qs-progress-label">
                                                {Math.round(((idx + 1) / timeline.length) * 100)}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="text-center mt-4">
                        <div className="qs-final-pill">
                            <span className="qs-final-dot"></span>
                            <span className="qs-final-text">Entrega final: Proyecto final (Febrero 2026)</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* FOOTER */}
            <footer className="qs-footer py-4 mt-0">
                <div className="container d-flex flex-wrap align-items-center justify-content-between gap-3">
                    <div className="d-flex align-items-baseline gap-2 text-white">
                        <strong style={{ fontSize: 18 }}>+vocal</strong>
                        <span style={{ opacity: 0.8, fontSize: 14 }}>· Equipo & Roadmap</span>
                    </div>

                    <div className="d-flex gap-3 flex-wrap" style={{ opacity: 0.9 }}>
                        <span className="qs-footer-link">Contacto</span>
                    </div>
                </div>
            </footer>
        </div>
    );
};
