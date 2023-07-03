import tkinter as tk
from tkinter import filedialog, colorchooser,messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import os

def open_image():
    global original_image, converted_image, cap, camera_opened

    # Verificar si la cámara está abierta
    if camera_opened:
        return

    # Abrir el cuadro de diálogo para seleccionar la imagen
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", ".jpg .jpeg .png .gif")])


    if file_path:
        # Cerrar la cámara si está abierta
        close_camera()

        # Cargar la imagen seleccionada
        original_image = Image.open(file_path).convert("RGB")
        original_image = original_image.resize((400, 400), Image.LANCZOS)

        # Mostrar la imagen en el lienzo
        image_tk = ImageTk.PhotoImage(original_image)
        canvas.create_image(0, 0, anchor="nw", image=image_tk)
        canvas.image = image_tk

        # Reiniciar la imagen convertida
        converted_image = None
def salir():
    if messagebox.askokcancel("Salir", "¿Estás seguro de que deseas salir?"):
        # Cerrar la cámara si está abierta
        close_camera()
        # Cerrar la ventana principal
        window.destroy()

def open_camera():
    global cap, camera_opened, capture_button

    # Verificar si la cámara ya está abierta
    if camera_opened:
        return

    # Cerrar la cámara si hay una imagen abierta
    if original_image:
        close_camera()

    # Abrir la cámara
    cap = cv2.VideoCapture(0)
    camera_opened = True

    # Actualizar el estado del botón
    camera_button.config(text="Cerrar cámara")
    capture_button.config(state="normal")

    # Actualizar la vista previa de la cámara
    update_camera_preview()

def close_camera():
    global cap, camera_opened, capture_button

    # Verificar si la cámara ya está cerrada
    if not camera_opened:
        return

    # Cerrar la cámara
    cap.release()
    camera_opened = False

    # Actualizar el estado del botón
    camera_button.config(text="Abrir cámara")
    capture_button.config(state="disabled")

def update_camera_preview():
    global cap, camera_opened, canvas

    # Verificar si la cámara está abierta
    if not camera_opened:
        return

    # Leer la imagen de la cámara
    ret, frame = cap.read()

    if ret:
        # Mostrar la imagen en el lienzo
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_pil = frame_pil.resize((400, 400), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(frame_pil)
        canvas.create_image(0, 0, anchor="nw", image=image_tk)
        canvas.image = image_tk

    # Programar la siguiente actualización de la vista previa
    canvas.after(10, update_camera_preview)

def capture_from_camera():
    global original_image, cap

    # Verificar si la cámara está abierta
    if not camera_opened:
        return

    # Capturar imagen desde la cámara
    ret, frame = cap.read()

    # Guardar la imagen capturada temporalmente
    temp_image_path = "temp_image.jpg"
    cv2.imwrite(temp_image_path, frame)

    # Cerrar la cámara
    close_camera()

    # Cargar la imagen capturada
    original_image = Image.open(temp_image_path).convert("RGB")
    original_image = original_image.resize((400, 400), Image.LANCZOS)

    # Mostrar la imagen en el lienzo
    image_tk = ImageTk.PhotoImage(original_image)
    canvas.create_image(0, 0, anchor="nw", image=image_tk)
    canvas.image = image_tk

    # Eliminar la imagen temporal
    os.remove(temp_image_path)

    # Reiniciar la imagen convertida
    converted_image = None

def convert_to_drawing():
    global original_image, converted_image

    if original_image:
        # Convertir la imagen a escala de grises
        gray_image = original_image.convert("L")

        # Crear una imagen en blanco transparente del mismo tamaño que la original
        converted_image = Image.new("RGB", original_image.size, "white")

        # Dibujar los píxeles negros del dibujo en la imagen en blanco
        draw = ImageDraw.Draw(converted_image)
        for x in range(image_width):
            for y in range(image_height):
                pixel = gray_image.getpixel((x, y))
                if pixel < 128:
                    draw.point((x, y), fill=current_color)

        # Agregar un borde a la imagen
        border_width = 10
        border_image = Image.new("RGB", (image_width + border_width * 2, image_height + border_width * 2), "white")
        border_image.paste(converted_image, (border_width, border_width))

        # Mostrar el dibujo con borde en el lienzo
        converted_image_tk = ImageTk.PhotoImage(border_image)
        canvas.create_image(0, 0, anchor="nw", image=converted_image_tk)
        canvas.image = converted_image_tk

def save_drawing():
    global converted_image

    if converted_image:
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if save_path:
            converted_image.save(save_path)
            print("Dibujo guardado con éxito.")

def toggle_drawing_mode():
    global drawing_mode

    if drawing_mode:
        draw_button.config(text="Activar dibujo")
        canvas.unbind("<B1-Motion>")
    else:
        draw_button.config(text="Desactivar dibujo")
        canvas.bind("<B1-Motion>", draw_on_image)

    drawing_mode = not drawing_mode

def choose_color():
    global current_color

    color = colorchooser.askcolor(title="Seleccionar color")
    if color:
        current_color = color[1]

def adjust_brush_size(value):
    global brush_size

    brush_size = int(value)

def choose_pencil_tip(pencil_tip):
    global current_pencil_tip

    current_pencil_tip = pencil_tip

def draw_on_image(event):
    global converted_image

    if converted_image and drawing_mode:
        x = event.x
        y = event.y

        draw = ImageDraw.Draw(converted_image)
        if eraser_mode:
            draw.rectangle((x - brush_size, y - brush_size, x + brush_size, y + brush_size), fill=(255, 255, 255, 0))
        else:
            if current_pencil_tip == "Brush":
                draw.ellipse((x - brush_size, y - brush_size, x + brush_size, y + brush_size), fill=current_color)
            elif current_pencil_tip == "Pencil":
                draw.rectangle((x - brush_size, y - brush_size, x + brush_size, y + brush_size), fill=current_color)
            elif current_pencil_tip == "Crayon":
                draw.line((x - brush_size, y - brush_size, x + brush_size, y + brush_size), fill=current_color, width=brush_size)

        # Mostrar el dibujo con borde en el lienzo
        converted_image_tk = ImageTk.PhotoImage(converted_image)
        canvas.create_image(0, 0, anchor="nw", image=converted_image_tk)
        canvas.image = converted_image_tk

def toggle_eraser_mode():
    global eraser_mode

    eraser_mode = not eraser_mode

    if eraser_mode:
        eraser_button.config(text="Desactivar borrador")
    else:
        eraser_button.config(text="Activar borrador")

# Crear la ventana principal
window = tk.Tk()
window.title("Foto a Dibujo")
window.geometry("700x600")

# Variables globales
original_image = None
converted_image = None
image_width = 400
image_height = 400
cap = None
camera_opened = False
drawing_mode = False
current_color = "black"  # Color predeterminado
brush_size = 5  # Grosor del pincel
eraser_mode = False
current_pencil_tip = "Brush"  # Tipo de punta de lápiz predeterminada

# Canvas para mostrar la imagen
canvas = tk.Canvas(window, width=image_width, height=image_height,)
canvas.grid(row=0, column=1, padx=10, pady=10, rowspan=14, sticky="n")

# Botón para importar foto
import_button = tk.Button(window, text="Importar foto", command=open_image,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
import_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Botón para abrir la cámara
camera_button = tk.Button(window, text="Abrir cámara", command=open_camera,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
camera_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

# Botón para capturar desde la cámara
capture_button = tk.Button(window, text="Capturar desde cámara", command=capture_from_camera,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
capture_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")
capture_button.config(state="disabled")

# Botón para convertir a dibujo
convert_button = tk.Button(window, text="Convertir a dibujo", command=convert_to_drawing,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
convert_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

# Botón para guardar el dibujo
save_button = tk.Button(window, text="Guardar dibujo", command=save_drawing,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
save_button.grid(row=5, column=0, padx=5, pady=5, sticky="w")

# Botón para activar/desactivar el modo de dibujo
draw_button = tk.Button(window, text="Activar dibujo", command=toggle_drawing_mode,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
draw_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")

# Botón para seleccionar color
color_button = tk.Button(window, text="Seleccionar color", command=choose_color,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
color_button.grid(row=7, column=0, padx=5, pady=5, sticky="w")

# Slider para ajustar el grosor del pincel
size_label = tk.Label(window, text="Grosor del pincel")
size_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")

size_slider = tk.Scale(window, from_=1, to=20, orient="horizontal", command=adjust_brush_size,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
size_slider.set(brush_size)
size_slider.grid(row=9, column=0, padx=5, pady=5, sticky="w")

# Botón para seleccionar tipo de punta de lápiz
pencil_tip_label = tk.Label(window, text="Tipo de punta de lápiz")
pencil_tip_label.grid(row=10, column=0, padx=5, pady=5, sticky="w")

pencil_tip_frame = tk.Frame(window)
pencil_tip_frame.grid(row=11, column=0, padx=5, pady=5, sticky="w")

brush_button = tk.Button(pencil_tip_frame, text="Brush", command=lambda: choose_pencil_tip("Brush"),bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
brush_button.grid(row=0, column=0, padx=5, pady=5)

pencil_button = tk.Button(pencil_tip_frame, text="Pencil", command=lambda: choose_pencil_tip("Pencil"),bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
pencil_button.grid(row=0, column=1, padx=5, pady=5)

crayon_button = tk.Button(pencil_tip_frame, text="Crayon", command=lambda: choose_pencil_tip("Crayon"),bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
crayon_button.grid(row=0, column=2, padx=5, pady=5)

# Botón para activar/desactivar el modo de borrador
eraser_button = tk.Button(window, text="Activar borrador", command=toggle_eraser_mode,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
eraser_button.grid(row=12, column=0, padx=5, pady=5, sticky="w")

# Botón para salir de la aplicación
exit_button = tk.Button(window, text="Salir", command=salir,bg="red", fg="white", relief="raised",font=("Arial", 12, "bold"))
exit_button.grid(row=13, column=0, padx=5, pady=5, sticky="w")

# Ejecutar la interfaz gráfica
window.mainloop()