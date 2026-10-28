# Música de fondo propia Botepronto (sintetizada por código)

Generada el 2026-10-28 con `generar_musica.py` (Python + numpy). Todo sale de osciladores y ruido del propio script, sin samples, loops ni presets de terceros: es de Botepronto, libre de derechos, apta para uso comercial en Instagram, TikTok y YouTube sin atribución. Sin Content ID.

Formato: WAV 48 kHz, 16 bit, estéreo, nivel de fondo ~-19 LUFS (pico -6 a -10 dBFS), pensado para ir debajo de los efectos.

| Tema | Archivos | Licencia | Tempo | Duración | Carácter |
|---|---|---|---|---|---|
| venta | venta_loop.wav, venta_cierre.wav | propio, libre de derechos | 116 bpm | 18,6 s loop / 21,2 s cierre | beat electrónico con bombo en negras, bajo con bombeo, acordes menores cortos |
| comunidad | comunidad_loop.wav, comunidad_cierre.wav | propio, libre de derechos | 96 bpm | 17,5 s / 20,1 s | piano eléctrico, shaker y rim, progresión mayor, más cálido |
| b2b (clubes / profes) | b2b_loop.wav, b2b_cierre.wav | propio, libre de derechos | 92 bpm | 18,3 s / 20,9 s | colchón sobrio + arpegio pulsado, percusión mínima |
| ofertas / combos | ofertas_loop.wav, ofertas_cierre.wav | propio, libre de derechos | 124 bpm | 17,4 s / 20,0 s | más urgente: semicorcheas, filtro que se abre, subida al final del loop |

- `_loop.wav`: loop exacto para `mezclar.js --musica` (lo repite y le hace fundido de entrada y salida).
- `_cierre.wav`: tema con golpe final y cola, para cuando el Reel termina con la placa del logo.
- `<tema>_muestra.mp3`: escucha rápida (versión cierre). `demo_mezcla_thunder_*.mp3`: efectos del Reel Thunder + música a 0,8.

Mezcla recomendada: `node mezclar.js params/<x>-final.json --musica audio/propios/musica/<tema>_loop.wav --vol-musica 0.8`. Con 0,8 la música queda unos 10 dB debajo de los efectos; el 0,35 por defecto la deja casi inaudible con estos archivos.
