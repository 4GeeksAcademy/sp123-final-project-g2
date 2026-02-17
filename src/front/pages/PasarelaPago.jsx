import React, { useState } from "react";
import { loadStripe } from "@stripe/stripe-js";

const urlBackend = import.meta.env.VITE_BACKEND_URL;

export const PasarelaPago = () => {
  const [selectedCourse, setSelectedCourse] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [cardNumber, setCardNumber] = useState("");

  const courses = [
    { id: 1, name: "Curso Iniciación Vocal" },
    { id: 2, name: "Curso Técnica Avanzada" },
    { id: 3, name: "Curso Interpretación" },
  ];

  const handleCheckout = async (e) => {
    e.preventDefault();

    if (!selectedCourse) {
      setErrorMessage("Selecciona un curso.");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    const token = localStorage.getItem("token");

    // 1️⃣ Crear PaymentIntent en backend
    const response = await fetch(urlBackend + "/api/purchases-private", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({
        course_id: selectedCourse
      })
    });

    const data = await response.json();

    if (!response.ok) {
      setLoading(false);
      setErrorMessage(data.message || "Error preparando el pago");
      return;
    }

    const stripeData = data.response.stripe_payment;

    // 2️⃣ Inicializar Stripe
    const stripe = await loadStripe(stripeData.publishable_key);

    // 3️⃣ Confirmar pago con tarjeta de prueba
    const result = await stripe.confirmCardPayment(
      stripeData.client_secret,
      {
        payment_method: {
          card: {
            // Para pruebas simples sin Stripe Elements:
            number: "4242424242424242",
            exp_month: 12,
            exp_year: 2030,
            cvc: "123"
          }
        }
      }
    );

    if (result.error) {
      setLoading(false);
      setErrorMessage(result.error.message);
      return;
    }

    if (result.paymentIntent.status === "succeeded") {
      alert("Pago realizado con éxito 🎉");
      window.location.reload();
    }

    setLoading(false);
  };

  return (
    <div className="container py-5" style={{ maxWidth: "500px" }}>
      <div className="card shadow p-4">
        <h2 className="mb-4 text-center">Comprar Curso</h2>

        <form onSubmit={handleCheckout}>
          <div className="mb-3">
            <label className="form-label fw-bold">
              Selecciona un curso
            </label>
            <select
              className="form-select"
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(Number(e.target.value))}
              required
            >
              <option value="">-- Selecciona --</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name}
                </option>
              ))}
            </select>
          </div>

          {errorMessage && (
            <div className="alert alert-danger">
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading ? "Procesando..." : "Pagar ahora"}
          </button>
        </form>
      </div>
    </div>
  );
};
