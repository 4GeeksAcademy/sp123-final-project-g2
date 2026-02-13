import { useEffect } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

// Componente para mostrar un logro individual
const AchievementCard = ({ achievement }) => {
  return (
    <div className="card text-bg-dark mb-3" style={{ maxWidth: "18rem" }}>
      <div className="card-header">
        {achievement.name}
      </div>
      <div className="card-body">
        {achievement.icon && (
          <img
            src={achievement.icon}
            alt={achievement.name}
            className="img-fluid mb-2"
          />
        )}
        <p className="card-text">{achievement.description}</p>
        <p className="text-warning">Puntos requeridos: {achievement.required_points}</p>
      </div>
    </div>
  );
};

export const Achievements = () => {
  const { store, dispatch } = useGlobalReducer();
  const achievements = store.achievements || [];

  useEffect(() => {
    const getAchievements = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/api/achievements`,
          {
            headers: { Authorization: `Bearer ${store.token}` },
          }
        );

        if (!res.ok) {
          const text = await res.text();
          console.error("Respuesta backend NO JSON:", text);
          dispatch({ type: "set_achievements", payload: [] });
          return;
        }

        const data = await res.json();

        // Asegurarse de que sea un array
        const arrayData = Array.isArray(data) ? data : data.achievements || [];
        dispatch({ type: "set_achievements", payload: arrayData });

      } catch (error) {
        console.error("Error cargando logros:", error);
        dispatch({ type: "set_achievements", payload: [] });
      }
    };

    getAchievements();
  }, [dispatch, store.token]);

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Mis Logros</h1>

      {achievements.length === 0 ? (
        <p className="text-center">Aún no has obtenido logros.</p>
      ) : (
        <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          {achievements.map((achievement) => (
            <div key={achievement.achievement_id} className="col">
              <AchievementCard achievement={achievement} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
