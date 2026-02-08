import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { CourseCard } from "../components/CourseCard.jsx";

export const Courses = () => {
  const { store, dispatch } = useGlobalReducer();
  const [courses, setCourses] = useState([]);
  const navigate = useNavigate();

  const getCourses = async () => {
    const response = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/courses`
    );
    const data = await response.json();
    setCourses(data);
  };

  const handleDetails = (course) => {
    dispatch({ type: "course_details", payload: course });
    navigate("/lessons");
  };

  useEffect(() => {
    dispatch({ type: "course_details", payload: {} });
    getCourses();
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="text-center">Courses</h1>

      <div className="row">
        {courses.map(course => (
          <CourseCard
            key={course.course_id}
            course={course}
            onDetails={handleDetails}
          />
        ))}
      </div>
    </div>
  );
};
