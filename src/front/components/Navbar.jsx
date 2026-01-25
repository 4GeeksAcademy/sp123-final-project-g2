import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {

	const { store, dispatch } = useGlobalReducer();
	const navigate = useNavigate();

	const handleRegistro = () => {
		navigate('/signup')
	}

	const handleLogin = () => {

		if (store.isLogged) {
			localStorage.removeItem('token')

			dispatch({ type: 'handle_token', payload: '' })
			dispatch({ type: 'handle_user', payload: {} })
			dispatch({ type: 'handle_isLogged', payload: false })

			navigate('/')
		} else {
			dispatch({
				type: 'handle_alert',
				payload: {
					text: '',
					color: '',
					display: false
				}
			})

			navigate('/login')
		}
	}

	return (
		<nav className="navbar navbar-light bg-light">
			<div className="container">
				<Link to="/">
					<span className="navbar-brand mb-0 h1">React Boilerplate</span>
				</Link>

				<div className="ml-auto">
					<Link to="/demo">
						<button className="btn btn-primary">
							Check the Context in action
						</button>
					</Link>

					<span onClick={handleLogin} className='btn btn-warning ms-2'>
						{store.isLogged ? 'Logout' :'Login'}
					</span>

					{!store.isLogged && (
						<span onClick={handleRegistro} className='btn btn-warning ms-2'>
							Registro
						</span>
					)}
				</div>
			</div>
		</nav>
	);
};