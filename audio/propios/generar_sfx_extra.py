# Efectos extra propios (síntesis numpy). Uso: python3 generar_sfx_extra.py <carpeta>
import numpy as np, wave, sys, os
SR = 48000; rng = np.random.default_rng(5); out = sys.argv[1]
def tt(d): return np.arange(int(SR*d))/SR
def bpf(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    return np.fft.irfft(X/np.sqrt(1+(f/hi)**8)/np.sqrt(1+(lo/np.maximum(f, 1))**8), len(x))
def save(name, x):
    x = x-np.mean(x); x = x/np.max(np.abs(x))*0.89; n = int(SR*0.008); x[-n:] *= np.linspace(1, 0, n)
    d = (x*32767).astype('<i2')
    with wave.open(os.path.join(out, name), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.stack([d, d], 1).tobytes())
    return x
S = {}
# golpe_pelota: "poc" de pala contra pelota: modos huecos agudos que caen rápido + chasquido
n = tt(0.22)
body = sum(a*np.sin(2*np.pi*f*n*(1+0.04*np.exp(-n/0.01)))*np.exp(-n/d) for f, a, d in ((1150, 1, 0.03), (1900, 0.5, 0.018), (620, 0.6, 0.04)))
snap = bpf(rng.standard_normal(len(n)), 2500, 9000)*np.exp(-n/0.0025)*1.5
S['golpe_pelota.wav'] = save('golpe_pelota.wav', np.tanh(1.5*(body+snap)))
# pique_pelota: rebote en el piso, más grave y con eco corto de cancha
n = tt(0.5); x = np.zeros(len(n))
for at, a in ((0, 1), (0.055, 0.25), (0.11, 0.1)):
    i = int(SR*at); m = tt(0.5-at)
    x[i:] += a*(np.sin(2*np.pi*420*m)*np.exp(-m/0.025)+0.6*np.sin(2*np.pi*780*m)*np.exp(-m/0.015)+bpf(rng.standard_normal(len(m)), 1500, 6000)*np.exp(-m/0.003))
S['pique_pelota.wav'] = save('pique_pelota.wav', x)
# ding_precio: campanita limpia de dos notas (Mi6 -> La6) para cuando aparece el precio
n = tt(1.2)
def bell(f): return sum(np.sin(2*np.pi*f*r*n)*np.exp(-n/(0.5/r**0.6))/(k+1) for k, r in enumerate((1, 2.0, 3.01, 4.2)))
x = bell(1318.5); i = int(SR*0.12); x[i:] += 1.1*bell(1760)[:len(n)-i]
S['ding_precio.wav'] = save('ding_precio.wav', x)
# click_ui: tic seco tipo interfaz, para cambiar dato o viñeta
n = tt(0.06)
S['click_ui.wav'] = save('click_ui.wav', (np.sin(2*np.pi*2400*n)*np.exp(-n/0.004)+0.4*bpf(rng.standard_normal(len(n)), 3000, 12000)*np.exp(-n/0.0015)))
gap = np.zeros(int(SR*0.6))
save('_muestra_extra.wav', np.concatenate([np.concatenate([S[k], gap]) for k in ('golpe_pelota.wav', 'pique_pelota.wav', 'golpe_pelota.wav', 'ding_precio.wav', 'click_ui.wav', 'click_ui.wav', 'click_ui.wav')]))
