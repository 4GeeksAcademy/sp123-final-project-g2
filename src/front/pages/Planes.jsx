import { useNavigate } from "react-router-dom";

export const Planes = () => {
  const navigate = useNavigate();

  const handleGoCheckout = () => {
    navigate("/parchares-private-psique");
  };

  return (
    <div className="d-flex flex-column min-vh-100" style={{ background: "#f6f8ff" }}>
      <section
        className="flex-grow-1 d-flex align-items-center justify-content-center"
        style={{
          paddingTop: "90px",
          paddingBottom: "90px",
        }}
      >
        <div className="container text-center">
          <div className="mb-4">
            <i className="bi bi-credit-card-2-front fs-1 text-primary"></i>
          </div>

          <h1 className="fw-bold mb-2" style={{ fontSize: "2.4rem", color: "#0b1fb8" }}>
            Tipos de planes
          </h1>
          <p className="text-muted mb-5" style={{ fontSize: "1.05rem" }}>
            Elige el plan que mejor encaje contigo y empieza a mejorar tu voz.
          </p>

          <div className="row justify-content-center g-4">

            {/* PLAN FREE */}
            <div className="col-12 col-md-5 col-lg-4">
              <div
                className="card border-0 shadow-sm h-100"
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                }}
              >
                <div className="card-body p-4 d-flex flex-column">
                  <div
                    className="fw-bold rounded-pill mx-auto px-4 py-2 mb-4 text-white"
                    style={{
                      background: "linear-gradient(90deg,#5aa7ff,#78b8ff)",
                      fontSize: "1.05rem",
                      width: "fit-content",
                    }}
                  >
                    <i className="bi bi-lightning-charge-fill me-2"></i>
                    Plan FREE
                  </div>

                  <ul className="list-unstyled text-start px-2 flex-grow-1 mb-4 text-dark">
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-primary me-2"></i>Acceso limitado a cursos introductorios</li>
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-primary me-2"></i>Progreso básico</li>
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-primary me-2"></i>Sin certificado</li>
                    <li><i className="bi bi-check-circle-fill text-primary me-2"></i>Ideal para probar</li>
                  </ul>

                  <button
                    onClick={handleGoCheckout}
                    className="btn btn-outline-primary rounded-pill px-4 py-2 mx-auto"
                  >
                    <i className="bi bi-cart-fill me-2"></i>
                    Comprar curso
                  </button>
                </div>
              </div>
            </div>

            {/* PLAN PREMIUM */}
            <div className="col-12 col-md-5 col-lg-4">
              <div
                className="card border-0 shadow-lg h-100 position-relative"
                style={{
                  background: "linear-gradient(135deg, #0b1fb8 0%, #2f45ff 70%, #3c6bff 100%)",
                  borderRadius: "18px",
                  overflow: "hidden",
                }}
              >
                <div
                  className="position-absolute"
                  style={{
                    top: "14px",
                    right: "-46px",
                    transform: "rotate(20deg)",
                    background: "#ffc107",
                    color: "#1a1a1a",
                    padding: "8px 60px",
                    fontWeight: 800,
                    fontSize: "0.85rem",
                    boxShadow: "0 10px 24px rgba(0,0,0,0.18)",
                  }}
                >
                  <i className="bi bi-arrow-up-right-circle-fill me-2"></i>
                  EL MÁS VENDIDO
                </div>

                <div className="card-body p-4 d-flex flex-column text-white">
                  <div
                    className="fw-bold rounded-pill mx-auto px-4 py-2 mb-4"
                    style={{
                      background: "linear-gradient(90deg,#f0b44c,#c78a1d)",
                      fontSize: "1.05rem",
                      width: "fit-content",
                    }}
                  >
                    <i className="bi bi-gem me-2"></i>
                    Plan PREMIUM
                  </div>

                  <ul className="list-unstyled text-start px-2 flex-grow-1 mb-4">
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-warning me-2"></i>Acceso a todos los cursos</li>
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-warning me-2"></i>Niveles avanzados</li>
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-warning me-2"></i>Certificado</li>
                    <li className="mb-3"><i className="bi bi-check-circle-fill text-warning me-2"></i>Seguimiento completo</li>
                    <li><i className="bi bi-check-circle-fill text-warning me-2"></i>Soporte prioritario</li>
                  </ul>

                  <button
                    onClick={handleGoCheckout}
                    className="btn btn-light text-primary fw-bold rounded-pill px-4 py-2 mx-auto"
                  >
                    <i className="bi bi-cart-fill me-2"></i>
                    Comprar curso
                  </button>

                  <p className="mt-3 mb-0 opacity-75" style={{ fontSize: "0.95rem" }}>
                    <i className="bi bi-tag-fill me-2"></i>
                    9,99€/mes
                  </p>
                </div>
              </div>
            </div>

          </div>

          {/* BLOQUE VISUAL BAJO LAS CARDS (Stripe + seguridad + 7 días de prueba) */}
<div className="mt-5">
  <div
    className="mx-auto shadow-sm"
    style={{
      maxWidth: "860px",
      background: "#ffffff",
      borderRadius: "16px",
      padding: "18px 18px",
      border: "1px solid rgba(11,31,184,0.08)",
    }}
  >
    <div className="d-flex flex-column flex-md-row align-items-center justify-content-between gap-3">
      <div className="text-start">
        <div className="d-flex align-items-center gap-2 mb-1">
          <i className="bi bi-shield-lock-fill text-success fs-5"></i>
          <span className="fw-semibold" style={{ color: "#0b1fb8" }}>
            Tus datos estarán seguros
          </span>
        </div>
        <div className="text-muted" style={{ fontSize: "0.95rem" }}>
          Pago protegido con Stripe · Cancelas cuando quieras
        </div>
      </div>

      <div className="d-flex flex-column align-items-center gap-3">

        <span
          className="badge rounded-pill"
          style={{
            background: "rgba(11,31,184,0.08)",
            color: "#0b1fb8",
            padding: "10px 18px",
            fontSize: "0.95rem",
            fontWeight: 700,
          }}
        >
          <i className="bi bi-calendar2-week me-2"></i>
          7 días de prueba
        </span>

        {/* LOGOS OFICIALES */}
        <div className="d-flex align-items-center gap-4 flex-wrap justify-content-center">
          
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/6/6b/Stripe_Logo%2C_revised_2016.svg"
             alt="Stripe"
              style={{ height: "24px" }}
          />

          <img
            src="https://upload.wikimedia.org/wikipedia/commons/4/41/Visa_Logo.png"
            alt="Visa"
            style={{ height: "22px" }}
          />

          <img
            src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg"
            alt="Mastercard"
            style={{ height: "28px" }}
          />

          <img
            src="https://upload.wikimedia.org/wikipedia/commons/3/30/American_Express_logo.svg"
            alt="American Express"
            style={{ height: "26px" }}
          />

          <img
            src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"
            alt="Apple Pay"
            style={{ height: "22px" }}
          />

          <img
            src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Google_Pay_Logo.svg"
            alt="Google Pay"
            style={{ height: "24px" }}
          />

        </div>
      </div>
    </div>

    <div className="mt-3 text-muted" style={{ fontSize: "0.9rem" }}>
      <i className="bi bi-lock-fill me-2"></i>
      La información de tu tarjeta se procesa de forma segura y no se almacena en nuestros servidores.
    </div>
  </div>
</div>

        </div>
      </section>
    </div>
  );
};
