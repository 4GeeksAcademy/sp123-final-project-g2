import bgImg from "../assets/img/background-screens.png";

export default function AuthShell({ children, title, subtitle, sidePanel = false }) {
  return (
    <div
      className="auth-theme"
      style={{
        backgroundImage: `url(${bgImg})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        minHeight: "100vh",
      }}
    >
      <div className="auth-shell">
        <div className={`auth-card ${sidePanel ? "auth-card-horizontal" : ""}`}>

          {/* Columna principal */}
          <div className="auth-card-main">
            {title && <div className="auth-title">{title}</div>}
            {subtitle && <div className="auth-sub">{subtitle}</div>}
            {children}
          </div>

          {/* Panel lateral opcional */}
          {sidePanel && (
            <div className="auth-card-side">
              <h3>MeetFit</h3>
              <p>
                Conecta con gente de tu ciudad, crea actividades deportivas
                y encuentra compañeros de entrenamiento sin complicaciones.
              </p>
              <ul>
                <li>🔍 Explora actividades cerca de ti</li>
                <li>💬 Queda con otras personas</li>
                <li>📅 Crea tus propios eventos</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
