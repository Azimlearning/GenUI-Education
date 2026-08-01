# ruff: noqa: E501
"""The deterministic Newton's-cannonball orbital-motion simulation and plan."""

from schemas.plan import ArtifactPlan, Variable

ORBITAL_SIM_ID = 'newton_cannonball_orbit_v1'

ORBITAL_SIM_HTML = (
    r'''<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Newton's Cannonball Orbit Lab</title><style>
:root{--ink:#26362f;--dim:#63736c;--line:#dce7dc;--teal:#078d80;--violet:#6f5ba6;--gold:#c68a00;--paper:#fff}*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden}body{color:var(--ink);background:#f6f9f4;font:14px/1.35 system-ui,sans-serif}main{height:100%;padding:14px;display:grid;grid-template-rows:auto auto auto auto minmax(0,1fr);gap:9px;background:linear-gradient(135deg,#fcfefb,#f4f8f1)}header{display:flex;align-items:center;gap:14px}header>div{min-width:0}.kicker{margin:0 0 3px;color:var(--teal);font-size:10px;font-weight:900;letter-spacing:.13em}h1{margin:0;color:#b67a00;font:700 clamp(20px,2.1vw,29px)/1.08 Georgia,serif;letter-spacing:-.02em}button{min-height:40px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);font-weight:800;cursor:pointer}.hint{margin:0;padding:0 2px;color:#99433e;font-weight:750}.note{padding:8px 11px;border:1px solid #e9cf88;border-radius:10px;background:linear-gradient(90deg,#fff9e9,#fffdf8)}.note b{color:#a76e00}.steps{display:flex;gap:8px}.step{flex:1;min-width:0;min-height:52px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#fff;box-shadow:0 2px 0 #eaf0e9;font-size:12px}.step b{display:inline-grid;place-items:center;width:19px;height:19px;margin-right:4px;border-radius:50%;background:var(--violet);color:#fff}.lab{min-height:0;display:grid;grid-template-columns:minmax(0,1.7fr) minmax(250px,.72fr);gap:12px}.stage,.panel{min-height:0;border:1px solid var(--line);border-radius:16px;background:#fff}.stage{position:relative;overflow:hidden;min-height:360px;display:grid;place-items:center;background:#0b1020;box-shadow:inset 0 0 0 1px #fff}#sky{display:block;width:100%;height:100%;object-fit:contain}.stage:before{content:'ORBIT SIMULATOR';position:absolute;left:16px;top:13px;z-index:2;color:#8fb7d6;font-size:10px;font-weight:900;letter-spacing:.12em}
.panel{padding:12px;display:grid;align-content:start;gap:10px;background:linear-gradient(#fff,#fbfdf9);box-shadow:inset 0 0 0 1px #fff}.card{padding:10px;border:1px solid var(--line);border-radius:11px;background:linear-gradient(135deg,#fff,#f8fbf7)}.label{color:var(--dim);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.value{margin-top:3px;font-size:20px;font-weight:800;color:var(--teal);font-variant-numeric:tabular-nums}.slider{width:100%;margin-top:8px;accent-color:#078d80}.readrow{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.typecard{border-color:#c9bff0;background:linear-gradient(135deg,#f6f3ff,#fbfaff)}.typecard .value{color:#5b45a0;font-size:17px}.legend{display:grid;gap:5px;font-size:11px;color:var(--dim)}.legend i{display:inline-block;width:22px;height:0;margin-right:7px;vertical-align:middle;border-top:3px solid}.btns{display:flex;gap:8px}.btns button{flex:1;box-shadow:0 2px 0 #dce8db}.launch{background:#0a776b;color:#fff;border-color:#0a776b;box-shadow:0 3px 0 #075247}.launch:active{transform:translateY(2px);box-shadow:0 1px 0 #075247}
@media(max-width:760px){main{padding:9px;gap:7px}.steps{display:none}.lab{grid-template-columns:1fr}.stage{min-height:300px}.panel{padding:8px}}
</style></head><body><main>
<header><div><p class='kicker'>INTERACTIVE PHYSICS SIMULATION</p><h1>Newton's Cannonball: Orbits and Escape</h1></div></header>
<p class='hint'>Try this: raise the launch speed and press Launch. Watch the path curve from falling back, to a circle, to an ellipse, to escaping Earth.</p>
<div class='note'><b>Key idea:</b> An orbit is just constant falling. Gravity pulls the cannonball toward Earth the whole time; with enough sideways speed it keeps missing the ground and circles instead.</div>
<div class='steps'><div class='step'><b>1</b>Set a low launch speed and press Launch.</div><div class='step'><b>2</b>Raise the speed toward 7.9 km/s for a circular orbit.</div><div class='step'><b>3</b>Go higher for a stretched ellipse.</div><div class='step'><b>4</b>Reach 11.2 km/s to escape Earth.</div></div>
<section class='lab'><div class='stage'><canvas id='sky'></canvas></div><aside class='panel'>
<div class='card'><div class='readrow'><div class='label'>Launch speed</div><div id='speedVal' class='value'>7.9 km/s</div></div><input id='speed' class='slider' type='range' min='1' max='15' step='0.1' value='7.9'></div>
<div class='card typecard'><div class='label'>Trajectory</div><div id='typeVal' class='value'>Press Launch</div></div>
<div class='card'><div class='readrow'><div class='label'>Peak altitude</div><div id='altVal' class='value'>-</div></div></div>
<div class='card'><div class='label'>Path colour</div><div class='legend'><div><i style='border-color:#e2795f'></i>falls back to Earth</div><div><i style='border-color:#3fb6a2'></i>circular / elliptical orbit</div><div><i style='border-color:#e6b93f'></i>escapes into space</div></div></div>
<div class='btns'><button id='launch' class='launch' type='button'>Launch</button><button id='clearBtn' type='button'>Clear</button></div>
</aside></section></main>
<script>
(function(){
  var cv=document.getElementById('sky'),ctx=cv.getContext('2d');
  var W=900,H=560;cv.width=W;cv.height=H;
  var EC={x:452,y:322},PX=150,GM=1,R0=1.2,KMS=8.66,R_EARTH_KM=6371;
  var speed=document.getElementById('speed'),speedVal=document.getElementById('speedVal');
  var typeVal=document.getElementById('typeVal'),altVal=document.getElementById('altVal');
  var trails=[],active=null,stars=[],launched=false;
  for(var s=0;s<70;s++)stars.push({x:Math.random()*W,y:Math.random()*H,r:Math.random()*1.3+0.3,a:Math.random()*0.6+0.2});
  function bridge(message){try{window.parent.postMessage(message,'*')}catch(error){}}
  function toPx(p){return{x:EC.x+p.x*PX,y:EC.y+p.y*PX}}
  function classify(v){
    var E=0.5*v*v-GM/R0;
    if(E>=-1e-6)return{name:'Escape trajectory',colour:'#e6b93f',kind:'escape'};
    var L=R0*v,e=Math.sqrt(Math.max(0,1+2*E*L*L/(GM*GM))),a=-GM/(2*E),rp=a*(1-e);
    if(rp<=1)return{name:'Suborbital: falls back',colour:'#e2795f',kind:'fall'};
    if(e<0.02)return{name:'Circular orbit',colour:'#3fb6a2',kind:'orbit'};
    return{name:'Elliptical orbit',colour:'#3fb6a2',kind:'orbit'};
  }
  function launch(){
    var kms=+speed.value,v=kms/KMS,info=classify(v);
    active={pos:{x:0,y:-R0},vel:{x:v,y:0},trail:[{x:0,y:-R0}],peak:R0,colour:info.colour,dead:null};
    typeVal.textContent=info.name;typeVal.style.color=info.colour;launched=true;
    bridge({type:'synapse_event',control:'launch_speed',value:+kms.toFixed(1)});
  }
  function step(dt){
    var p=active.pos,vel=active.vel,r=Math.hypot(p.x,p.y),f=-GM/(r*r*r);
    vel.x+=p.x*f*dt;vel.y+=p.y*f*dt;p.x+=vel.x*dt;p.y+=vel.y*dt;
    active.trail.push({x:p.x,y:p.y});var rr=Math.hypot(p.x,p.y);if(rr>active.peak)active.peak=rr;
    if(rr<=1)active.dead='crash';else if(rr>6.2)active.dead='escape';else if(active.trail.length>5200)active.dead='timeout';
  }
  function drawPath(trail,colour,width,alpha){
    if(trail.length<2)return;ctx.globalAlpha=alpha;ctx.strokeStyle=colour;ctx.lineWidth=width;ctx.lineJoin='round';ctx.beginPath();
    for(var i=0;i<trail.length;i++){var q=toPx(trail[i]);if(i===0)ctx.moveTo(q.x,q.y);else ctx.lineTo(q.x,q.y)}
    ctx.stroke();ctx.globalAlpha=1;
  }
  function render(){
    ctx.fillStyle='#0b1020';ctx.fillRect(0,0,W,H);
    for(var i=0;i<stars.length;i++){var st=stars[i];ctx.globalAlpha=st.a;ctx.fillStyle='#cfe4f5';ctx.beginPath();ctx.arc(st.x,st.y,st.r,0,6.2832);ctx.fill()}
    ctx.globalAlpha=1;
    var g=ctx.createRadialGradient(EC.x-45,EC.y-50,20,EC.x,EC.y,PX);g.addColorStop(0,'#7fd0ff');g.addColorStop(.45,'#2f8fd6');g.addColorStop(1,'#123f78');
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(EC.x,EC.y,PX,0,6.2832);ctx.fill();
    ctx.strokeStyle='#8fd6a0';ctx.globalAlpha=.35;ctx.lineWidth=2;ctx.beginPath();ctx.arc(EC.x,EC.y,PX,0,6.2832);ctx.stroke();ctx.globalAlpha=1;
    var lp=toPx({x:0,y:-R0});ctx.fillStyle='#e9eef4';ctx.beginPath();ctx.moveTo(lp.x-9,lp.y+10);ctx.lineTo(lp.x+9,lp.y+10);ctx.lineTo(lp.x,lp.y-8);ctx.closePath();ctx.fill();
    for(var t=0;t<trails.length;t++)drawPath(trails[t].trail,trails[t].colour,2,.4);
    if(active){drawPath(active.trail,active.colour,3,.95);var hp=toPx(active.pos);ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(hp.x,hp.y,4.5,0,6.2832);ctx.fill()}
    if(!launched){ctx.globalAlpha=.85;ctx.fillStyle='#9fbdd8';ctx.font='600 15px system-ui';ctx.textAlign='center';ctx.fillText('Set a speed and press Launch',W/2,42);ctx.globalAlpha=1;ctx.textAlign='left'}
  }
  function loop(){
    if(active){for(var k=0;k<7&&!active.dead;k++)step(0.004);
      var altKm=(active.peak-1)*R_EARTH_KM;altVal.textContent=altKm>=0?Math.round(altKm).toLocaleString()+' km':'-';
      if(active.dead){if(active.dead==='crash')typeVal.textContent='Fell back to Earth';trails.push(active);if(trails.length>5)trails.shift();active=null}}
    render();window.requestAnimationFrame(loop);
  }
  speed.addEventListener('input',function(){speedVal.textContent=(+speed.value).toFixed(1)+' km/s';var info=classify(+speed.value/KMS);typeVal.textContent=info.name;typeVal.style.color=info.colour});
  document.getElementById('launch').addEventListener('click',launch);
  document.getElementById('clearBtn').addEventListener('click',function(){trails=[];active=null;launched=false;altVal.textContent='-';typeVal.textContent='Press Launch';typeVal.style.color='#5b45a0';bridge({type:'synapse_event',control:'clear',value:true})});
  try{speedVal.textContent=(+speed.value).toFixed(1)+' km/s';loop();window.requestAnimationFrame(function(){bridge({type:'synapse_ready'})})}catch(error){bridge({type:'synapse_error',message:String(error.message||error).slice(0,200)})}
})();
</script></body></html>'''
)

ORBITAL_SIM_PLAN = ArtifactPlan(
    title="Newton's Cannonball: Orbits and Escape",
    learning_objective='Show that raising a projectile\'s sideways launch speed turns a falling path into a circular orbit, an ellipse, and finally an escape trajectory.',
    variables=[Variable(name='launch speed', unit='km/s', min=1, max=15, default=7.9)],
    governing_model=(
        'Newtonian gravity: acceleration a = -GM r / |r|^3 toward Earth\'s centre. A horizontal '
        'launch at radius r0 gives a circular orbit when v = sqrt(GM / r0) (about 7.9 km/s for low '
        'Earth orbit), a bound ellipse for higher speeds, and escape when v >= sqrt(2 GM / r0) '
        '(about 11.2 km/s). Below circular speed the ellipse dips into Earth, so the projectile '
        'falls back. Orbit type is set by specific energy E = v^2/2 - GM/r0.'
    ),
    expected_behaviors=[
        'a low launch speed produces a suborbital arc that falls back to Earth',
        'about 7.9 km/s produces a near-circular orbit that never hits the ground',
        'speeds between circular and escape produce a stretched ellipse with a higher far point',
        'at about 11.2 km/s and above the path opens up and escapes Earth entirely',
    ],
    layout_notes=(
        'A dark space canvas shows Earth at the centre with a launch point at the top. A launch-speed '
        'slider and a Launch button sit in the side panel with readouts for the speed, the trajectory '
        'type, and the peak altitude, plus a colour legend. Each launch traces its path; a Clear button '
        'wipes the traces.'
    ),
    library='none',
    interaction_mode='controls',
    interaction_requirements=[
        'Set the launch-speed slider to choose the sideways speed.',
        'Press Launch to fire the cannonball and trace its path.',
    ],
    study_note=(
        'An orbit is continuous falling: gravity always pulls the cannonball toward Earth, but enough '
        'sideways speed makes it keep missing the ground. Circular orbit needs about 7.9 km/s and escape '
        'about 11.2 km/s at this altitude.'
    ),
    steps=[],
)

ORBITAL_SIM_SPOT_CHECKS = [
    {
        'inputs': 'Launch speed well below 7.9 km/s (for example 4 km/s)',
        'expected': 'the ellipse periapsis drops below Earth\'s radius, so the projectile falls back (suborbital)',
        'code_derived': 'classify() computes E<0 with periapsis rp = a(1-e) <= 1 and returns the falls-back trajectory',
    },
    {
        'inputs': 'Launch speed about 7.9 km/s at the launch radius',
        'expected': 'v approx sqrt(GM/r0), giving a near-circular orbit (eccentricity near zero)',
        'code_derived': 'classify() returns a circular orbit when the computed eccentricity is below 0.02',
    },
    {
        'inputs': 'Launch speed at or above 11.2 km/s',
        'expected': 'specific energy E >= 0, so the trajectory is unbound and escapes Earth',
        'code_derived': 'classify() returns the escape trajectory once E = v^2/2 - GM/r0 is non-negative',
    },
]
