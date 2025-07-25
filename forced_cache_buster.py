
"""
FORCED CACHE BUSTER - DEPLOY INMEDIATO
Fuerza Docker a usar código actualizado
"""

import time
import random
import string

def generate_cache_buster():
    """Generar timestamp único para forzar rebuild"""
    timestamp = int(time.time())
    random_id = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"FORCE_UPDATE_{timestamp}_{random_id}"

# FORZAR ACTUALIZACIÓN INMEDIATA
CACHE_BUSTER = generate_cache_buster()
BUILD_VERSION = f"2025-07-24-22:15-EMERGENCY-FIX"

print(f"FORCED UPDATE: {CACHE_BUSTER}")
print(f"BUILD VERSION: {BUILD_VERSION}")

# Escribir a archivo para verificar
with open("DEPLOYMENT_VERIFICATION.txt", "w") as f:
    f.write(f"DEPLOYMENT_TIME: {time.ctime()}\n")
    f.write(f"CACHE_BUSTER: {CACHE_BUSTER}\n")
    f.write(f"BUILD_VERSION: {BUILD_VERSION}\n")
    f.write("STATUS: FORCED_DEPLOYMENT_ACTIVE\n")

print("Cache buster creado - REBUILD INMEDIATO REQUERIDO")