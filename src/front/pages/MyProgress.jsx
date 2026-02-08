import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { ProgressCard } from "../components/ProgressCard.jsx";

export const MyProgress = () => {
  const { store } = useGlobalReducer();
  const [progress, setProgress] = useState([]);

  const getProgress = async () => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/progress`,
        {
          headers: {
            Authorization: `Bearer ${store.token}`
          }
        }
      );

      if (!res.ok) {
        const text = await res.text();
        console.error("Respuesta backend NO JSON:", text);
        return;
      }

      const data = await res.json();
      setProgress(data);

    } catch (error) {
      console.error("Error cargando progreso:", error);
    }
  };

  useEffect(() => {
    if (store.isLogged) {
      getProgress();
    }
  }, [store.isLogged]);

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver tu progreso</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h2 className="text-center mb-4">Mi Progreso</h2>

      <div className="row">
        {progress.length === 0 ? (
          <p className="text-center">Aún no tienes progreso registrado</p>
        ) : (
          progress.map((item) => (
            <ProgressCard key={item.progress_id} progress={item} />
          ))
        )}
      </div>
    </div>
  );
};
