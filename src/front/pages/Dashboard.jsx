import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { Link } from "react-router-dom";

export const Dashboard = () => {
  const { store } = useGlobalReducer();

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver el dashboard</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Dashboard</h1>

      {/* USER INFO */}
      <div className="card mb-4 shadow-sm">
        <div className="card-body">
          <h5 className="card-title">
            👋 Hola {store.current_user.first_name}
          </h5>
          <p className="mb-1">Email: {store.current_user.email}</p>
          <p className="mb-1">Rol: {store.current_user.role}</p>
          <p className="mb-0">
            ⭐ Puntos actuales: <strong>{store.current_user.current_points}</strong>
          </p>
        </div>
      </div>

      {/* QUICK STATS */}
      <div className="row text-center mb-4">
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5>🏆 Logros</h5>
              <p className="display-6">{store.achievements.length}</p>
              <Link to="/achievements" className="btn btn-outline-primary btn-sm">
                Ver logros
              </Link>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5>📊 Progreso</h5>
              <p className="display-6">{store.my_progress.length}</p>
              <Link to="/my-progress" className="btn btn-outline-success btn-sm">
                Ver progreso
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
