from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from textwrap import wrap

app = Flask(__name__)

# Diccionario de empleados con nombre, cédula y cargo
empleados = {
    "Clean Hub": [
        {"nombre": "PUERTA ROJAS MARTA BEATRIZ", "cedula": "0966605388", "cargo": "AUXILIAR DE LIMPIEZA"},
        {"nombre": "QUIJANO CUEVA EDUARDO ALEJANDRO", "cedula": "1724584196", "cargo": "TRABAJADOR EN GENERAL"},
        {"nombre": "TOALA RODRIGUEZ IRENE LEONOR", "cedula": "0919539551", "cargo": "AUXLIAR DE ENFERMERIA"},
    ],
    "Zurcidos": [
        {"nombre": "BUENO YUNGA TRINIDAD NARSISA DE JESUS", "cedula": "0702595612", "cargo": "COSTURERA"},
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/empleados', methods=['POST'])
def obtener_empleados():
    empresa = request.form.get("empresa")
    if empresa in empleados:
        return jsonify({"empleados": empleados[empresa]})
    return jsonify({"empleados": []})

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    # Obtener los datos del formulario
    nombre = request.form.get('empleado')
    empresa = request.form.get('empresa')
    dias = request.form.get('dias')
    tipo_solicitud = request.form.get('tipo_solicitud')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    fecha_actual = datetime.now().strftime('%d/%m/%Y')

    # Validar que el empleado seleccionado está en la empresa correspondiente
    empleado_info = None
    for emp in empleados.get(empresa, []):
        if emp["nombre"] == nombre:
            empleado_info = emp
            break

    if not empleado_info:
        return "Error: El empleado seleccionado no es válido.", 400

    cedula = empleado_info["cedula"]
    cargo = empleado_info["cargo"]
    
    # Crear un buffer en memoria para el archivo PDF
    buffer = io.BytesIO()

    # Crear el PDF con ReportLab
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Dimensiones de la hoja

    # Márgenes
    margin_x = 50
    margin_y = 50

    # Posición inicial
    y_position = height - margin_y

    # Título centrado
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, y_position, "Formulario de Solicitud de Vacaciones")
    y_position -= 40

    # Añadir el nombre de la empresa debajo del título
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y_position, f"Empresa: {empresa}")
    y_position -= 30  # Espaciado después del nombre de la empresa

    # Fecha Actual
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_x, y_position, "Fecha: ")
    c.setFont("Helvetica", 12)
    c.drawString(margin_x + 50, y_position, fecha_actual)
    y_position -= 30

    # Texto principal justificado
    c.setFont("Helvetica", 12)
    text = f"Yo, {nombre}, con cédula: {cedula}, que desempeño el cargo de: {cargo}, solicito a usted me otorgue:"
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 30

    # Tipo de solicitud
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y_position, "Tipo de solicitud:")
    y_position -= 20
    c.setFont("Helvetica", 12)
    tipo_texto = "Vacaciones" if tipo_solicitud == "vacaciones" else "Anticipo de vacaciones"
    y_position = draw_paragraph(c, tipo_texto, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 30

    # Días tomados
    text = f"Solicito {dias} días a partir del {fecha_inicio} hasta el {fecha_fin}."
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 40

    # Firmas
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y_position, "Firma del solicitante: ___________________________")
    y_position -= 50

    y_position -= 60

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y_position, "Autorización")
    y_position -= 30

    c.setFont("Helvetica", 12)
    text = f"En calidad de jefe inmediato, autorizo {dias} días."
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 50

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y_position, "Firma Jefe Departamento: ___________________________")

    y_position -= 60

    # Notas
    y_position -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y_position, "Notas:")

    y_position -= 20
    c.setFont("Helvetica", 8)
    notas = [
        "1. No serán válidas las solicitudes que contengan tachones, enmendaduras o tinta correctora.",
        "2. La presente solicitud está sujeta a verificación, previo análisis del servidor/a responsable del proceso de vacaciones."
    ]
    for nota in notas:
        y_position = draw_paragraph(c, nota, margin_x, y_position, max_width=width - 2 * margin_x)
        y_position -= 10

    # Finalizar el PDF
    c.showPage()
    c.save()

    # Volver al inicio del buffer para leer el contenido
    buffer.seek(0)

    # Enviar el PDF generado al navegador
    return send_file(buffer, as_attachment=True, download_name="solicitud_vacaciones.pdf", mimetype="application/pdf")

def draw_paragraph(c, text, x, y, max_width, font="Helvetica", font_size=12, line_spacing=18):
    """
    Función para dibujar un párrafo justificado dentro de un ancho máximo.
    """
    c.setFont(font, font_size)
    lines = wrap(text, width=80)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_spacing
    return y

if __name__ == '__main__':
    app.run(debug=True)
