import { useNavigate } from "react-router-dom";

export const Planes = () => {
  const navigate = useNavigate();

  const handleGoRegister = () => {
    navigate("/register");
  };

  const handleGoCheckout = () => {
    // Ruta de tu pasarela de pago (cámbiala si usas otra)
    navigate("/checkout");
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <section
        className="flex-grow-1 d-flex align-items-center justify-content-center text-white"
        style={{
          background:
            "linear-gradient(135deg, #0b1fb8 0%, #2336e8 40%, #2f45ff 70%, #3c6bff 100%)",
          paddingTop: "90px",
          paddingBottom: "90px",
        }}
      >
        <div className="container text-center">
          <h1 className="fw-normal mb-5" style={{ fontSize: "2.4rem" }}>
            Planes y suscripción
          </h1>

          <div className="row justify-content-center g-4">
            {/* PLAN FREE */}
            <div className="col-12 col-md-5 col-lg-4">
              <div
                className="card border-0 shadow-lg text-white h-100"
                style={{
                  background: "rgba(255,255,255,0.14)",
                  backdropFilter: "blur(10px)",
                  borderRadius: "18px",
                }}
              >
                <div className="card-body p-4 d-flex flex-column">
                  <div
                    className="fw-bold rounded-pill mx-auto px-4 py-2 mb-4"
                    style={{
                      background: "linear-gradient(90deg,#5aa7ff,#78b8ff)",
                      fontSize: "1.05rem",
                      width: "fit-content",
                    }}
                  >
                    Plan FREE
                  </div>

                  <ul className="list-unstyled text-start px-2 flex-grow-1 mb-4">
                    <li className="mb-3">• Acceso limitado a cursos introductorios</li>
                    <li className="mb-3">• Progreso básico</li>
                    <li className="mb-3">• Sin certificado</li>
                    <li>• Ideal para probar</li>
                  </ul>

                  <button
                    onClick={handleGoRegister}
                    className="btn btn-outline-light rounded-pill px-4 py-2 mx-auto"
                    style={{ fontSize: "1rem" }}
                  >
                    Registrarse
                  </button>
                </div>
              </div>
            </div>

            {/* PLAN PREMIUM */}
            <div className="col-12 col-md-5 col-lg-4">
              <div
                className="card border-0 shadow-lg text-white h-100"
                style={{
                  background: "rgba(255,255,255,0.16)",
                  backdropFilter: "blur(10px)",
                  borderRadius: "18px",
                }}
              >
                <div className="card-body p-4 d-flex flex-column">
                  <div
                    className="fw-bold rounded-pill mx-auto px-4 py-2 mb-4"
                    style={{
                      background: "linear-gradient(90deg,#f0b44c,#c78a1d)",
                      fontSize: "1.05rem",
                      width: "fit-content",
                    }}
                  >
                    Plan PREMIUM
                  </div>

                  <ul className="list-unstyled text-start px-2 flex-grow-1 mb-4">
                    <li className="mb-3">• Acceso a todos los cursos</li>
                    <li className="mb-3">• Niveles avanzados</li>
                    <li className="mb-3">• Certificado</li>
                    <li className="mb-3">• Seguimiento completo</li>
                    <li>• Soporte prioritario</li>
                  </ul>

                  <button
                    onClick={handleGoCheckout}
                    className="btn btn-light text-primary fw-bold rounded-pill px-4 py-2 mx-auto"
                    style={{ fontSize: "1rem" }}
                  >
                    Suscribirme
                  </button>

                  <p className="mt-3 mb-0 opacity-75" style={{ fontSize: "0.95rem" }}>
                    9,99€/mes
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
