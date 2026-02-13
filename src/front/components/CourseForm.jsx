import { useState } from "react";

export const CourseForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    points: "",
    is_active: true
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
      price: parseFloat(formData.price),
      points: parseInt(formData.points)
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4 shadow">
      <h4>Crear Curso</h4>

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
        <label>Descripción</label>
        <textarea
          name="description"
          className="form-control"
          value={formData.description}
          onChange={handleChange}
          required
        />
      </div>

      <div className="mb-3">
        <label>Precio</label>
        <input
          type="number"
          name="price"
          className="form-control"
          value={formData.price}
          onChange={handleChange}
          required
        />
      </div>

      <div className="mb-3">
        <label>Puntos que otorga</label>
        <input
          type="number"
          name="points"
          className="form-control"
          value={formData.points}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-check mb-3">
        <input
          type="checkbox"
          name="is_active"
          className="form-check-input"
          checked={formData.is_active}
          onChange={handleChange}
        />
        <label className="form-check-label">
          Curso activo
        </label>
      </div>

      <button className="btn btn-primary w-100">
        Guardar Curso
      </button>
    </form>
  );
};
