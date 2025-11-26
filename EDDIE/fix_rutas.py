import sqlite3

conn = sqlite3.connect('EDDI.db')
cursor = conn.cursor()

# Actualizamos las rutas para que coincidan con tus archivos renombrados
# Asegúrate de que tus archivos en la carpeta se llamen 'firma.jpg' y 'sello.jpg'
cursor.execute("""
    UPDATE Usuarios 
    SET ruta_firma = 'static/firmas/firma.png', 
        ruta_sello = 'static/firmas/sello.png'
    WHERE rol = 'jefe'
""")



conn.commit()
conn.close()
print("Rutas actualizadas a firma.png y sello.png")