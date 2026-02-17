import React, { useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, CardElement, useStripe, useElements } from "@stripe/react-stripe-js";

const stripePromise = loadStripe("TU_PUBLIC_KEY_DE_STRIPE");

const CheckoutForm = ({ clientSecret }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");

    if (!stripe || !elements) return;

    const cardElement = elements.getElement(CardElement);

    const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: { card: cardElement }
    });

    if (error) {
      setErrorMessage(error.message);
    } else if (paymentIntent.status === "succeeded") {
      alert("Pago exitoso 🎉");
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      {errorMessage && <div className="text-danger mt-2">{errorMessage}</div>}
      <button type="submit" className="btn btn-primary w-100 mt-3" disabled={loading}>
        {loading ? "Procesando..." : "Pagar"}
      </button>
    </form>
  );
};

export const StripePaymentModal = ({ show, onClose, clientSecret }) => {
  if (!show) return null;
  return (
    <div className="modal show d-block">
      <div className="modal-dialog">
        <div className="modal-content p-3">
          <button className="btn-close mb-3" onClick={onClose}></button>
          <Elements stripe={stripePromise}>
            <CheckoutForm clientSecret={clientSecret} />
          </Elements>
        </div>
      </div>
    </div>
  );
};
