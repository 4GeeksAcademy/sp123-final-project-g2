import { useState } from "react";

export const ModuleForm = ({ courseId, onSubmit }) => {
  const [title, setTitle] = useState("");

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit({ title, course_id: courseId });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 shadow">
      <h4>Nuevo módulo</h4>

      <div className="mb-3">
        <label className="form-label">Título del módulo</label>
        <input
          type="text"
          className="form-control"
          value={title}
          onChange={e => setTitle(e.target.value)}
          required
        />
      </div>

      <button className="btn btn-success w-100">
        Crear módulo
      </button>
    </form>
  );
};
