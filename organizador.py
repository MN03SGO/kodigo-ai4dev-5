import os
import shutil
import subprocess
from pathlib import Path

def organizar_descargas():
    # Definir la ruta de descargas
    downloads_path = Path("/home/sigaran/Descargas")
    papelera_path = downloads_path / "Papelera_Temporales"
    
    # Extensiones permitidas
    extensiones_permitidas = {'.pdf', '.mp3', '.jpg', '.jpeg', '.png', '.mp4'}
    # Extensiones temporales a mover a papelera
    temporales_permitidas = {'.part', '.crdownload', '.tmp'}
    
    if not downloads_path.exists():
        print(f"La ruta {downloads_path} no existe.")
        return

    # Crear carpeta de papelera si no existe
    papelera_path.mkdir(exist_ok=True)

    # Iterar sobre los archivos en la carpeta
    for item in downloads_path.iterdir():
        # Solo procesar archivos
        if item.is_file():
            ext = item.suffix.lower()
            
            # Caso 1: Archivos a organizar
            if ext in extensiones_permitidas:
                folder_name = ext[1:].upper()
                target_folder = downloads_path / folder_name
                target_folder.mkdir(exist_ok=True)
                
                try:
                    shutil.move(str(item), str(target_folder / item.name))
                    print(f"Movido a organizacion: {item.name}")
                except Exception as e:
                    print(f"Error moviendo {item.name}: {e}")
            
            # Caso 2: Archivos temporales a papelera
            elif ext in temporales_permitidas:
                try:
                    # Usando gio para mover a la papelera del sistema
                    # 'gio trash <archivo>' es la forma estándar en Debian
                    subprocess.run(['gio', 'trash', str(item)], check=True)
                    print(f"Enviado a papelera (gio): {item.name}")
                except subprocess.CalledProcessError as e:
                    print(f"Error enviando {item.name} a papelera: {e}")

if __name__ == "__main__":
    organizar_descargas()
