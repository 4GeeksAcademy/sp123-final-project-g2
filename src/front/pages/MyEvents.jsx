import React from 'react'
import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import AuthShell from "../components/AuthShell";
import TextInput from "../components/TextInput";
import { login } from "../jsApiComponents/auth"
import { Button } from 'react-bootstrap';


export default function MyEvents() {
    return (

            <AuthShell title="Iniciar sesión" subtitle="Por favor, inicia sesión para continuar" >
                <Button variant= "btn custom-btn m-2">Mis actividades</Button>
                <Button variant= "btn custom-btn m-2">Actividades que sigo</Button>
            </AuthShell>

    )
}


