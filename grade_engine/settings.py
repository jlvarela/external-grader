import os
import json
import logging
# requiere instalar path.py (pip - easy_install)
from path import path

ROOT_PATH = path(__file__).dirname() # donde se ubica este archivo
REPO_PATH = ROOT_PATH.dirname() # directorio del repositorio ../ROOT_PATH
ENV_ROOT = REPO_PATH.dirname() # ambiente ../REPO_PATH

# nivel de avisos del log del motor de calificacion
GRADER_ENGINE_LOG_LEVEL = logging.DEBUG 
# formato par el log del motor de calificacion
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_TIME_LOG_FORMAT = "%Y-%m-%d %H:%M:%S"


settings_file_path = None

# si no se explicita un archivo de configuracion, utilizamos
# el archivo por defecto.
if settings_file_path:
	SETTINGS_FILE_PATH = settings_file_path
else:
	SETTINGS_FILE_PATH = REPO_PATH / "settings.json"

# abrimos el archivo para obtener la configuracion
with open(SETTINGS_FILE_PATH) as settings_file:
	settings_tokens = json.load(settings_file)
QUEUES = settings_tokens.get("QUEUES")