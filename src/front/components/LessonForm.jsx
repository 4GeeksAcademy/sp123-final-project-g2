import { useState } from "react";

export const LessonForm = ({ moduleId, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    learning_objective: "",
    signs_taught: "",
    order: "",
    trial_visible: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      ...formData,
      order: parseInt(formData.order),
      module_id: moduleId
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 shadow">
      <h4>Crear Lección</h4>

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
        <label>Contenido</label>
        <textarea
          name="content"
          className="form-control"
          value={formData.content}
          onChange={handleChange}
          required
        />
      </div>

      <div className="mb-3">
        <label>Objetivo de aprendizaje</label>
        <input
          type="text"
          name="learning_objective"
          className="form-control"
          value={formData.learning_objective}
          onChange={handleChange}
        />
      </div>

      <div className="mb-3">
        <label>Señas enseñadas</label>
        <input
          type="text"
          name="signs_taught"
          className="form-control"
          value={formData.signs_taught}
          onChange={handleChange}
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

      <div className="form-check mb-3">
        <input
          type="checkbox"
          name="trial_visible"
          className="form-check-input"
          checked={formData.trial_visible}
          onChange={handleChange}
        />
        <label className="form-check-label">
          Visible en modo prueba
        </label>
      </div>

      <button className="btn btn-warning w-100">
        Guardar Lección
      </button>
    </form>
  );
};
