import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

export const Navbar = () => {
  const { store, dispatch } = useGlobalReducer();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");

    dispatch({ type: "handle_token", payload: "" });
    dispatch({ type: "handle_user", payload: {} });
    dispatch({ type: "handle_isLogged", payload: false });

    navigate("/");
  };


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

  const handleRegistro = () => {
  dispatch({
    type: "handle_alert",
    payload: { text: "", color: "", display: false }
  });

  navigate("/register"); // asegúrate que la ruta exista
};
  return (
    <nav
      className="navbar navbar-expand-lg navbar-dark shadow px-4"
      style={{ background: "linear-gradient(90deg,#1e2bd6,#2f45ff)" }}
    >
      {/* LOGO */}
      <Link to="/" className="navbar-brand fw-bold fs-4">
       +Vocal
      </Link>

      {/* HAMBURGUESA */}
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      <div className="collapse navbar-collapse" id="mainNavbar">
        
        {/* IZQUIERDA */}
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          
          <li className="nav-item">
            <Link className="nav-link fw-semibold" to="/quienes-somos">
              Quiénes somos
            </Link>
          </li>

          {store.isLogged && (
            <li className="nav-item dropdown">
              <a
                className="nav-link dropdown-toggle text-white"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                📚 Mis Cursos
              </a>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/courses">
                    Cursos
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/my-progress">
                    Mi progreso
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/achievements">
                    Logros
                  </Link>
                </li>
              </ul>
            </li>
          )}

        </ul>

        {/* DERECHA */}
        <div className="d-flex align-items-center gap-3">

          {store.isLogged && (
            <span className="text-light">
              👋 Hola, <strong>{store.current_user?.first_name || "Usuario"}</strong>
            </span>
          )}

          <button
            onClick={handleLogin}
            className={`btn ${
              store.isLogged
                ? "btn-outline-light"
                : "btn-light text-primary fw-bold"
            } rounded-pill px-3`}
          >
            {store.isLogged ? "Cerrar sesión" : "Iniciar sesión"}
          </button>

          {!store.isLogged && (
            <button
              onClick={handleRegistro}
              className="btn btn-warning fw-bold rounded-pill px-3" >
              Registro
            </button> 
          )}
        </div>
      </div>
    </nav>
  );
};

  
