import React from "react";
import { useLocation } from "react-router-dom";

const urlBackend = import.meta.env.VITE_BACKEND_URL;

export const PasarelaPago = () => {
  const location = useLocation();
  const paymentAmount = location.state?.paymentAmount || 0;

  const handleCheckout = async () => {
    try {
      const response = await fetch(urlBackend + "create-checkout-session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: paymentAmount,
        }),
      });

      const data = await response.json();

      if (data.url) {
        window.location.href = data.url; // 👈 redirige a Stripe
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="checkout-container">
      <h2>Total a pagar: {paymentAmount} €</h2>
      <button onClick={handleCheckout} className="btn-checkout">
        Pagar ahora
      </button>
    </div>
  );
};
