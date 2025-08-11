from django.contrib.auth.hashers import make_password

# Generar hash para la contraseña "admin"
password_hash = make_password('admin123')
print(password_hash)