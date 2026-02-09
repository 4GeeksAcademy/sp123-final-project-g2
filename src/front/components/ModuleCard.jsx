export const ModuleCard = ({ module, onLessons }) => (
  <div className="col-md-4">
    <div className="card mb-3 shadow">
      <div className="card-body">
        <h5>{module.title}</h5>
        <p>Puntos: {module.points}</p>

        <button
          className="btn btn-secondary"
          onClick={() => onLessons(module)}
        >
          Ver lecciones
        </button>
      </div>
    </div>
  </div>
);
