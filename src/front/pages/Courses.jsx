import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";
import { CourseCard } from "../components/CourseCard";
import { CourseForm } from "../components/CourseForm";

export const Courses = () => {
  const { store } = useGlobalReducer();
  const [courses, setCourses] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const getCourses = async () => {
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/courses`);
    const data = await res.json();
    setCourses(data);
  };

  const handleCreateCourse = async (courseData) => {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/courses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`
      },
      body: JSON.stringify(courseData)
    });

    setShowForm(false);
    getCourses();
  };

  useEffect(() => {
    getCourses();
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Cursos</h1>

      {store.isLogged && (
        <button
          className="btn btn-primary mb-3"
          onClick={() => setShowForm(!showForm)}
        >
          ➕ Crear curso
        </button>
      )}

      {showForm && <CourseForm onSubmit={handleCreateCourse} />}

      <div className="row mt-4">
        {courses.map(course => (
          <CourseCard key={course.course_id} course={course} />
        ))}
      </div>
    </div>
  );
};
