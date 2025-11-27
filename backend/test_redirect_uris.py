"""
Script para probar diferentes redirect_uri y ver cuál funciona
"""
import requests
from urllib.parse import urlencode

# Datos proporcionados por la universidad
CLIENT_ID = "3d5ee5aa-404d-49ee-a7cd-025d90e4eeb4"
TENANT_ID = "eeefd6bf-96ae-45fe-ab13-8ff7fd3e5801"

# URLs a probar
redirect_uris = [
    "http://localhost:8000/api/v1/sso/callback",
    "http://127.0.0.1:8000/api/v1/sso/callback",
    "http://localhost:3000/callback",
    "https://apps.unitecnologica.edu.co/tooli_ia/api/v1/sso/callback",
]

print("🔍 PROBANDO REDIRECT URIs DISPONIBLES EN AZURE AD\n")
print("=" * 70)

for redirect_uri in redirect_uris:
    auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
    
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": "openid profile email",
        "state": "test123"
    }
    
    full_url = f"{auth_url}?{urlencode(params)}"
    
    print(f"\n📌 Testing: {redirect_uri}")
    print(f"   URL: {full_url[:100]}...")
    
    # Intentar hacer request
    try:
        response = requests.get(full_url, allow_redirects=False, timeout=5)
        
        if response.status_code == 302:
            print(f"   ✅ REDIRECT OK (302) - Esta URL PUEDE estar registrada")
        elif response.status_code == 200:
            print(f"   ⚠️  OK (200) - Probablemente muestra login")
        else:
            print(f"   ❌ Error ({response.status_code})")
            
    except Exception as e:
        print(f"   ⚠️  No se pudo verificar: {str(e)[:50]}")

print("\n" + "=" * 70)
print("\n💡 RECOMENDACIÓN:")
print("1. Abre tu navegador")
print("2. Ve a: http://localhost:8000/api/v1/sso/providers")
print("3. Copia la URL que aparece y ábrela en el navegador")
print("4. Si te lleva a Microsoft login = ✅ Funciona")
print("5. Si da error redirect_uri_mismatch = ❌ No está registrada")
