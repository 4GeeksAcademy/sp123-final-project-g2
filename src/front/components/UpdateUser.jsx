
import { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import useGlobalReducer from '../hooks/useGlobalReducer';
import { user } from '../jsApiComponents/user';
import { updateUser } from '../jsApiComponents/auth';
import { Button } from 'react-bootstrap';
export default function UpdateUser() {
    const [info, setInfo] = useState({ bio: "", sports: "", level: "", lastName: "" })
    const [errors, setErrors] = useState({});
    const userID = localStorage.getItem('USER')

    const navigate = useNavigate()

    const updateSuccess = async (e) => {
        e.preventDefault()
        const body = {
            "lastname": info.lastName,
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
            navigate('/user')
        }
    }



    const recoverBio = (e) => {
        setInfo({...info, bio: e.target.value})
    }
    const recoverLevel = (e) => {
        setInfo({...info, level: e.target.value})
    }
    const recoverSport = (e) => {
        setInfo({...info, sports: e.target.value})
    }
    const recoverName = (e) => {
        setInfo({...info, name: e.target.value})
    }
    const recoverLastname = (e) => {
        setInfo({...info, lastName: e.target.value})
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
            <div className="dropdown" style={{minWidth: "300px"}}>
                <form className="dropdown-menu p-4 m-2 form-register" onSubmit={updateSuccess}>
                    <div className="mb-3 ">
                        <label htmlFor="bio" className='form-label'><h4>Bio</h4></label>
                        <input type="text" placeholder='Hola soy Sergio...' id='bio' className='form-control' onChange={recoverBio} />
                    </div>
                    <div className="mb-3 ">
                        <label htmlFor="deporte" className='form-label'><h4>Deporte</h4></label>
                        <input type="text" placeholder='Correr, Tenis, Futbol...' id='deporte' className='form-control' onChange={recoverSport} />
                    </div>
                    <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Nivel</h4></label>
                        <input type="text" placeholder='Principante, intermedio...' id='nivel' className='form-control' onChange={recoverLevel} />
                    </div>
                    {/* <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Nombre</h4></label>
                        <input type="text" placeholder='Sergio' id='nivel' className='form-control' onChange={recoverName} />
                    </div> */}
                    <div className="mb-3 ">
                        <label htmlFor="nivel" className='form-label'><h4>Apellidos</h4></label>
                        <input type="text" placeholder='Alvarez Lopez...' id='nivel' className='form-control' onChange={recoverLastname} />
                    </div>
                    <button type='submit' className='btn btn-success mt-1'>Enviar</button>
                </form>
            </div>
        </>
    )
}