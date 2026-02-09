import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { MultimediaResource } from "../components/MultimediaResource.jsx";

export const LessonDetails = () => {
  const { store } = useGlobalReducer();
  const [resources, setResources] = useState([]);

  const lessonId = store.lesson_details?.lesson_id;

  const getResources = async () => {
    if (!lessonId) return;

    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/lessons/${lessonId}/resources`
    );
    const data = await res.json();
    setResources(data);
  };

  useEffect(() => {
    getResources();
  }, [lessonId]);

  if (!lessonId) return <h4 className="text-center mt-4">Selecciona una lección</h4>;

  return (
    <div className="container mt-4">
      <h2>{store.lesson_details.title}</h2>

      {resources.map(resource => (
        <MultimediaResource key={resource.resource_id} resource={resource} />
      ))}
    </div>
  );
};
