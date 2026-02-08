import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {
	const { store, dispatch } = useGlobalReducer();
	const navigate = useNavigate();

	const handleRegistro = () => {
		navigate("/signup");
	};

	const handleLogin = () => {
		if (store.isLogged) {
			// Logout
			localStorage.removeItem("token");

			dispatch({ type: "handle_token", payload: "" });
			dispatch({ type: "handle_user", payload: {} });
			dispatch({ type: "handle_isLogged", payload: false });

			navigate("/");
		} else {
			// Login
			dispatch({
				type: "handle_alert",
				payload: {
					text: "",
					color: "",
					display: false
				}
			});
			navigate("/login");
		}
	};

	return (
		<nav className="navbar navbar-light bg-light px-3">
			
			{/* LEFT MENU */}
			<ul className="navbar-nav flex-row gap-3">
				{store.isLogged && (
					<>
						<li className="nav-item">
							<Link className="nav-link" to="/courses">
								Cursos
							</Link>
						</li>

						<li className="nav-item">
							<Link className="nav-link" to="/dashboard">
								Mi progreso
							</Link>
						</li>

						<li className="nav-item">
							<Link className="nav-link" to="/achievements">
								Logros
							</Link>
						</li>
					</>
				)}
			</ul>

			{/* BRAND */}
			<Link to="/" className="navbar-brand mx-auto">
				React Boilerplate
			</Link>

			{/* RIGHT ACTIONS */}
			<div className="d-flex align-items-center">
				<span
					onClick={handleLogin}
					className="btn btn-warning ms-2"
					style={{ cursor: "pointer" }}
				>
					{store.isLogged ? "Logout" : "Login"}
				</span>

				{!store.isLogged && (
					<span
						onClick={handleRegistro}
						className="btn btn-warning ms-2"
						style={{ cursor: "pointer" }}
					>
						Registro
					</span>
				)}
			</div>

		</nav>
	);
};
