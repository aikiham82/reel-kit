# Hacer reels con Claude en Windows

Claude ve tus vídeos, elige los mejores momentos, los corta en vertical y monta el reel. Todo pasa en tu PC; tú solo hablas con Claude en la app.

Los nombres de los menús pueden cambiar un poco según la versión de Claude Desktop.

## 1. Instalar programas (una sola vez)

Abre **PowerShell** y pega esto:

```text
winget install OpenJS.NodeJS.LTS Gyan.FFmpeg Python.Python.3.12 Git.Git
```

Cierra PowerShell, ábrelo otra vez y pega:

```text
pip install numpy
git clone https://github.com/Abraham-Hdez/reel-kit.git $HOME\reel-kit
cd $HOME\reel-kit
npm install
```

La carpeta queda en `C:\Users\<tu usuario>\reel-kit`.

## 2. Claude Desktop

1. Descarga e instala Claude Desktop desde https://claude.ai/download y entra con tu cuenta.
2. **Ajustes → Extensiones → Explorar extensiones**: instala **Desktop Commander**. Permite a Claude ejecutar programas y leer archivos de tu PC.
3. **Ajustes → Capacidades**: activa la ejecución de código y luego, en **Skills**, sube el archivo `reels-skill.zip` (descárgalo de https://github.com/Abraham-Hdez/reel-kit/releases/latest, o créalo con `python tools\reel.py skill-zip`, queda en `dist\`).

## 3. Hacer un reel

1. Copia tus vídeos a una carpeta, por ejemplo `C:\Users\<tu usuario>\Videos\clase-sabado`.
2. Abre un chat nuevo en Claude Desktop y escribe algo así:

```text
Usa la skill de reels. El proyecto está en C:\Users\<tu usuario>\reel-kit y los vídeos en C:\Users\<tu usuario>\Videos\clase-sabado. Haz un reel de yoga de 30 segundos para anunciar la clase abierta del sábado 10 a las 10:00 en Murcia. Música: C:\Users\<tu usuario>\Music\calma.mp3. Al final pon "Reserva tu plaza" y mi Instagram @miestudio.
```

3. Claude te pedirá permiso para usar Desktop Commander: acepta.
4. El reel sale en `reel-kit\out\`. Para cambiar algo, díselo: "quita el tercer clip", "sin música", "más corto", "que el texto diga...".

## Consejos

- Tarda unos minutos, sobre todo con vídeos 4K. No cierres Claude Desktop mientras trabaja.
- Usa música tuya o con licencia para redes sociales.
- El estilo por defecto es suave: posturas enteras, fundidos, música tranquila. Si quieres otro, díselo a Claude y que lo apunte para la próxima vez.

## Desde el móvil

El móvil sirve para pedirle cosas a Claude, pero el trabajo lo hace el PC: tiene que estar encendido con Claude Desktop abierto.
