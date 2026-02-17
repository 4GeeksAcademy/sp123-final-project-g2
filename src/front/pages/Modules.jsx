import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { ModuleCard } from "../components/ModuleCard.jsx";
import { useLocation } from "react-router-dom";
 
 
const normalizeModules = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.modules)) return payload.modules;
  if (payload && Array.isArray(payload.data)) return payload.data;
  return [];
};
 
const apiFetchJson = (url, options) => {
  return fetch(url, options).then((res) =>
    res
      .json()
      .catch(() => null)
      .then((data) => ({ ok: res.ok, status: res.status, data }))
  );
};
 
const filterModulesByCourse = (modules, courseId) => {
  if (!courseId) return modules;
  return modules.filter(m => String(m.course_id) === String(courseId));
};
 
 
export const Modules = () => {
  const { store, dispatch } = useGlobalReducer();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();
 
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const courseId = params.get("course_id");
 
  const base = (import.meta.env.VITE_BACKEND_URL || "").replace(/\/$/, "");
  const endpoint = `${base}/api/modules-private`;
 
  const loadModules = () => {
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
          setModules([]);
 
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
 
          setErrorMsg(data?.msg || "Error cargando módulos.");
          return;
        }
        if (data?.count === 0) {
          setModules([]);
          setErrorMsg("No se encontraron módulos para este usuario.");
          return;
        }
 
        let normalized = normalizeModules(data.results);
        setModules(filterModulesByCourse(normalized, courseId));
      })
      .catch(() => {
        setModules([]);
        setErrorMsg("No se pudo conectar con el servidor.");
      })
      .finally(() => setLoading(false));
  };
 
  const handleLessons = (module) => {
    dispatch({ type: "module_details", payload: module });
    navigate('/lessons?module_id=' + module.module_id);
  };
 
  useEffect(() => {
    // getModules();
    if (store.isLogged && store.token) loadModules();
  }, [courseId]);
 
  if (!courseId) return <h4 className="text-center mt-4">Selecciona un curso</h4>;
 
  return (
    <div className="container mt-4">
      <h2 className="text-center">Modules</h2>
 
      <div className="row">
        {modules.map(module => (
          <ModuleCard
            key={module.module_id}
            module={module}
            onLessons={handleLessons}
          />
        ))}
      </div>
    </div>
  );
};
 
 