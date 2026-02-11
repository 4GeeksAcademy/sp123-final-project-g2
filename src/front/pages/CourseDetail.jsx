import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ModuleForm } from "../components/ModuleForm";

export const CourseDetail = () => {
  const { courseId } = useParams();
  const [modules, setModules] = useState([]);

  const getModules = async () => {
    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/courses/${courseId}/modules`
    );
    const data = await res.json();
    setModules(data);
  };

  useEffect(() => {
    getModules();
  }, []);

  return (
    <div className="container mt-4">
      <h2>Módulos</h2>

      <ModuleForm
        courseId={courseId}
        onSubmit={async (data) => {
          await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/modules`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
          });
          getModules();
        }}
      />

      <ul className="list-group mt-3">
        {modules.map(m => (
          <li key={m.module_id} className="list-group-item">
            {m.title}
          </li>
        ))}
      </ul>
    </div>
  );
};
