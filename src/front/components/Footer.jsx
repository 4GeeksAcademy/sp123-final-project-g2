export const Footer = () => (
  <footer className="bg-white border-top py-4 mt-auto">
    <div className="container text-center">

      {/* Redes sociales */}
      <div className="mb-3 fs-4">
        <a href="#" className="text-dark me-3">
          <i className="bi bi-instagram"></i>
        </a>
        <a href="#" className="text-dark me-3">
          <i className="bi bi-twitter-x"></i>
        </a>
        <a href="#" className="text-dark me-3">
          <i className="bi bi-linkedin"></i>
        </a>
        <a href="#" className="text-dark">
          <i className="bi bi-github"></i>
        </a>
      </div>

      {/* Copyright */}
      <div className="small text-secondary">
        © 2026 <span className="fw-semibold text-dark">+vocal</span>
      </div>

      {/* Firma */}
      <div className="small text-secondary">
        Hecho con ❤️ por el equipo de +vocal
      </div>

    </div>
  </footer>
);
