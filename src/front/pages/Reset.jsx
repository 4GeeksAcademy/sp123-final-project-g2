import { useState } from "react";
import { useNavigate, Link, useParams } from "react-router-dom";
import AuthShell from "../components/AuthShell";
import TextInput from "../components/TextInput";
const BASE_URL = import.meta.env.VITE_BACKEND_URL
export function Reset() {
  const nav = useNavigate();
  const [p1, setP1] = useState("");
  const [p2, setP2] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const { token } = useParams()


  const submit = async (e) => {
    e.preventDefault();
    setErr("");

    if (p1.length < 8) return setErr("La nueva contraseña debe tener al menos 8 caracteres.");
    if (p1 !== p2) return setErr("Las contraseñas no coinciden.");

    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/api/reset/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          password: p1,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        return setErr(data.error || "Error inesperado al cambiar la contraseña.");
      }

      nav("/login");
    } catch (error) {
      setErr("Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      title="Cambiar contraseña"
      subtitle="Introduce tu contraseña actual y define una nueva"
    >
      <form onSubmit={submit} noValidate>

        <TextInput
          label="Nueva contraseña"
          name="p1"
          value={p1}
          onChange={(e) => setP1(e.target.value)}
          withToggle
          placeholder="••••••••"
        />
        <TextInput
          label="Repite la nueva contraseña"
          name="p2"
          value={p2}
          onChange={(e) => setP2(e.target.value)}
          withToggle
          placeholder="••••••••"
        />

        {err && <div className="alert alert-danger py-2">{err}</div>}

        <button className="btn btn-accent w-100" disabled={loading}>
          {loading ? "Procesando..." : "Cambiar contraseña"}
        </button>
      </form>

      <div className="text-center mt-3">
        <Link to="/profile" className="link-accent">Volver al perfil</Link>
      </div>
    </AuthShell>
  );
}