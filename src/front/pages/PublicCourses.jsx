import { useEffect, useState } from "react";

export const PublicCourses = () => {
  const [courses, setCourses] = useState([]);

  const getPublicCourses = async () => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/courses-public`
      );

      const data = await res.json();
      setCourses(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando cursos públicos:", error);
    }
  };

  useEffect(() => {
    getPublicCourses();
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">Cursos Disponibles</h1>

      {courses.length === 0 ? (
        <p className="text-center">No hay cursos disponibles.</p>
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
