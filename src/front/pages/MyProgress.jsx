import { useEffect } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

// Card individual de progreso
const ProgressCard = ({ progress }) => {
  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-body">
        <h5 className="card-title">{progress.course_title}</h5>

        <p className="card-text">
          <strong>Módulo:</strong> {progress.module_title}
        </p>

        <p className="card-text">
          <strong>Lección:</strong> {progress.lesson_title}
        </p>

        <p className="card-text">
          <strong>Estado:</strong>{" "}
          {progress.completed ? "Completada ✅" : "En progreso ⏳"}
        </p>

        {progress.progress_percentage !== undefined && (
          <div className="progress mt-2">
            <div
              className="progress-bar bg-success"
              role="progressbar"
              style={{ width: `${progress.progress_percentage}%` }}
            >
              {progress.progress_percentage}%
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export const MyProgress = () => {
  const { store, dispatch } = useGlobalReducer();
  const progressList = store.my_progress || [];

  useEffect(() => {
    const getProgress = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/api/progress`,
          {
            headers: {
              Authorization: `Bearer ${store.token}`,
            },
          }
        );

        if (!res.ok) {
          const text = await res.text();
          console.error("Respuesta backend NO JSON:", text);
          dispatch({ type: "set_my_progress", payload: [] });
          return;
        }

        const data = await res.json();

        const arrayData = Array.isArray(data)
          ? data
          : data.progress || data.results || [];

        dispatch({ type: "set_my_progress", payload: arrayData });

      } catch (error) {
        console.error("Error cargando progreso:", error);
        dispatch({ type: "set_my_progress", payload: [] });
      }
    };

    if (store.isLogged) {
      getProgress();
    }
  }, [store.isLogged, store.token, dispatch]);

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver tu progreso</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Mi Progreso</h1>

      {progressList.length === 0 ? (
        <p className="text-center">Aún no tienes progreso registrado</p>
      ) : (
        progressList.map((item, index) => (
          <ProgressCard key={item.progress_id || index} progress={item} />
        ))
      )}
    </div>
  );
};
