import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

export const LessonCard = ({ lesson }) => {
  const { store } = useGlobalReducer();

  const markCompleted = async () => {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`
      },
      body: JSON.stringify({
        lesson_id: lesson.lesson_id,
        completed: true
      })
    });
  };

  return (
    <div className="col-md-4">
      <div className="card mb-3 shadow">
        <div className="card-body">
          <h5>{lesson.title}</h5>

          <button
            className="btn btn-success"
            onClick={markCompleted}
          >
            Marcar como completada
          </button>
        </div>
      </div>
    </div>
  );
};
