const BASE_URL = import.meta.env.VITE_BACKEND_URL;
const userID = localStorage.getItem("USER");
const token = localStorage.getItem("JWT-STORAGE-KEY");
export const deleteUser = async (body) => {
  try {
    const response = await fetch(`${BASE_URL}api/user/${userID}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.status === 204) return {'msg': "Usuario Eliminado"}
    
    const data = await response.json();

    return data;
  } catch (error) {
    console.log(error);
  }
};
