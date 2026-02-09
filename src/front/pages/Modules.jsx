import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { ModuleCard } from "../components/ModuleCard.jsx";

export const Modules = () => {
  const { store, dispatch } = useGlobalReducer();
  const [modules, setModules] = useState([]);
  const navigate = useNavigate();

  const courseId = store.course_details?.course_id;

  const getModules = async () => {
    if (!courseId) return;

    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/courses/${courseId}/modules`
    );
    const data = await res.json();
    setModules(data);
  };

  const handleLessons = (module) => {
    dispatch({ type: "module_details", payload: module });
    navigate("/lessons");
  };

  useEffect(() => {
    getModules();
  }, [courseId]);

  if (!courseId) return <h4 className="text-center mt-4">Selecciona un curso</h4>;

  return (
    <div className="container mt-4">
      <h2 className="text-center">Modules</h2>

      <div className="row">
        {modules.map(module => (
          <ModuleCard
            key={module.module_id}
            module={module}
            onLessons={handleLessons}
          />
        ))}
      </div>
    </div>
  );
};
