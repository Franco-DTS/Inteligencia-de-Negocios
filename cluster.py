import pandas as pd
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from concurrent.futures import ThreadPoolExecutor

def cargar_datos():
    # Cargar el conjunto de datos de Netflix
    netflix_data = pd.read_csv('netflix_data.csv')
    # Reemplazar los valores NaN en la columna 'rating' con "Desconocido"
    netflix_data['rating'] = netflix_data['rating'].fillna("Desconocido")
    return netflix_data

def mostrar_descripcion_pelicula_serie():
    global listbox_recomendaciones, netflix_data, descripcion_text
    
    # Obtener el índice seleccionado en la lista de recomendaciones
    seleccion = listbox_recomendaciones.curselection()
    
    # Verificar si se ha seleccionado algo
    if seleccion:
        # Obtener el título seleccionado
        indice_seleccionado = seleccion[0]
        titulo_seleccionado = listbox_recomendaciones.get(indice_seleccionado)
        
        # Obtener la descripción correspondiente al título seleccionado
        descripcion = netflix_data[netflix_data['title'] == titulo_seleccionado]['description'].iloc[0]
        
        # Mostrar la descripción en el widget Text
        descripcion_text.config(state=tk.NORMAL)  # Habilitar el widget para escribir
        descripcion_text.delete(1.0, tk.END)
        descripcion_text.insert(tk.END, descripcion)
        descripcion_text.config(state=tk.DISABLED)  # Deshabilitar el widget para escribir

def generar_recomendaciones():
    def actualizar_listbox(recomendaciones):
        listbox_recomendaciones.delete(0, tk.END)  # Limpiar las recomendaciones anteriores
        for recomendacion in recomendaciones:
            listbox_recomendaciones.insert(tk.END, recomendacion)
    
    genero = genre_combobox.get()
    año_lanzamiento = int(year_combobox.get())
    rating = rating_combobox.get()

    # Filtrar el conjunto de datos en función de las preferencias del usuario
    filtered_data = netflix_data[
        (netflix_data['listed_in'].str.contains(genero, case=False, na=False)) &
        (netflix_data['release_year'] == año_lanzamiento) &
        (netflix_data['rating'] == rating)
    ]

    recomendaciones = filtered_data['title'].tolist()
    
    # Actualizar el Listbox en el hilo principal
    root.after(0, actualizar_listbox, recomendaciones)

def actualizar_años(event):
    genero_seleccionado = genre_combobox.get()
    if genero_seleccionado:
        años_disponibles = sorted(netflix_data[netflix_data['listed_in'].str.contains(genero_seleccionado, case=False, na=False)]['release_year'].unique())
        year_combobox['values'] = años_disponibles
        year_combobox.set('')  
        rating_combobox.set('')  
        if años_disponibles:
            actualizar_clasificaciones(None)

def actualizar_clasificaciones(event):
    año_seleccionado = year_combobox.get()
    if año_seleccionado:
        genero_seleccionado = genre_combobox.get()
        clasificaciones_disponibles = sorted(netflix_data[(netflix_data['release_year'] == int(año_seleccionado)) & (netflix_data['listed_in'].str.contains(genero_seleccionado, case=False, na=False))]['rating'].unique())
        rating_combobox['values'] = clasificaciones_disponibles
        rating_combobox.set('')  

def limpiar_campos():
    genre_combobox.set('')
    year_combobox.set('')
    rating_combobox.set('')
    descripcion_text.config(state=tk.NORMAL)  # Habilitar el widget para escribir
    descripcion_text.delete(1.0, tk.END)
    descripcion_text.config(state=tk.DISABLED)  # Deshabilitar el widget para escribir
    listbox_recomendaciones.delete(0, tk.END)

def main():
    global netflix_data, root, listbox_recomendaciones, genre_combobox, year_combobox, rating_combobox, descripcion_text
    
    netflix_data = cargar_datos()

    root = tk.Tk()
    root.title("Sistema de Recomendación de Netflix")

    # Establecer el color de fondo de la ventana principal a negro
    root.configure(bg='black')

    # Aplicar un estilo al root
    style = ttk.Style()
    style.theme_use('clam')  # Seleccionar un tema (puedes probar otros como 'vista', 'winnative', etc.)
    style.configure('Accent.TButton', background='red', foreground='black', font=('Helvetica', 12, 'bold'))
    style.configure('TLabel', foreground='red', font=('Helvetica', 12))
    style.configure('TCombobox', foreground='red', background='black', font=('Helvetica', 12))

    # Etiqueta de título
    title_label = ttk.Label(root, text="Sistema de Recomendación de Netflix", font=('Helvetica', 18, 'bold'), foreground='red', background='black')
    title_label.pack(pady=(10,0), expand=True)

    # Agregar el logotipo de Netflix
    netflix_logo_path = "netflix_logo.png"
    if os.path.exists(netflix_logo_path):
        netflix_logo = Image.open(netflix_logo_path)  
        netflix_logo = netflix_logo.resize((200, 100), Image.NEAREST)
        netflix_logo = ImageTk.PhotoImage(netflix_logo)
        logo_label = ttk.Label(root, image=netflix_logo, background='black')
        logo_label.image = netflix_logo  # Mantener una referencia para evitar la recolección de basura
        logo_label.pack(expand=True)

    # Marco para los widgets de selección
    selection_frame = ttk.Frame(root, padding=10, relief="solid")
    selection_frame.pack(pady=(10,0), expand=True)

    # Opción de selección para el género
    genre_label = ttk.Label(selection_frame, text="Seleccione un género:", foreground='red', background='black')
    genre_label.grid(row=0, column=0, sticky="w")
    generos = netflix_data['listed_in'].str.split(', ').explode().unique()
    generos = [genero.strip() for genero in generos]  # Eliminar espacios en blanco alrededor de los géneros
    genre_combobox = ttk.Combobox(selection_frame, values=generos)
    genre_combobox.grid(row=0, column=1)
    genre_combobox.bind("<<ComboboxSelected>>", actualizar_años)  # Enlazar evento de selección de género

    # Opción de selección para el año de lanzamiento
    year_label = ttk.Label(selection_frame, text="Seleccione un año de lanzamiento:", foreground='red', background='black')
    year_label.grid(row=1, column=0, sticky="w")
    años_disponibles = sorted(netflix_data['release_year'].unique())
    year_combobox = ttk.Combobox(selection_frame, values=años_disponibles)
    year_combobox.grid(row=1, column=1)
    year_combobox.bind("<<ComboboxSelected>>", actualizar_clasificaciones)  # Enlazar evento de selección de año

    # Opción de selección para la clasificación
    rating_label = ttk.Label(selection_frame, text="Seleccione una clasificación:", foreground='red', background='black')
    rating_label.grid(row=2, column=0, sticky="w")
    clasificaciones_disponibles = sorted(netflix_data['rating'].unique())
    rating_combobox = ttk.Combobox(selection_frame, values=clasificaciones_disponibles)
    rating_combobox.grid(row=2, column=1)

    # Botones
    button_frame = ttk.Frame(root, padding=10, relief="solid")
    button_frame.pack(pady=10, expand=True)

    # Botón para limpiar los campos
    clear_button = ttk.Button(button_frame, text="Limpiar Campos", command=limpiar_campos, style='Accent.TButton')
    clear_button.grid(row=0, column=0, padx=5)

    # Botón para buscar recomendaciones
    search_button = ttk.Button(button_frame, text="Buscar Recomendaciones", command=generar_recomendaciones, style='Accent.TButton')
    search_button.grid(row=0, column=1, padx=5)

    # Widget Listbox para mostrar las recomendaciones
    listbox_recomendaciones = tk.Listbox(root, font=('Helvetica', 12), width=50)
    listbox_recomendaciones.pack(pady=(0,10), expand=True)

    # Botón para mostrar la descripción de la recomendación seleccionada
    show_info_button = ttk.Button(root, text="Mostrar Descripción", command=mostrar_descripcion_pelicula_serie, style='Accent.TButton')
    show_info_button.pack(pady=(0,10), expand=True)

    # Widget Text para mostrar la descripción de la película/serie seleccionada
    descripcion_text = tk.Text(root, height=5, wrap='word', font=('Helvetica', 12))
    descripcion_text.pack(pady=(0,10), expand=True)
    descripcion_text.config(state=tk.DISABLED)  # Configurar el widget como de solo lectura

    root.mainloop()

if __name__ == "__main__":
    main()
