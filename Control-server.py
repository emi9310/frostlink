import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font

# Diccionario para almacenar los topics y sus valores por equipo
device_topics = {}

# Crear la ventana principal de tkinter
root = tk.Tk()
root.title("Dispositivos de la Red FrostLink")

# Configurar la fuente mayor para el título
title_font = font.Font(family="Helvetica", size=16, weight="bold")

# Crear un widget de etiqueta para el título
title_label = tk.Label(root, text="FrostLink:", font=title_font)
title_label.pack(pady=5)

# Crear un widget de lista para mostrar los dispositivos
device_label = tk.Label(root, text="Lista de Dispositivos:")
device_label.pack(pady=5)
device_listbox = tk.Listbox(root, height=5, width=50)
device_listbox.pack(pady=5)

# Crear un widget de lista para mostrar los topics de un dispositivo
topic_label = tk.Label(root, text="Topics del Dispositivo Seleccionado:")
topic_label.pack(pady=5)
topic_listbox = tk.Listbox(root, height=10, width=50)
topic_listbox.pack(pady=5)

# Crear un widget de texto para depuración por consola
console_text = tk.Text(root, height=5, width=50)
console_text.pack(pady=5)

# Función para manejar el evento de clic en la lista de dispositivos
def on_device_click(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        device = event.widget.get(index)
        console_text.insert(tk.END, f"Dispositivo seleccionado: {device}\n")
        console_text.see(tk.END)
        # Limpiar la lista de topics y mostrar los topics del dispositivo seleccionado con sus valores
        topic_listbox.delete(0, tk.END)
        if device in device_topics:
            for topic, value in device_topics[device].items():
                topic_listbox.insert(tk.END, f"{topic}: {value}")

device_listbox.bind('<<ListboxSelect>>', on_device_click)

# Función de callback cuando te conectas al servidor MQTT
def on_connect(client, userdata, flags, rc):
    console_text.insert(tk.END, "Conectado al servidor MQTT de Orion\n")
    console_text.insert(tk.END, "Dispositivos de la Red FrostLink:\n")
    console_text.see(tk.END)
    # Suscribirse a todos los topics
    client.subscribe("#")

# Función de callback cuando se recibe un mensaje
def on_message(client, userdata, msg):
    global device_topics
    # Extraer el dispositivo del topic
    topic_parts = msg.topic.split('/')
    if len(topic_parts) > 1:
        device = topic_parts[1]
        topic = '/'.join(topic_parts[2:])
        value = msg.payload.decode()
        if device not in device_topics:
            device_listbox.insert(tk.END, device)
            device_topics[device] = {}
        device_topics[device][topic] = value
        console_text.insert(tk.END, f"Equipo: {device}, Topic: {topic}, Mensaje: {value}\n")
        console_text.see(tk.END)

# Crear una instancia del cliente
client = mqtt.Client()

# Asignar funciones de callback
client.on_connect = on_connect
client.on_message = on_message

# Conectarse al broker MQTT
client.connect("mqtt.orionsi.com.ar", 11883, 60)

# Función para procesar mensajes MQTT en el bucle principal de tkinter
def process_mqtt():
    client.loop(timeout=1.0)
    root.after(100, process_mqtt)

# Iniciar el procesamiento de mensajes MQTT
root.after(100, process_mqtt)

# Iniciar el bucle principal de tkinter
root.mainloop()
