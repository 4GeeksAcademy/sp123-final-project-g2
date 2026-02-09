import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {
  const { store, dispatch } = useGlobalReducer();
  const navigate = useNavigate();

  const handleRegistro = () => navigate("/signup");

  const handleLogin = () => {
    if (store.isLogged) {
      localStorage.removeItem("token");

      dispatch({ type: "handle_token", payload: "" });
      dispatch({ type: "handle_user", payload: {} });
      dispatch({ type: "handle_isLogged", payload: false });

      navigate("/");
    } else {
      dispatch({
        type: "handle_alert",
        payload: { text: "", color: "", display: false }
      });
      navigate("/login");
    }
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow px-4">
      
      <Link to="/" className="navbar-brand fw-bold fs-4">
        🤟 SignaLearn
      </Link>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar"
        aria-controls="mainNavbar"
        aria-expanded="false"
        aria-label="Toggle navigation">
        <span className="navbar-toggler-icon"></span>
      </button>

      <div className="collapse navbar-collapse" id="mainNavbar">

        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          {store.isLogged && (
            <>
              <li className="nav-item">
                <Link className="nav-link" to="/courses">
                  📚 Cursos
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/my-progress">
                  📈 Mi progreso
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/achievements">
                  🏆 Logros
                </Link>
              </li>
            </>
          )}
        </ul>
        
        <div className="d-flex align-items-center gap-3">
          {store.isLogged && (
            <span className="text-light">
              👋 Hola, <strong>{store.current_user?.first_name || "Usuario"}</strong>
            </span>
          )}

          <button
            onClick={handleLogin}
            className={`btn ${
              store.isLogged ? "btn-outline-light" : "btn-light"
            }`}
          >
            {store.isLogged ? "Cerrar sesión" : "Iniciar sesión"}
          </button>

          {!store.isLogged && (
            <button
              onClick={handleRegistro}
              className="btn btn-outline-light"
            >
              Registro
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};
