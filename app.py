from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from textwrap import wrap

app = Flask(__name__)

# Diccionario de empleados con nombre, cédula y cargo
empleados = {
    "PUERTA ROJAS MARTA BEATRIZ": {"cedula": "0966605388", "cargo": "AUXILIAR DE LIMPIEZA"},
    "QUIJANO CUEVA EDUARDO ALEJANDRO": {"cedula": "1724584196", "cargo": "TRABAJADOR EN GENERAL "},
    "TOALA RODRIGUEZ IRENE LEONOR": {"cedula": "0919539551", "cargo": "AUXLIAR DE ENFERMERIA"}
}

@app.route('/')
def index():
    # Convertimos el diccionario de empleados a un formato adecuado para enviar al frontend
    empleados_list = [{"nombre": nombre, "cedula": datos["cedula"], "cargo": datos["cargo"]} for nombre, datos in empleados.items()]
    return render_template('index.html', empleados=empleados_list)

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    # Obtener los datos del formulario
    nombre = request.form['empleado']
    cedula = empleados[nombre]['cedula']  # Obtener cédula desde el diccionario de empleados
    cargo = empleados[nombre]['cargo']  # Obtener cargo desde el diccionario de empleados
    empresa = request.form['empresa']  # Obtener la empresa seleccionada
    dias = request.form['dias']
    tipo_solicitud = request.form['tipo_solicitud']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    fecha_actual = datetime.now().strftime('%d/%m/%Y')

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

    # Colocar el logo en la esquina superior izquierda
    logo_path = "static/images/logo.png"  # Ruta del logo
    logo_width = 50  # Ancho del logo (ajustar según el tamaño deseado)
    logo_height = 50  # Alto del logo (ajustar según el tamaño deseado)

    # Dibuja el logo en la esquina superior izquierda
    c.drawImage(logo_path, margin_x, height - logo_height - 10, width=logo_width, height=logo_height)

    # Título centrado
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, y_position, "Formulario de Solicitud de Vacaciones")
    y_position -= 40

    # Fecha Actual
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_x, y_position, "Fecha: ")  # Texto en negrita

    c.setFont("Helvetica", 12)
    c.drawString(margin_x + 50, y_position, fecha_actual)  # Alinear la fecha con el texto anterior
    y_position -= 30

    # Texto principal justificado
    c.setFont("Helvetica", 12)
    text = f"Yo, {nombre}, con cédula: {cedula}, que desempeño el cargo de: {cargo}, solicito a usted me otorgue:"
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    # Espaciado antes del siguiente bloque
    y_position -= 30

    # Tipo de solicitud en negrita
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x, y_position, "Tipo de solicitud:")

    # Ajustar posición para evitar cortes en el texto
    y_position -= 20  # Espacio debajo del título

    # Mostrar correctamente la selección del usuario
    c.setFont("Helvetica", 12)
    tipo_texto = "Vacaciones" if tipo_solicitud == "vacaciones" else "Anticipo de vacaciones"

    # Usamos draw_paragraph() para asegurarnos de que se ajuste correctamente
    y_position = draw_paragraph(c, tipo_texto, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 30  # Espaciado después del tipo de solicitud

    # Días tomados
    text = f"Solicito {dias} días a partir del {fecha_inicio} hasta el {fecha_fin}."
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 40

    # Firmas
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y_position, "Firma del solicitante: ___________________________")
    y_position -= 50

    y_position -= 60 

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y_position, "Autorización")
    y_position -= 30

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    text = f"En calidad de jefe inmediato, autorizo {dias} días."
    y_position = draw_paragraph(c, text, margin_x, y_position, max_width=width - 2 * margin_x)

    y_position -= 50

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y_position, "Firma Jefe Departamento: ___________________________")

    y_position -= 60

    # Notas al final del documento
    y_position -= 50  # Espacio antes de las notas
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(margin_x, y_position, "Notas:")

    y_position -= 20  # Espacio antes de las notas

    # Configurar fuente y color para el contenido de las notas
    c.setFont("Helvetica", 8)
    notas = [
        "1. No serán válidas las solicitudes que contengan tachones, enmendaduras o tinta correctora.",
        "2. La presente solicitud está sujeta a verificación, previo análisis del servidor/a responsable del proceso de vacaciones."
    ]

    # Dibujar notas con draw_paragraph() para alineación correcta
    for nota in notas:
        y_position = draw_paragraph(c, nota, margin_x, y_position, max_width=width - 2 * margin_x)
        y_position -= 10  # Espaciado entre notas
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
    lines = wrap(text, width=80)  # Ajusta el ancho máximo de caracteres por línea
    for line in lines:
        c.drawString(x, y, line)  # Dibuja cada línea alineada a la izquierda
        y -= line_spacing  # Espaciado entre líneas
    return y  # Retorna la nueva posición Y después de escribir el texto

if __name__ == '__main__':
    app.run(debug=True)
