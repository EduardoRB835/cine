from flask import Flask, render_template, request, redirect, url_for, flash, session
import qrcode
import os
import uuid  # Para generar nombres de archivos únicos

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash messages

MAX_QR_CODES = 5

# Información de las películas
movies_info = {
    "La Sustancia": {
        "time": "12:00",
        "image_url": "/static/images/sustancia.webp"
    },
    "por definir": {
        "time": "11:00",
        "image_url": "/static/images/Opcion1.jpg"
    },
    "por definir1": {
        "time": "13:00",
        "image_url": "/static/images/opcion2.webp"
    }
}

# Crear carpeta de códigos QR si no existe
qr_code_base_folder = os.path.join(app.root_path, "static", "qr_codes")
if not os.path.exists(qr_code_base_folder):
    os.makedirs(qr_code_base_folder)

# Crear subcarpetas para cada película
for movie in movies_info.keys():
    movie_folder = os.path.join(qr_code_base_folder, movie.replace(' ', '_'))
    if not os.path.exists(movie_folder):
        os.makedirs(movie_folder)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_time", methods=["POST"])
def select_time():
    movie = request.form["movie"]
    return redirect(url_for("show_time", movie=movie))

@app.route("/show_time")
def show_time():
    movie = request.args.get("movie")
    
    # Obtener los detalles de la película
    movie_info = movies_info.get(movie, {})
    movie_time = movie_info.get("time", "")
    image_url = movie_info.get("image_url", "")

    return render_template("time.html", movie=movie, time=movie_time, image_url=image_url)

@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    movie = request.form["movie"]
    time = request.form["time"]
    seats = request.form.get("seats", "N/A")

    # Verifica que 'movie' está en 'movies_info'
    if movie in movies_info:
        # Crear carpeta para la película si no existe
        movie_folder = os.path.join(qr_code_base_folder, movie.replace(" ", "_"))
        if not os.path.exists(movie_folder):
            os.makedirs(movie_folder)

        # Contar cuántos códigos QR ya existen en la carpeta de la película
        existing_qr_codes = len([name for name in os.listdir(movie_folder) if name.endswith('.png')])

        # Verifica que no se hayan generado demasiados códigos QR para esta película
        if existing_qr_codes >= MAX_QR_CODES:
            flash("Lo sentimos, ya no tenemos lugar para esta función.", "error")
            return redirect(url_for("index"))

        # Generar el código QR
        qr_data = f"Película: {movie}\nHora: {time}\nAsientos: {seats}"
        qr_code_img = qrcode.make(qr_data)

        # Generar un nombre único para el archivo QR
        unique_filename = f"{uuid.uuid4()}.png"
        qr_code_path = os.path.join(movie_folder, unique_filename)
        qr_code_img.save(qr_code_path)

        flash("¡Código QR generado exitosamente!", "success")
        
        # Obtener la imagen de la película para pasarla a la plantilla
        image_url = movies_info[movie]["image_url"]

        return render_template("qr_code.html", movie=movie, time=time, seats=seats,
                               qr_code_url=f"/static/qr_codes/{movie.replace(' ', '_')}/{unique_filename}",
                               image_url=image_url)
    else:
        flash("La película no está disponible.", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
