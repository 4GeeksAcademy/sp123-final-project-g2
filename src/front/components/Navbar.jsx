import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

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

  return (
    <nav
      className="navbar navbar-expand-lg shadow px-4"
      style={{ backgroundColor: "#4A90E2" }}>
      
      <Link to="/" className="navbar-brand fw-bold fs-4 text-white">
        +VO
      </Link>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar" >

        <span className="navbar-toggler-icon"></span>
      </button>

      <div className="collapse navbar-collapse" id="mainNavbar">

        <ul className="navbar-nav me-auto mb-2 mb-lg-0">

          <li className="nav-item">
            <Link className="nav-link text-white" to="/quienes-somos">
              ℹ️ Sobre nosotros
            </Link>
          </li>

          {!store.isLogged && (
            <li className="nav-item">
              <Link className="nav-link text-white" to="/courses-public">
                📘 Cursos disponibles
              </Link>
            </li>
          )}

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

        <div className="d-flex align-items-center gap-3">

          {store.isLogged ? (
            <>
              <span className="text-white">
                👋 Hola,{" "}
                <strong>
                  {store.current_user?.first_name || "Usuario"}
                </strong>
              </span>

              <button
                onClick={handleLogout}
                className="btn btn-light btn-sm"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link text-white">
                Iniciar sesión
              </Link>
              <Link to="/signup" className="nav-link text-white">
                Registro
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
