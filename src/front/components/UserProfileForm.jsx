import { useState } from "react";

export const UserProfileForm = ({ user, onUpdate, onDelete }) => {
  const [firstName, setFirstName] = useState(user.first_name);
  const [email, setEmail] = useState(user.email);

  const handleSubmit = e => {
    e.preventDefault();
    onUpdate({ first_name: firstName, email });
  };

  return (
    <div className="card p-4 shadow">
      <h4>Perfil de usuario</h4>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Nombre</label>
          <input
            className="form-control"
            value={firstName}
            onChange={e => setFirstName(e.target.value)}
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Email</label>
          <input
            type="email"
            className="form-control"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>

        <button className="btn btn-primary w-100 mb-2">
          Guardar cambios
        </button>
      </form>

      <button
        className="btn btn-danger w-100"
        onClick={onDelete}
      >
        Eliminar cuenta
      </button>
    </div>
  );
};
