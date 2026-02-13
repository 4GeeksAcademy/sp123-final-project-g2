import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { LessonCard } from "../components/LessonCard.jsx";
import { LessonForm } from "../components/LessonForm.jsx";

export const Lessons = () => {
  const { store } = useGlobalReducer();
  const [lessons, setLessons] = useState([]);

  // Este id viene del curso o módulo seleccionado previamente
  const moduleId = store.module_details?.module_id;

  const getLessons = async () => {
    if (!moduleId) return;

    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/modules/${moduleId}/lessons`
    );

    const data = await res.json();
    setLessons(data);
  };

  useEffect(() => {
    getLessons();
  }, [moduleId]);

  if (!moduleId) {
    return (
      <div className="container mt-4 text-center">
        <h4>Selecciona un módulo para ver las lecciones</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">

      <h2 className="text-center mb-4">Lecciones</h2>

      <LessonForm
        moduleId={moduleId}
        onSubmit={async (data) => {
          await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/lessons`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              ...data,
              module_id: moduleId
            })
          });

          getLessons(); // refresca la lista
        }}
      />

      <hr />

      <div className="row">
        {lessons.length === 0 ? (
          <p className="text-center text-muted">
            Aún no hay lecciones en este módulo
          </p>
        ) : (
          lessons.map(lesson => (
            <LessonCard
              key={lesson.lesson_id}
              lesson={lesson}
            />
          ))
        )}
      </div>

    </div>
  );
};
