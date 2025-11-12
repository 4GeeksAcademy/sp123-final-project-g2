import React, { useEffect, useState } from 'react'
import { user } from '../jsApiComponents/user'
import { useNavigate } from 'react-router-dom'
import HandleError from '../components/HandleError'
export default function User() {
  const [userInfo, setUserInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errorCode, setErrorCode] = useState(null);
  const nav = useNavigate()


  const handleSubmit = (e) =>{
    e.preventDefault()
  }

  useEffect(() => {
    const infoUser = async () => {
      const data = await user()
      console.log(data)
      if (data.status == 422) {
        alert('Algo ha salido mal!')
        nav('/login')
      }
      if (data.status == 401) {
        alert('Para entrar aqui, debes estar registrado / iniciar sesion!')
        nav('/login')
      }
      setUserInfo(data.data)
      setLoading(false)

    }

    infoUser()
  }, [])
  // Simbolo de carga
  if (loading) return <p>Cargando...

    <button onClick={() => {
      return console.log(errorCode);
    }}>Ver errorCode</button></p>
  // Manejo errores 


  return (
    <div>
      <button onClick={() => {
        return console.log(userInfo)
      }}>ver que trae user</button>
      User
      <div>
{/*         
        <button onClick={() => {
          return nav('/login')
        }}>ir a login</button> */}
      </div>



      <div className="auth-theme">
        <div className="auth-shell">
          <div className="auth-card">
            <div className="auth-title"><h3>Profile</h3></div>
            <div className="auth-title">
              <h1>aqui va la Foto de perfil</h1>
              <p><button>Cambiar foto de perfil</button></p>
            </div>
            <div className="auth-sub">
              

              <form onSubmit={handleSubmit} className='form-control '>
                <input type="text" id = "Nombre"/>
                <label className='form-label input-dark' ></label>
              </form>


              <h5>Nombre</h5>
              <h5>Apellidos</h5>
              <h5>Ubicacion</h5>
              <h5>Numero de Telefono</h5>
              

            </div>

          </div>
        </div>
      </div>
      );
    </div>

  )
}
