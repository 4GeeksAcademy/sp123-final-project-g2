import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";


export const Lessons = () => {
  const { store } = useGlobalReducer();
  const [lessons, setLessons] = useState([]);

  const courseId = store.course_details?.course_id;

  const getLessons = async () => {
    if (!courseId) return;

    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/courses/${courseId}/lessons`
    );

    const data = await res.json();
    setLessons(data);
  };

  useEffect(() => {
    getLessons();
  }, [courseId]);

  if (!courseId) {
    return (
      <div className="container mt-4 text-center">
        <h4>Selecciona un curso primero</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h2 className="text-center">Lessons</h2>

      <div className="row">
        {lessons.map(lesson => (
          <LessonCard key={lesson.lesson_id} lesson={lesson} />
        ))}
      </div>
    </div>
  );
};
