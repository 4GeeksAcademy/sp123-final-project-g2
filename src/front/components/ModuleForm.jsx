import { useState } from "react";

export const ModuleForm = ({ courseId, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: "",
    order: "",
    points: ""
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      ...formData,
      order: parseInt(formData.order),
      points: parseInt(formData.points),
      course_id: courseId
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 shadow">
      <h4>Crear Módulo</h4>

      <div className="mb-3">
        <label>Título</label>
        <input
          type="text"
          name="title"
          className="form-control"
          value={formData.title}
          onChange={handleChange}
          required
        />
      </div>

      <div className="mb-3">
        <label>Orden</label>
        <input
          type="number"
          name="order"
          className="form-control"
          value={formData.order}
          onChange={handleChange}
          required
        />
      </div>

      <div className="mb-3">
        <label>Puntos del módulo</label>
        <input
          type="number"
          name="points"
          className="form-control"
          value={formData.points}
          onChange={handleChange}
          required
        />
      </div>

      <button className="btn btn-success w-100">
        Guardar Módulo
      </button>
    </form>
  );
};
