# Instagram Local (proyecto educativo)

Clon de Instagram con propósitos educativos para practicar Django y los conocimientos
del máster de desarrollo fullstack de Conquer Blocks.

## Stack tecnológico

- **Backend:** Python 3.14.4 + Django 6.1.3
- **Base de datos:** SQLite3
- **Frontend:** Django templates + Bootstrap 5 (CDN) + django-crispy-forms + Google Fonts (Poppins/Inter)
- **Estética:** degradado Instagram, header sticky, cards con hover, botones píldora, imágenes cuadradas 1:1
- **Dependencias de desarrollo:** django-extensions, crispy-bootstrap5
- **Infraestructura:** Linux Ubuntu (entorno local)

## Apps y modelos

| App | Modelos |
|-----|---------|
| `users` | `User` (custom: login por email, `username=None`, `display_name`) |
| `profiles` | `UserProfile` (OneToOne con User, foto de perfil), `Follow` (seguidores) |
| `posts` | `Post` (con likes/dislikes), `Like`, `Comment` (con respuestas, likes y dislikes) |
| `notifications` | `Notification` (destinatario, actor, tipo, leída) |

## Funcionalidades implementadas

- Registro (`UserCreationForm`, contraseña hasheada), login por email y logout.
- Home = feed de posts de cuentas seguidas (estado vacío con CTA si no sigues a nadie).
- Publicar posts con imagen; listado, detalle y grid en el perfil.
- Interacciones: like/dislike (👍/👎) en posts y comentarios, accesibles desde el feed y el detalle; comentarios con respuestas anidadas.
- Likes/dislikes vía AJAX (sin recarga de página).
- Carga asincrónica de publicaciones (botón "Cargar más" en el feed).
- Contador de like/dislike oculto cuando no hay reacciones (mejor UX/UI).
- Seguimiento: seguir/dejar de seguir, listado de usuarios (excluye superusuarios y al propio), perfil público, y listas de followers/following en tu perfil.
- Notificaciones de like/dislike/comentario/respuesta, con badge de no leídas en el header.
- Perfil editable (foto, bio, ubicación, fecha) y auto-creado por señal `post_save`.
- Nombres/apellidos mostrados en toda la app (`display_name`, con fallback al email).
- Avatar del autor en posts y comentarios.
- Botón Follow junto al autor en posts y comentarios (solo "Follow"; el "Unfollow" queda en Users/perfil público).
- Página de aviso legal y formulario de contacto (Name, Email, Subject, Message).
- Internacionalización EN/ES con selector de idioma en el header.
- Diseño responsivo (adaptable a móvil/tablet).
- Mensajes flash de Django renderizados en el layout.

> Crear superusuario: `python manage.py createsuperuser` (pide **email**, no username).

## Configuración del entorno

```bash
python3 -m venv env
source env/bin/activate
pip install -r requeriments.txt
python manage.py migrate
python manage.py runserver
```

## Variables de entorno (opcionales)

| Variable | Default |
|----------|---------|
| `DJANGO_SECRET_KEY` | clave insecure de desarrollo |
| `DJANGO_DEBUG` | `True` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` |

## Estructura

```
instagram/
├── manage.py
├── requeriments.txt
├── instagram/          # paquete de configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── views.py        # vistas generales (home, login, register, ...)
├── users/              # User custom + RegistrationForm
├── profiles/           # UserProfile + Follow + signals + ProfileForm
├── posts/              # Post + Like + Comment
├── notifications/      # Notification (likes/comentarios/respuestas)
├── templates/          # templates globales (general/, profiles/, _includes/)
├── static/             # css/, js/
├── locale/             # traducciones (es/)
├── media/              # archivos subidos (fotos de perfil, posts)
```

## Créditos y agradecimientos

- **Creador:** Javier Esquivel
- **Proyecto:** Instagram Local (clon educativo) para el máster de desarrollo fullstack de Conquer Blocks.
- **Tecnologías:** Python/Django, Bootstrap 5, django-crispy-forms, SQLite.
- **Agradecimientos:** a Conquer Blocks y a todo el equipo docente por la formación y el acompañamiento en el proceso de aprendizaje.
- **Nota:** aplicación con fines exclusivamente académicos.
