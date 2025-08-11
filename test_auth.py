import sys

print("Python path:", sys.path)
print("Diretório atual:", __file__)

try:
    print("1. Testando config.database...")
    from config.database import get_db_connection

    print("✅ config.database OK")

    print("2. Testando repositories...")
    from repositories.user_repositories import UserRepository

    print("✅ repositories OK")

    print("3. Testando services...")
    from services.auth_service import AuthService

    print("✅ services OK")

    print("4. Testando auth completo...")
    from routes.auth import router

    print("✅ auth.py OK")

except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback

    traceback.print_exc()