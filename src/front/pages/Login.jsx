import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";
import { login } from "../services/auth.js";

export const Login = () => {
  const { dispatch } = useGlobalReducer();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      dispatch({
        type: "handle_alert",
        payload: {
          text: "Introduce email y contraseña",
          color: "danger",
          display: true,
        },
      });
      return;
    }

    setLoading(true);

    const result = await login({ email, password });

    setLoading(false);

    if (!result || !result.access_token) {
      dispatch({
        type: "handle_alert",
        payload: {
          text: "Email o contraseña incorrectos",
          color: "danger",
          display: true,
        },
      });
      return;
    }
    

    localStorage.setItem("token", result.access_token);
    dispatch({ type: "handle_token", payload: result.access_token });
    dispatch({ type: "handle_user", payload: result.results });
    dispatch({ type: "handle_isLogged", payload: true });

    navigate("/dashboard");
  };

  return (
    <div style={styles.page}>
      {/* Fondo */}
      <div style={styles.bgImage}></div>
      <div style={styles.overlay}></div>

      {/* Logo */}
      <div style={styles.logo}>
        <span style={styles.logoPlus}>+</span>
        <span style={styles.logoText}>vocal</span>
      </div>

      {/* Card */}
      <div style={styles.card}>
        <h2 style={styles.title}>Accede a tu área</h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            placeholder="Usuario"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
          />

          {/* Password con icono Bootstrap */}
          <div style={{ position: "relative", width: "100%" }}>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
            />

            <i
              className={`bi ${
                showPassword ? "bi-eye-slash-fill" : "bi-eye-fill"
              }`}
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: "15px",
                top: "50%",
                transform: "translateY(-50%)",
                cursor: "pointer",
                fontSize: "18px",
                color: "#555",
              }}
            ></i>
          </div>

          <button
            type="submit"
            style={{
              ...styles.button,
              opacity: loading ? 0.7 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            disabled={loading}
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
};


const styles = {
  page: {
    minHeight: "100vh",
    width: "100%",
    position: "relative",
    display: "flex",
    justifyContent: "flex-end",
    alignItems: "center",
    paddingRight: "8%",
    fontFamily:
      "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    overflow: "hidden",
  },

  // ✅ Imagen REAL (no página de Unsplash)
  bgImage: {
    position: "absolute",
    inset: 0,
    backgroundImage:
      "url('https://images.unsplash.com/photo-1456428199391-a3b1cb5e93ab?auto=format&fit=crop&w=1920&q=80')",
    backgroundSize: "cover",
    backgroundPosition: "center",
    filter: "blur(2px)",
    transform: "scale(1.02)",
    zIndex: -2,
    pointerEvents: "none", 
  },

  overlay: {
    position: "absolute",
    inset: 0,
    background: "rgba(255,255,255,0.78)",
    zIndex: -1,
    pointerEvents: "none", // 🔥 evita bloquear clicks
  },

  logo: {
    position: "absolute",
    top: "60px",
    right: "8%",
    display: "flex",
    alignItems: "baseline",
    gap: "10px",
    color: "#2f36ff",
    fontWeight: 800,
  },

  logoPlus: {
    fontSize: "56px",
  },

  logoText: {
    fontSize: "84px",
    letterSpacing: "-1px",
  },

  card: {
    width: "420px",
    background: "#ffffff",
    borderRadius: "22px",
    padding: "42px",
    boxShadow: "0 24px 60px rgba(0,0,0,0.12)",
  },

  title: {
    textAlign: "center",
    fontSize: "26px",
    fontWeight: 500,
    marginBottom: "26px",
  },

  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },

  input: {
    height: "50px",
    borderRadius: "8px",
    border: "1px solid #d1d1d1",
    padding: "0 14px",
    fontSize: "16px",
  },

  forgot: {
    textAlign: "right",
    fontSize: "14px",
    color: "#2f36ff",
    cursor: "pointer",
  },

  button: {
    marginTop: "10px",
    height: "52px",
    borderRadius: "999px",
    border: "none",
    background: "#2f36ff",
    color: "#fff",
    fontSize: "18px",
  },
};
