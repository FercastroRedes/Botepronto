// Uso: node render.js params/metal-passion.json [--draft|--final] [--cuadros 30,90,...] [--sin-audio]
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const path=require('path'),fs=require('fs'),{execFileSync}=require('child_process');
const ROOT='/mnt/project-files';
const args=process.argv.slice(2);
const pfile=args.find(a=>a.endsWith('.json'));
const final=args.includes('--final');
const ci=args.indexOf('--cuadros'), only=ci>=0?args[ci+1].split(',').map(Number):null;
const conAudio=!args.includes('--sin-audio');
const P=JSON.parse(fs.readFileSync(path.resolve(__dirname,pfile),'utf8'));
const S=final?1:0.5, W=1080*S, H=1920*S, fps=P.fps, N=Math.round(P.duracion*fps);
const url=f=>'file://'+path.join(ROOT,f).split('/').map(encodeURIComponent).join('/').replace(/%3A/g,':');
const cfg={...P,fotos:Object.fromEntries(Object.entries(P.fotos).map(([k,v])=>[k,url(v)]))};
const base=path.join(ROOT,P.salida+(final?'_final':'_borrador'));
const tmp=fs.mkdtempSync('/tmp/reel-');
(async()=>{
  const br=await chromium.launch();
  const pg=await br.newPage({viewport:{width:W,height:H}});
  await pg.goto('file://'+path.join(__dirname,'reel.html'));
  await pg.evaluate(async([c,s])=>{init(c);document.getElementById('stage').style.transform=`scale(${s})`;
    await document.fonts.ready;await Promise.all([...document.images].filter(i=>i.src).map(i=>i.decode()))},[cfg,S]);
  const list=only||[...Array(N).keys()], t0=Date.now();
  for(const f of list){
    await pg.evaluate(t=>render(t),f/fps);
    await pg.screenshot({path:only?`${base}_cuadro${f}.jpg`:`${tmp}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});
  }
  await br.close();
  console.log('cuadros',list.length,'seg',(Date.now()-t0)/1000);
  if(only) return;
  const mudo=`${base}_sin_audio.mp4`;
  execFileSync('ffmpeg',['-y','-loglevel','error','-framerate',String(fps),'-i',`${tmp}/f%04d.jpg`,'-c:v','libx264','-preset',final?'slow':'veryfast',
    '-crf',final?'18':'23','-pix_fmt','yuv420p','-r',String(fps),'-movflags','+faststart',mudo]);
  if(conAudio&&P.sonidos&&P.sonidos.length){
    const inp=[],fl=[];
    P.sonidos.forEach((s,i)=>{inp.push('-i',path.join(ROOT,s.archivo));
      const largo=s.largo?`atrim=0:${s.largo},afade=t=out:st=${Math.max(0,s.largo-.3).toFixed(2)}:d=0.3,`:'';
      const ms=Math.round(s.t*1000);
      fl.push(`[${i+1}:a]aformat=sample_rates=48000:channel_layouts=stereo,${largo}volume=${s.vol??1},adelay=${ms}|${ms}[s${i}]`)});
    const mix=P.sonidos.map((_,i)=>`[s${i}]`).join('')+`amix=inputs=${P.sonidos.length}:normalize=0,apad,atrim=0:${P.duracion},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]`;
    execFileSync('ffmpeg',['-y','-loglevel','error','-i',mudo,...inp,'-filter_complex',fl.join(';')+';'+mix,'-map','0:v','-map','[a]',
      '-c:v','copy','-c:a','aac','-b:a','160k','-t',String(P.duracion),'-movflags','+faststart',`${base}.mp4`]);
  }
  fs.rmSync(tmp,{recursive:true,force:true});
  console.log('listo',base+'.mp4');
})();
