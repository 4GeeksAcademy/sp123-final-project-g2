import { useEffect, useState } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { useNavigate } from "react-router-dom";
import { LessonCard } from "../components/LessonCard.jsx";
import { useLocation } from "react-router-dom";
import { LessonForm } from "../components/LessonForm.jsx";
 
 
const apiFetchJson = (url, options) => {
  return fetch(url, options).then((res) =>
    res
      .json()
      .catch(() => null)
      .then((data) => ({ ok: res.ok, status: res.status, data }))
  );
};
 
const filterLessonsByModule = (lessons, moduleId) => {
  if (!moduleId) return lessons;
  return lessons.filter(l => String(l.module_id) === String(moduleId));
};
 
const normalizeLessons = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.lessons)) return payload.lessons;
  if (payload && Array.isArray(payload.data)) return payload.data;
  return [];
};
 
 
export const Lessons = () => {
  const { store } = useGlobalReducer();
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();
 
  if (!store.isLogged) {
    return (
      <div className="container mt-4 text-center">
        <h4>Debes iniciar sesión para ver el dashboard</h4>
      </div>
    );
  }
 
  const user = store.current_user || {};
  const role = String(user.role || "student").toLowerCase().trim();
  const isAdmin = role === "admin";
  const isTeacher = role === "teacher" || role === "tacher";
 
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const moduleId = params.get("module_id");
 
 
  const base = (import.meta.env.VITE_BACKEND_URL || "").replace(/\/$/, "");
  const endpoint = `${base}/api/lessons-private`;
 
 
  const loadLessons = async () => {
    setLoading(true);
    setErrorMsg("");
 
    apiFetchJson(endpoint, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${store.token}`,
      },
    })
      .then(({ ok, status, data }) => {
        if (!ok) {
          setLessons([]);
 
          if (status === 401 || status === 422) {
            setErrorMsg("Token inválido o expirado. Vuelve a iniciar sesión.");
            return;
          }
          if (status === 403) {
            setErrorMsg(
              data?.msg ||
              "Acceso denegado (403). Revisa CORS/permisos del backend para este endpoint."
            );
            return;
          }
 
          setErrorMsg(data?.msg || "Error cargando lecciones.");
          return;
        }
        if (data?.count === 0) {
          setLessons([]);
          setErrorMsg("No se encontraron lecciones para este módulo.");
          return;
        }
 
        let normalized = normalizeLessons(data.results);
        console.log("Normalized lessons:", normalized);
        setLessons(filterLessonsByModule(normalized, moduleId));
      })
      .catch(() => {
        setLessons([]);
        setErrorMsg("No se pudo conectar con el servidor.");
      })
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    loadLessons();
  }, [moduleId]);
 
  if (!moduleId) {
    return (
      <div className="container mt-4 text-center">
        <h4>Selecciona un módulo para ver las lecciones</h4>
      </div>
    );
  }
 
  const [showForm, setShowForm] = useState(false);
 
  return (
    <div className="container mt-4">
 
      <h2 className="text-center mb-4">Lecciones</h2>
 
      <hr />
 
      <div className="row">
        {lessons.length === 0 ? (
          <p className="text-center text-muted">
            Aún no hay lecciones en este módulo
          </p>
        ) : (
          lessons.map(lesson => (
            <LessonCard
              key={lesson.lesson_id}
              lesson={lesson}
            />
          ))
        )}
      </div>
 
      {(isAdmin || isTeacher) && (
        <>
          <button
            className="btn btn-primary mt-4"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? "Cancelar" : "Añadir lecciones"}
          </button>
          {showForm && (
            <LessonForm
              moduleId={moduleId}
              onSubmit={async (data) => {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/lessons-private`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${store.token}`
                  },
                  body: JSON.stringify({
                    ...data,
                    module_id: moduleId
                  })
                });
 
                if (response.ok) {
                  setShowForm(false);
                  await loadLessons();
                } else {
                  const errorData = await response.json();
                  alert("Error al crear la lección: " + (errorData?.msg || "Error desconocido"));
                }
              }}
            />
          )}
        </>
      )}
 
    </div>
  );
};
 
 