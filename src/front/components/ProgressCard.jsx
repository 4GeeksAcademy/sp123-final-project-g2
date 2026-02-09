export const ProgressCard = ({ progress }) => {
  return (
    <div className="col-md-4">
      <div className="card mb-3 shadow">
        <div className="card-body">
          <h5>{progress.lesson_title}</h5>
          <p><strong>Módulo:</strong> {progress.module_title}</p>
          <p><strong>Curso:</strong> {progress.course_title}</p>
          <p><strong>Completado:</strong> {progress.completed ? "Sí" : "No"}</p>
          <p><strong>Fecha inicio:</strong> {progress.start_date || "-"}</p>
          <p><strong>Fecha completado:</strong> {progress.completion_date || "-"}</p>
        </div>
      </div>
    </div>
  );
};
