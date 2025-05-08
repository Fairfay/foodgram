# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://tychindas.sytes.net',
    'http://tychindas.sytes.net',
    'https://www.tychindas.sytes.net',
    'http://www.tychindas.sytes.net',
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'https://tychindas.sytes.net',
    'http://tychindas.sytes.net',
    'https://www.tychindas.sytes.net',
    'http://www.tychindas.sytes.net',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Session settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax' 