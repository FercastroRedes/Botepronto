# Plantilla Reel ficha de paleta (motion 2D, 18 s)

Siete escenas fijas: logo con onda de choque, entrada de paleta + título, 2 callouts con número, barras + specs, foto detalle con medida, precio + CTA + logo y, si `escenas` trae un 9.º valor, placa final con el logo grande (onda de choque y rebote) antes del fundido a negro. Para sacarla, borrar el último valor de `escenas` y poner `duracion` igual al anterior. Barrido rojo en los cortes 2,0 / 9,6 / 12,0 / 15,0 s y desenfoque de movimiento en los pases de cámara.

## Archivos
- `reel.html`: diseño y animación (función `render(t)`). No hace falta tocarlo para otra paleta.
- `params/<paleta>.json`: todo lo variable (fotos, título, callouts, barras, specs, medida, precio, CTA, envíos, tiempos de escena, sonidos, `version` oscuro/claro).
- `render.js`: captura con Playwright y arma el MP4 con ffmpeg.

## Otra paleta
1. Recortar la foto Frente con `assets/recortes/cut.py` y limpiar el corazón (ver regla de recortes). Guardar en `assets/recortes/`.
2. Copiar `params/metal-passion.json` a `params/<nueva>.json` y cambiar textos, números, precio (de la planilla) y rutas. `salida` es la ruta sin extensión dentro de /mnt/project-files.
3. `callouts[].punto` = [x, y] del punto marcado sobre la foto, en proporción (0 a 1) del ancho y alto del recorte.
4. Probar cuadros sueltos: `node render.js params/<nueva>.json --draft --cuadros 30,100,200,330,400,510`
5. Borrador: `node render.js params/<nueva>.json --draft` (540x960, ~20 s de render)
6. Final: `node render.js params/<nueva>.json --final` (1080x1920, H.264 CRF 18)

Opciones: `--sin-audio` saltea la mezcla. Siempre deja además `<salida>_sin_audio.mp4`.

## Audio
Los sonidos salen de /mnt/project-files/audio/ en los tiempos de `sonidos` (con `vol` y `largo` opcional para recortar), normalizado a -14 LUFS. Licencias sin verificar (ver audio/licencias.md): solo para revisión interna hasta confirmarlas.

Requiere: Node con Playwright global (/opt/node22/lib/node_modules), ffmpeg, red a fonts.googleapis.com (tipografía Barlow Condensed).
