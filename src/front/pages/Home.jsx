import React, { useEffect } from "react"
import rigoImageUrl from "../assets/img/rigo-baby.jpg";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Link } from "react-router-dom";


export const Home = () => {
  return (
    <>
      {/* HOME PRINCIPAL */}
      <main>
        {/* HERO */}
        <section className="voc-hero">
          <div className="container py-5">
            <div className="row align-items-center">
              <div className="col-12 col-lg-7">
                <h1 className="voc-hero-title mb-1">+vocal</h1>

                <p className="voc-hero-subtitle mb-3">
                  APRENDE LENGUA DE SIGNOS DESDE CERO, A TU RITMO
                </p>

                <p className="voc-hero-lead mb-4">
                  Cursos estructurados, vídeos prácticos y seguimiento de progreso.
                </p>

                <div className="d-flex gap-3 flex-wrap">
                  <a className="btn voc-btn-brand" href="/registro">
                    Empieza gratis
                  </a>
                  <a className="btn voc-btn-ghost" href="/planes">
                    Ver planes
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* DESCRIPCIÓN */}
        <section className="py-4">
          <div className="container">
            <p className="text-center mb-0 voc-desc">
              +vocal es una plataforma web para el aprendizaje básico de la lengua de signos,
              con un sistema de acceso y vistas diferenciadas de alumno y administrador
            </p>
          </div>
        </section>

        {/* FEATURES */}
        <section className="pb-5">
          <div className="container">
            <div className="row g-3 justify-content-center">
              {[
                { icon: "📈", text: "Aprendizaje progresivo" },
                { icon: "🤟", text: "Vídeos en lengua de signos" },
                { icon: "🧩", text: "Ejercicios prácticos" },
                { icon: "🧑‍🏫", text: "Accesible y estructurado" },
              ].map((f) => (
                <div className="col-6 col-md-3" key={f.text}>
                  <div className="card voc-feature h-100">
                    <div className="card-body p-3 text-center">
                      <div className="voc-feature-icon">{f.icon}</div>
                      <p className="voc-feature-title mb-0">{f.text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CÓMO FUNCIONA */}
        <section className="py-5 voc-soft-section">
          <div className="container">
            <h2 className="text-center voc-section-title mb-4">¿Cómo funciona?</h2>

            <div className="row text-center g-4 align-items-stretch">
              <div className="col-md-4">
                <div className="h-100 d-flex flex-column justify-content-center">
                  <div className="voc-step-number">1</div>
                  <div className="voc-step-pill mx-auto">Regístrate gratis</div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="h-100 d-flex flex-column justify-content-center">
                  <div className="voc-step-number">2</div>
                  <div className="voc-step-pill voc-step-pill--sky mx-auto">
                    Aprende con lecciones en vídeo
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="h-100 d-flex flex-column justify-content-center">
                  <div className="voc-step-number">3</div>
                  <div className="voc-step-pill mx-auto">Sigue tu progreso y mejora</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* OPINIONES */}
        <section className="py-5">
          <div className="container">
            <h3 className="text-center voc-section-title mb-4">Nuestros alumnos opinan</h3>

            <div className="row g-3">
              {[
                {
                  plan: "Plan FREE",
                  planClass: "text-bg-primary",
                  name: "Matías Gutiérrez",
                  text:
                    "La plataforma es sencilla y fácil de usar, ideal para empezar con la lengua de signos.",
                },
                {
                  plan: "Plan PREMIUM",
                  planClass: "text-bg-warning",
                  name: "Sara García",
                  text: "Los contenidos están bien organizados y permiten aprender paso a paso.",
                },
                {
                  plan: "Plan PREMIUM",
                  planClass: "text-bg-warning",
                  name: "Carmen Benavente",
                  text: "Me ha resultado útil para practicar y seguir mi progreso de forma clara.",
                },
              ].map((t) => (
                <div className="col-md-4" key={t.name}>
                  <div className="card voc-card-soft h-100">
                    <div className="card-body p-3">
                      <div className="d-flex align-items-center justify-content-between mb-2">
                        <span className={`badge voc-badge-plan ${t.planClass}`}>{t.plan}</span>
                      </div>

                      <div className="d-flex align-items-center gap-2 mb-2">
                        <div className="voc-avatar">{t.name.slice(0, 1)}</div>
                        <strong>{t.name}</strong>
                      </div>

                      <p className="mb-0 text-secondary">“{t.text}”</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="voc-footer pt-5 pb-4">
        <div className="container">
          <div className="row gy-4">
            <div className="col-md-4">
              <div className="voc-brand fs-4">+vocal</div>
            </div>

            <div className="col-6 col-md-2">
              <div className="fw-bold mb-2">Planes</div>
              <div className="d-grid gap-1">
                <a href="/planes">Planes</a>
                <a href="/planes">Información</a>
                <a href="/login">Mi Área</a>
              </div>
            </div>

            <div className="col-6 col-md-3">
              <div className="fw-bold mb-2">Políticas</div>
              <div className="d-grid gap-1">
                <a href="/privacidad">Política de privacidad</a>
                <a href="/aviso-legal">Aviso legal</a>
                <a href="/cookies">Política de cookies</a>
              </div>
            </div>

            <div className="col-6 col-md-3">
              <div className="fw-bold mb-2">Sobre</div>
              <div className="d-grid gap-1">
                <a href="/sobre-nosotros">Quiénes somos</a>
                <a href="/contacto">Contacto</a>
              </div>
            </div>
          </div>

          <hr className="my-4 opacity-25" />
          <div className="small">© {new Date().getFullYear()} +vocal</div>
        </div>
      </footer>
    </>
  );
};
