# Música de fondo propia Botepronto: síntesis pura con numpy (sin samples de terceros).
# Uso: python3 generar_musica.py [carpeta_salida]
# Por cada tema deja <tema>_loop.wav (loop exacto, para mezclar.js --musica, que lo repite y le hace fade)
# y <tema>_cierre.wav (cuerpo + golpe final con cola, ~21 s).
import numpy as np, wave, sys, os
SR = 48000
out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(11)

def tt(d): return np.arange(int(SR*d))/SR
def hz(n): return 440*2**((n-69)/12)
def fft_filt(x, lo=0, hi=SR/2, slope=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    g = np.ones_like(f)
    if hi < SR/2: g *= 1/np.sqrt(1+(f/hi)**(2*slope))
    if lo > 0: g *= 1/np.sqrt(1+(lo/np.maximum(f,1))**(2*slope))
    return np.fft.irfft(X*g, len(x))
def reverb(x, dur=1.6, wet=0.25, lp=5000):
    n = int(SR*dur); ir = rng.standard_normal(n)*np.exp(-tt(dur)/(dur/6.9)); ir = fft_filt(ir, 200, lp)
    L = len(x)+n; y = np.fft.irfft(np.fft.rfft(x, L)*np.fft.rfft(ir, L), L)[:len(x)]
    return x + wet*y/np.max(np.abs(y)+1e-9)*np.max(np.abs(x))
def add(buf, x, at):
    i = int(SR*at)
    if i >= len(buf): return
    m = min(len(x), len(buf)-i); buf[i:i+m] += x[:m]
def adsr(n, a=0.005, r=0.05, d=None):
    x = np.arange(n)/SR; e = np.minimum(x/max(a,1e-4), 1)
    if d: e *= np.exp(-x/d)
    rel = int(SR*r); e[-rel:] *= np.linspace(1, 0, rel); return e

# --- instrumentos ---
def kick(v=1.0, dec=0.28, top=150):
    n = tt(0.45); f = 44+(top-44)*np.exp(-n/0.035)
    b = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-n/dec)
    c = fft_filt(rng.standard_normal(len(n)), 0, 3000)*np.exp(-n/0.004)*0.25
    return v*np.tanh(1.6*(b+c))
def clap(v=1.0):
    n = tt(0.3); x = np.zeros(len(n)); ns = fft_filt(rng.standard_normal(len(n)), 900, 3500, 2)
    for k, o in enumerate((0, 0.011, 0.022)):
        e = np.zeros(len(n)); i = int(SR*o); e[i:] = np.exp(-np.arange(len(n)-i)/SR/(0.09 if k == 2 else 0.008)); x += ns*e
    return v*x/np.max(np.abs(x))*0.8
def hat(v=1.0, dec=0.035):
    n = tt(0.15); return v*0.35*fft_filt(rng.standard_normal(len(n)), 7000)*np.exp(-n/dec)
def shaker(v=1.0):
    n = tt(0.12); e = np.sin(np.pi*n/0.12)**2
    return v*0.3*fft_filt(rng.standard_normal(len(n)), 5000, 11000)*e
def rim(v=1.0):
    n = tt(0.08); return v*0.5*(np.sin(2*np.pi*1700*n)+0.5*np.sin(2*np.pi*820*n))*np.exp(-n/0.012)
def additive(f, d, cut=8, nh=24, det=(0,), dec_h=None, a=0.005, r=0.05, d_env=None):
    n = tt(d); x = np.zeros(len(n))
    for dt in det:
        ff = f*2**(dt/1200)
        for k in range(1, nh+1):
            if k*ff > SR/2.2: break
            amp = (1/k)*np.exp(-(k/cut)**2)
            h = np.sin(2*np.pi*k*ff*n+rng.random()*6.28)
            if dec_h: h *= np.exp(-n*k/dec_h)
            x += amp*h
    return x*adsr(len(n), a, r, d_env)/len(det)
def epiano(f, d, v=1.0):
    n = tt(d); I = 1.8*np.exp(-n/0.25)
    x = np.sin(2*np.pi*f*n+I*np.sin(2*np.pi*f*n)) + 0.25*np.sin(2*np.pi*f*4.0*n)*np.exp(-n/0.08)
    return v*x*adsr(len(n), 0.004, 0.12, 0.9)*(1+0.12*np.sin(2*np.pi*4.5*n))
def pluck(f, d, v=1.0): return v*additive(f, d, cut=14, nh=20, dec_h=1.2, a=0.002, r=0.05, d_env=0.35)
def pad(f, d, v=1.0, cut=5, a=0.12): return v*additive(f, d, cut=cut, nh=14, det=(-9, 0, 8), a=a, r=0.6)
def bass(f, d, v=1.0, cut=5): return v*additive(f, d, cut=cut, nh=16, a=0.004, r=0.03, d_env=0.6)

def chord(root, kind):
    return [root+i for i in {'m': (0,3,7,10), 'M': (0,4,7,11), 'M9': (0,4,7,14), 'm9': (0,3,7,14), 's': (0,5,7,10)}[kind]]

# --- temas ---
TEMAS = {
 # venta: enérgico, kick en negras, bajo a contratiempo con bombeo, stabs menores
 'venta':    dict(bpm=116, prog=[(57,'m'),(53,'M'),(48,'M9'),(55,'s')], style='venta'),
 # comunidad: cálido, piano eléctrico, shaker y rim, progresión mayor
 'comunidad':dict(bpm=96,  prog=[(48,'M9'),(57,'m9'),(53,'M9'),(55,'s')], style='comunidad'),
 # b2b clubes/profes: sobrio, pad + arpegio pulsado, kick suave
 'b2b':      dict(bpm=92,  prog=[(50,'m9'),(46,'M9'),(53,'M9'),(48,'M9')], style='b2b'),
 # ofertas/combos: urgente, semicorcheas, apertura de filtro y subida antes del cierre
 'ofertas':  dict(bpm=124, prog=[(52,'m'),(48,'M'),(55,'M9'),(50,'s')], style='ofertas'),
}

def render(nombre, bpm, prog, style, bars):
    b = 60/bpm; bar = 4*b; L = bars*bar
    drums = np.zeros(int(SR*(L+3))); bassb = np.zeros_like(drums); harm = np.zeros_like(drums); lead = np.zeros_like(drums)
    side = np.ones_like(drums)
    for i in range(bars):
        t0 = i*bar; root, kind = prog[i % len(prog)]; ch = chord(root, kind)
        for q in range(4):
            tq = t0+q*b
            if style in ('venta', 'ofertas'):
                add(drums, kick(1.0), tq)
                n0 = int(SR*tq); m = int(SR*b*0.9); side[n0:n0+m] = np.minimum(side[n0:n0+m], 1-0.6*np.exp(-tt(b*0.9)[:len(side[n0:n0+m])]/0.09))
                add(drums, hat(0.9), tq+b/2)
                if q in (1, 3): add(drums, clap(0.7), tq)
                if style == 'ofertas':
                    for s in (0.25, 0.75): add(drums, hat(0.45, 0.02), tq+s*b)
                f = hz(root-12) if style == 'venta' else hz(root-12)*(1 if q % 2 == 0 else 2)
                add(bassb, bass(f, b*0.45, 1.0, 6), tq+b/2)
                if style == 'ofertas': add(bassb, bass(hz(root-12), b*0.22, 0.7, 6), tq)
            elif style == 'comunidad':
                if q in (0, 2): add(drums, kick(0.75, 0.22, 120), tq)
                if q in (1, 3): add(drums, rim(0.6), tq)
                for s in (0, 0.5): add(drums, shaker(0.8 if s else 0.5), tq+s*b)
                if q in (0, 2): add(bassb, bass(hz(root-12), b*2.0, 0.9, 3), tq)
            else:  # b2b
                if q in (0, 2): add(drums, kick(0.6, 0.2, 110), tq)
                add(drums, hat(0.35, 0.025), tq+b/2)
                if q == 0: add(bassb, bass(hz(root-12), bar+0.1, 0.8, 2.5), tq)
        # armonía
        if style == 'venta':
            for st in (0, 1.5, 3):
                for nn in ch: add(harm, additive(hz(nn), b*0.35, cut=9, nh=16, det=(-7, 7), a=0.003, r=0.06, d_env=0.25)*0.35, t0+st*b)
            for nn in ch[:3]: add(harm, pad(hz(nn+12), bar+0.6, 0.12, 4), t0)
        elif style == 'ofertas':
            sweep = min(1, (i+1)/bars)
            for k in range(8):
                nn = ch[k % 4]+12; add(lead, pluck(hz(nn), b*0.4, 0.28), t0+k*b/2)
            for nn in ch: add(harm, pad(hz(nn), bar+0.6, 0.13, 2.5+6*sweep), t0)
        elif style == 'comunidad':
            for st in (0, 1.5, 2.5):
                for nn in ch: add(harm, epiano(hz(nn), b*1.4, 0.16), t0+st*b)
            for nn in ch[:3]: add(harm, pad(hz(nn), bar+0.6, 0.07, 3, 0.2), t0)
            mel = [ch[2]+12, ch[3]+12, ch[1]+12, ch[2]+12]
            for k, nn in enumerate(mel): add(lead, pluck(hz(nn), b*0.7, 0.12), t0+(k*1+0.5)*b)
        else:
            for nn in ch: add(harm, pad(hz(nn), bar+0.6, 0.16, 3, 0.2), t0)
            arp = [ch[0], ch[1], ch[2], ch[3]]*2
            for k, nn in enumerate(arp): add(lead, pluck(hz(nn+12), b*0.45, 0.13), t0+k*b/2)
    if style == 'ofertas':  # subida de ruido en el último compás del loop
        n = tt(bar); p = n/bar; rs = fft_filt(rng.standard_normal(len(n)), 2000, 9000)*p**2*0.15; add(lead, rs, L-bar)
    bassb *= side; harm *= side**0.6
    harm = reverb(harm, 1.8, 0.35); lead = reverb(lead, 1.4, 0.3)
    dg = 0.9 if style in ('venta', 'ofertas') else 0.6
    mix = drums*dg + bassb*0.8 + harm + lead
    mix = fft_filt(mix, 30)
    loop = mix[:int(SR*L)].copy()
    # cola de reverb del final del loop sumada al arranque para que el empalme no corte
    tail = mix[int(SR*L):int(SR*(L+1.5))]; loop[:len(tail)] += tail*np.linspace(1, 0, len(tail))
    # versión con cierre: cuerpo + golpe final (kick + acorde de tónica) con cola de 2,5 s
    root, kind = prog[0]; fin = np.zeros(int(SR*2.6))
    add(fin, kick(1.0, 0.35), 0)
    for nn in chord(root, kind): add(fin, pad(hz(nn), 2.6, 0.18, 4)*np.exp(-tt(2.6)/0.9), 0)
    add(fin, bass(hz(root-12), 2.0, 0.9, 3), 0)
    fin = reverb(fin, 2.0, 0.4); fin *= np.linspace(1, 0, len(fin))**1.5
    body = mix[:int(SR*L)].copy(); n = int(SR*0.05); body[-n:] *= np.linspace(1, 0.6, n)
    cierre = np.concatenate([body, fin])
    return loop, cierre

def lvl(x, rms_db=-20.0, peak_db=-3.0):
    x = np.tanh(x/np.max(np.abs(x))*1.3)
    x *= 10**(rms_db/20)/np.sqrt(np.mean(x**2))
    pk = np.max(np.abs(x)); lim = 10**(peak_db/20)
    if pk > lim: x = np.where(np.abs(x) > lim*0.8, np.sign(x)*(lim*0.8+(lim*0.2)*np.tanh((np.abs(x)-lim*0.8)/(lim*0.2))), x)
    return x
def save(path, x):
    d = (np.clip(x, -1, 1)*32767).astype('<i2'); st = np.stack([d, d], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

if __name__ == '__main__':
    os.makedirs(out, exist_ok=True)
    for nombre, cfg in TEMAS.items():
        bars = int(18.8//(4*60/cfg['bpm']))
        loop, cierre = render(nombre, cfg['bpm'], cfg['prog'], cfg['style'], bars)
        save(os.path.join(out, f'{nombre}_loop.wav'), lvl(loop))
        save(os.path.join(out, f'{nombre}_cierre.wav'), lvl(cierre))
        print(nombre, cfg['bpm'], 'bpm', bars, 'compases', round(len(loop)/SR, 2), 's loop /', round(len(cierre)/SR, 2), 's cierre')
