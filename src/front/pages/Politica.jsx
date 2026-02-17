import React from "react";

export default function Politica() {
  return (
    <div className="bg-light">

      
      <div className="bg-white border-bottom py-5 mb-4">
        <div className="container">
          <h1 className="display-5 fw-bold">Política de Privacidad</h1>
          <p className="lead text-muted mb-0">
            Información sobre el tratamiento de datos personales en esta web
          </p>
        </div>
      </div>

 
      <div className="container pb-5">
        <div className="card shadow-sm">
          <div className="card-body p-4 p-md-5">

            <section className="mb-5">
              <h2 className="h4 fw-bold">INFORMACIÓN DEL TITULAR DE LA WEB</h2>
              <p>
                <strong>+volca</strong> CIF/NIF <strong>xxxxx</strong> con domicilio en
                CALLE MAHON, 18, ELCHE (ALICANTE), 03206 y mail de comunicaciones{" "}
                <a href="mailto:hola@activaelkoko.com">hola@activaelkoko.com</a>
              </p>
              <p>Inscripción en el Registro Mercantil con Nº: A-179901.</p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">RESPONSABLE DE PROTECCIÓN DE DATOS</h2>
              <p>
                El titular es el responsable de los datos personales recabados por la navegación
                y uso de esta web conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley 34/2002
                de Servicios de la Sociedad de la Información.
              </p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">DATOS RECABADOS, FINALIDAD Y LICITUD</h2>
              <ul className="list-group list-group-flush">
                <li className="list-group-item">Envío de información sobre productos o servicios</li>
                <li className="list-group-item">Atención de consultas</li>
                <li className="list-group-item">Gestión de pedidos y facturación</li>
              </ul>
              <p className="mt-3">
                El tratamiento se basa en ejecución de contrato, obligación legal,
                interés legítimo o consentimiento del usuario.
              </p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">FORMULARIOS WEB</h2>
              <p>
                Los datos del formulario de contacto se utilizan para responder consultas.
                Los datos del formulario de pedidos se utilizan para gestionar compras.
              </p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">DESTINATARIOS DE LOS DATOS</h2>
              <p>
                No se comunicarán datos a terceros salvo obligación legal o necesidad
                para prestar el servicio (pasarelas de pago y transportistas).
              </p>

              <div className="accordion mt-3" id="pagos">
                <div className="accordion-item">
                  <h2 className="accordion-header">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#redsys">
                      Redsys
                    </button>
                  </h2>
                  <div id="redsys" className="accordion-collapse collapse" data-bs-parent="#pagos">
                    <div className="accordion-body">
                      Redsys Servicios de Procesamiento, S.L. (CIF B-85955367)
                      <br />
                      <a target="_blank" href="https://www.redsys.es/legal/20180223_politica_de_privacidad_web_publica_redsys.pdf">
                        Ver política de privacidad
                      </a>
                    </div>
                  </div>
                </div>

                <div className="accordion-item">
                  <h2 className="accordion-header">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#paypal">
                      PayPal
                    </button>
                  </h2>
                  <div id="paypal" className="accordion-collapse collapse" data-bs-parent="#pagos">
                    <div className="accordion-body">
                      PayPal (Europe) S.à.r.l. et Cie, S.C.A.
                      <br />
                      <a target="_blank" href="https://www.paypal.com/es/webapps/mpp/ua/privacy-full?locale.x=es_ES#1">
                        Ver política de privacidad
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">CONSERVACIÓN DE LOS DATOS</h2>
              <p>
                Los datos se conservarán mientras exista relación contractual o hasta solicitar su supresión.
              </p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">DELEGADO DE PROTECCIÓN DE DATOS</h2>
              <p>
                SYMTRA CONSULTORES Y FORMACION SLU —{" "}
                <a href="mailto:DPD@SOLUCIONLOPD.NET">DPD@SOLUCIONLOPD.NET</a>
              </p>
            </section>

            <section className="mb-5">
              <h2 className="h4 fw-bold">OPOSICIÓN A PUBLICIDAD</h2>
              <p>
                Puede revocar su consentimiento enviando un correo a{" "}
                <a href="mailto:hola@activaelkoko.com">hola@activaelkoko.com</a>
              </p>
            </section>

            <section>
              <h2 className="h4 fw-bold">CAMBIOS EN LA POLÍTICA</h2>
              <p>
                Nos reservamos el derecho de modificar esta política para adaptarla a novedades legales.
              </p>
            </section>

            <hr />
            <div className="text-muted small">Última actualización: 17/02/2026</div>

          </div>
        </div>
      </div>

    </div>
  );
}


