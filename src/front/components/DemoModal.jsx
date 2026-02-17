import React from "react";

export const DemoModal = ({ show, onClose, course }) => {
  if (!show) return null;

  return (
    <div className="modal show d-block" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Demo: {course.name}</h5>
            <button className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <p>Video o contenido de prueba del curso aquí.</p>
            <div className="ratio ratio-16x9">
              <iframe 
                src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                title="Demo" 
                allowFullScreen
              ></iframe>
            </div>
          </div>
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={onClose}>Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  );
};
