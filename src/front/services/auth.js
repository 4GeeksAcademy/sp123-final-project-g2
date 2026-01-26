import { Await } from "react-router-dom"

let HOSTFINAL = import.meta.env.VITE_BACKEND_URL
 
export const login = async (dataToSend) => {
    //Envair el email y pass al  back para recibir el token o no ...
    console.log(dataToSend)   
    const url = `${HOSTFINAL}/api/login` 
    const options = {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(dataToSend)
    }
    
    const response = await fetch(url, options)
    if (!response.ok) {
        console.log('Error', response.status, response.statusText);
        return false
    }
    const data =  await response.json()
    return data
}

export const protect = async () => {
  console.log('funcion protect')
  const options = {
    headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem('token')}`
    }
  }
  console.log(options);
  
  const response = await fetch(`${HOSTFINAL}/api/protected`, options); 
  if (!response.ok){
    console.log('Error', response.status, response.statusText)
    return false    
  }
  const data = await response.json()
  console.log("RESPUESTA PROTECTED:", data);
  return data 
}

export const signup = async (dataToSend) => {
  const url = `${HOSTFINAL}/api/users`
  
  const options = {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
        body: JSON.stringify(dataToSend)
  }
    
  const response = await fetch(url, options)
  if (!response.ok) {
    const errorText = await response.text()
   console.error("Error backend:", errorText)
   return false
   }
  const data = await response.json()
  return data
  }
    
