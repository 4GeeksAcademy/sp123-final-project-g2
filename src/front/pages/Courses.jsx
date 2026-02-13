import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Courses = () => {
  const { store } = useGlobalReducer();
  const [courses, setCourses] = useState([]);

  const getCourses = async () => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/courses-private`,
        {
          headers: {
            Authorization: `Bearer ${store.token}`
          }
        }
      );

      if (!res.ok) {
        console.error("Error cargando cursos privados");
        return;
      }

      const data = await res.json();
      setCourses(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    if (store.isLogged) {
      getCourses();
    }
  }, [store.isLogged]);

  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver tus cursos</h4>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Mis Cursos</h1>

      {courses.length === 0 ? (
        <p className="text-center">No tienes cursos creados aún.</p>
      ) : (
        <div className="row">
          {courses.map((course) => (
            <div key={course.id} className="col-md-4 mb-3">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h5 className="card-title">{course.title}</h5>
                  <p className="card-text">{course.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
