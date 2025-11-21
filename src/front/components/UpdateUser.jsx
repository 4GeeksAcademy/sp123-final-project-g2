
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import useGlobalReducer from '../hooks/useGlobalReducer';
import { user } from '../jsApiComponents/user';
import { updateUser } from '../jsApiComponents/auth';
import { Button } from 'react-bootstrap';
export default function UpdateUser({ refreshUser ,user_bio, user_sports, user_level, user_lastname }) {
    const [info, setInfo] = useState({ bio: "", sports: "", level: "", lastname: "" })
    const [errors, setErrors] = useState({});
    const userID = localStorage.getItem('USER')

    const navigate = useNavigate()

    const updateSuccess = async (e) => {
        e.preventDefault()
        const body = {
            "lastname": info.lastname,
            "bio": info.bio,
            "sports": info.sports,
            "level": info.level,
        }
        e.preventDefault();

        const data = await updateUser(body, userID)
        if (data.status == 400) {
            alert('Algo ha salido mal!')
        }
        if (data.status == 200) {
            alert('Has actualizado la info correctamente!')
            refreshUser()
            navigate('/profile')
        }
    }

    // const getUserInfo = () => {
        

    // }

    useEffect(() => {
        setInfo({ bio: user_bio, sports: user_sports, level: user_level, lastname: user_lastname })
    }, [user_bio, user_sports, user_level, user_lastname])




    const recoverBio = (e) => {
        setInfo({ ...info, bio: e.target.value })
    }
    const recoverLevel = (e) => {
        setInfo({ ...info, level: e.target.value })
    }
    const recoverSport = (e) => {
        setInfo({ ...info, sports: e.target.value })
    }
    const recoverName = (e) => {
        setInfo({ ...info, name: e.target.value })
    }
    const recoverLastname = (e) => {
        setInfo({ ...info, lastname: e.target.value })
    }
    return (
        <>

            <Button
                type='button'
                className="btn btn-warning dropdown-toggle btn-success"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                data-bs-auto-close="outside"
            >
                Editar Perfil
            </Button>
            <div className="dropdown" style={{ minWidth: "300px" }}>
                <form className="dropdown-menu p-4 m-2 form-register" onSubmit={updateSuccess}>
                    <div className="mb-3 ">
                        <label htmlFor="bio" className='form-label'><h4>Bio</h4></label>
                        <input type="text" placeholder='Hola soy Sergio...' id='bio' className='form-control' value={info.bio} onChange={recoverBio} />
                    </div>
                    <div className="mb-3 ">
                        <label htmlFor="deporte" className='form-label'><h4>Deporte</h4></label>
                        <input type="text" placeholder='Correr, Tenis, Futbol...' id='deporte' className='form-control' value={info.sports} onChange={recoverSport} />
                    </div>
                    <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Nivel</h4></label>
                        <input type="text" placeholder='Principante, intermedio...' id='nivel' className='form-control' value={info.level} onChange={recoverLevel} />
                    </div>
                    {/* <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Nombre</h4></label>
                        <input type="text" placeholder='Sergio' id='nivel' className='form-control' onChange={recoverName} />
                    </div> */}
                    <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Apellidos</h4></label>
                        <input type="text" placeholder='Alvarez Lopez...' id='nivel' className='form-control' value={info.lastname} onChange={recoverLastname} />
                    </div>
                    <button type='submit' className='btn btn-success mt-1'>Enviar</button>
                </form>
            </div>
        </>
    )
}