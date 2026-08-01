# ruff: noqa: E501
'''Deterministic, locally stored labs for high-value repeatable experiments.'''

import re
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest

from schemas.plan import ArtifactPlan, Variable
from services.hookes_law_lab import (
    HOOKES_LAW_HTML,
    HOOKES_LAW_ID,
    HOOKES_LAW_PLAN,
    HOOKES_LAW_SPOT_CHECKS,
)
from services.orbital_sim_lab import (
    ORBITAL_SIM_HTML,
    ORBITAL_SIM_ID,
    ORBITAL_SIM_PLAN,
    ORBITAL_SIM_SPOT_CHECKS,
)
from services.yeast_fermentation_lab import (
    YEAST_FERMENTATION_HTML,
    YEAST_FERMENTATION_ID,
    YEAST_FERMENTATION_PLAN,
    YEAST_FERMENTATION_SPOT_CHECKS,
)

KOH_TITRATION_ID = 'koh_titration_interactive_v2'


@dataclass(frozen=True)
class BuiltinLab:
    key: str
    plan: ArtifactPlan
    html: str


KOH_TITRATION_HEAD = r'''<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>KOH Titration Lab</title>
<style>
:root{--bg:#f7f8f4;--paper:#fff;--ink:#26362f;--dim:#62736b;--line:#dfe6db;--teal:#0b8e80;--pink:#f29bb9;--gold:#e6a200;--green:#1a9958;--violet:#7560ad}*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden}body{background:var(--bg);color:var(--ink);font:14px/1.35 system-ui,sans-serif}main{height:100%;padding:12px;display:grid;grid-template-rows:auto auto auto minmax(0,1fr);gap:8px}header{display:flex;justify-content:space-between;align-items:center}h1{margin:0;font:700 clamp(19px,2.4vw,28px)/1.1 Georgia,serif;color:var(--gold)}button{min-height:40px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);font-weight:700;cursor:pointer}.hint{margin:0;color:#a4463f;font-weight:700}.note{padding:8px 10px;border:1px solid #f1d891;border-radius:10px;background:#fffaf0}.note b{color:#a87900}.steps{display:flex;gap:6px;overflow:hidden}.step{flex:1;min-width:0;padding:7px;border:1px solid var(--line);border-radius:9px;background:var(--paper);font-size:12px}.step b{display:inline-grid;place-items:center;width:18px;height:18px;margin-right:4px;border-radius:50%;background:var(--violet);color:#fff}.lab{min-height:0;display:grid;grid-template-columns:minmax(0,1.5fr) minmax(230px,.8fr);gap:10px}.stage,.panel{border:1px solid var(--line);border-radius:14px;background:var(--paper);min-height:0}.stage{position:relative;overflow:hidden;background:linear-gradient(#fdfefd 0 78%,#edf2ea 78%)}.tile{position:absolute;left:23%;right:16%;bottom:8%;height:18%;border:2px solid #d7d7d4;background:#f9f9f7;box-shadow:0 3px 0 #d3d6d0}.burette{position:absolute;left:12%;top:9%;height:62%;width:54px;border:3px solid #66716d;border-radius:9px;background:linear-gradient(90deg,#e9fbff,#a8e2f1,#e9fbff)}.burette:before{content:'HNO3';position:absolute;top:8px;left:5px;font-size:11px;font-weight:800;color:#226070}.burette:after{content:'';position:absolute;bottom:-45px;left:21px;height:45px;border-left:5px solid #66716d}.stopcock{position:absolute;bottom:-60px;left:-9px;width:66px;height:27px;display:grid;place-items:center;border:2px solid #b48117;border-radius:14px;background:#ffe4a1;color:#704b00;font-size:10px;font-weight:800;touch-action:none;user-select:none}.pipette{position:absolute;left:6%;top:68%;z-index:4;width:118px;min-height:62px;padding:5px;border:2px solid var(--teal);border-radius:30px;background:#d9f5f0;color:#075f56;touch-action:none;user-select:none}.pipette.dragging{opacity:.86;box-shadow:0 7px 18px #0b8e8066}.flask{position:absolute;left:51%;top:36%;z-index:3;width:154px;height:158px;border:4px solid #66716d;border-top:0;border-radius:20px 20px 44px 44px;background:#fff;overflow:hidden;touch-action:none;user-select:none}.flask:before{content:'25 cm3 KOH flask';position:absolute;top:-25px;left:-19px;width:180px;text-align:center;font-size:11px;font-weight:800;color:var(--dim)}.liquid{position:absolute;left:0;right:0;bottom:0;height:52%;background:#f29bb9;transition:background .2s,height .2s}.flaskLabel{position:absolute;left:0;right:0;bottom:13px;z-index:1;text-align:center;color:#5b2540;font-size:11px;font-weight:800}.gesture{position:absolute;left:39%;top:73%;z-index:5;padding:5px 8px;border-radius:12px;background:#eef5ef;color:#28624a;font-size:11px;font-weight:800}.panel{padding:12px;display:grid;align-content:start;gap:9px}.card{padding:10px;border:1px solid var(--line);border-radius:10px;background:#fbfcf9}.label{font-size:11px;color:var(--dim);font-weight:800;text-transform:uppercase;letter-spacing:.06em}.value{margin-top:3px;font-size:22px;font-weight:800;color:var(--teal);font-variant-numeric:tabular-nums}.status{color:var(--violet);font-weight:800}.formula{font:700 16px Georgia,serif;color:#395247}.wide{width:100%}.ok{color:var(--green)}@media(max-width:640px){main{padding:8px;gap:6px}.lab{grid-template-columns:1fr}.panel{display:grid;grid-template-columns:repeat(2,1fr);gap:6px;padding:7px}.stage{min-height:310px}.note{font-size:12px}.steps{display:none}.gesture{top:78%}.burette{left:8%}.flask{left:49%}}
</style>
<style>
/* The deterministic lab is deliberately drawn with CSS instead of a canvas:
   its controls remain real DOM targets on every browser size. */
main{grid-template-rows:auto auto auto auto minmax(0,1fr);gap:9px;padding:14px;background:linear-gradient(135deg,#fbfdf9 0%,#f5f8f3 100%)}
header{min-height:38px;padding:0 2px}h1{font-size:clamp(20px,2.1vw,29px);letter-spacing:-.025em;color:#bd7a00}.hint{padding:0 2px;color:#a8423d}.note{border-color:#f1d28a;background:linear-gradient(90deg,#fff9e9,#fffdf7);box-shadow:0 1px 0 #fff inset}.steps{gap:8px}.step{display:flex;align-items:flex-start;min-height:57px;padding:9px 10px;border-color:#dbe5dc;background:#fff;box-shadow:0 2px 0 #edf1ea;font-size:12px;line-height:1.3}.step b{flex:0 0 auto;margin-top:1px;background:#7360ad}
.lab{grid-template-columns:minmax(0,1.62fr) minmax(255px,.78fr);gap:12px}.stage{min-height:400px;border-color:#d9e5db;border-radius:16px;background:linear-gradient(180deg,#fbfffe 0 64%,#eef4eb 64%);box-shadow:inset 0 0 0 1px #fff}.stage:before{content:'TITRATION STATION';position:absolute;left:20px;top:15px;color:#4b827b;font-size:10px;font-weight:900;letter-spacing:.13em}.stage:after{content:'';position:absolute;left:0;right:0;bottom:0;height:36%;background:repeating-linear-gradient(90deg,transparent 0 42px,#ffffff66 42px 43px),linear-gradient(#eef4eb,#e7eee4);border-top:1px solid #dbe6db;pointer-events:none}.tile{z-index:2;left:28%;right:11%;bottom:7%;height:20%;border:2px solid #d3d9d0;border-radius:4px;background:linear-gradient(#fff,#f3f4f0);box-shadow:0 4px 0 #d5dbd3}.tile:before{content:'WHITE TILE';position:absolute;top:7px;right:9px;color:#829088;font-size:9px;font-weight:900;letter-spacing:.08em}
.burette{z-index:3;left:16%;top:11%;width:70px;height:52%;border:3px solid #526e6b;border-radius:12px 12px 8px 8px;background:repeating-linear-gradient(to bottom,transparent 0 19px,#7da3a4 19px 20px),linear-gradient(90deg,#edfcff 0 17%,#b9e8f4 48%,#eafdff 100%);box-shadow:inset 6px 0 #ffffff88,0 4px 0 #d7e1db}.burette:before{content:'1.0 M\A HNO3';white-space:pre;top:9px;left:9px;color:#176376;font-size:10px;line-height:1.05;letter-spacing:.04em;text-align:center}.burette:after{bottom:-52px;left:29px;height:52px;border-left:6px solid #526e6b;filter:drop-shadow(2px 0 #d6eff3)}.stopcock{bottom:-52px;left:-11px;width:87px;height:33px;border:2px solid #bd8918;border-radius:18px;background:linear-gradient(#ffe9af,#f5cb64);box-shadow:0 3px 0 #d8b455;color:#664800;font-size:10px;letter-spacing:.02em}.stopcock:before{content:'↟';position:absolute;left:8px;font-size:17px;line-height:1;color:#a36500}.stopcock:hover{filter:brightness(1.04);transform:translateY(-1px)}
.pipette{z-index:6;left:5%;top:70%;width:144px;min-height:57px;padding:10px 19px 9px 29px;border:2px solid #079d91;border-radius:32px;background:linear-gradient(90deg,#d8f7f1,#f4fffc);box-shadow:0 4px 0 #9ad8ce;color:#075f56;font-size:12px;line-height:1.1;text-align:center}.pipette:before{content:'';position:absolute;left:-16px;top:20px;width:21px;height:13px;border-radius:8px 2px 2px 8px;background:#1db6aa;box-shadow:-4px 0 0 #b4e9e1}.pipette:after{content:'KOH';position:absolute;right:11px;top:8px;color:#11978b;font-size:9px;font-weight:900;letter-spacing:.08em}.pipette.dragging{box-shadow:0 9px 22px #0b8e8066;transform:scale(1.04)}
.flask{z-index:5;left:51%;top:21%;width:min(29vw,235px);height:min(68%,282px);border:0;border-radius:0;background:transparent;overflow:visible;transform-origin:50% 88%}.flask:before{content:'';position:absolute;left:calc(50% - 35px);top:0;width:70px;height:73px;border:4px solid #526e6b;border-bottom:0;border-radius:9px 9px 0 0;background:linear-gradient(90deg,#efffff,#fff 50%,#d7f0f3);box-shadow:inset 5px 0 #ffffffaa}.flask:after{content:'PHENOLPHTHALEIN';position:absolute;top:83px;left:50%;transform:translateX(-50%);z-index:5;white-space:nowrap;color:#6d6e83;font-size:9px;font-weight:900;letter-spacing:.07em}.flask-body{position:absolute;left:0;right:0;bottom:0;height:77%;clip-path:polygon(24% 0,76% 0,100% 90%,96% 100%,4% 100%,0 90%);background:#526e6b;filter:drop-shadow(0 4px 0 #d3ded5);overflow:hidden}.flask-body:before{content:'';position:absolute;z-index:0;inset:4px;clip-path:polygon(25% 0,75% 0,98% 90%,94% 100%,6% 100%,2% 90%);background:linear-gradient(90deg,#e8fbff,#fff 35%,#fff 65%,#d7eff1);box-shadow:inset 10px 0 #ffffff88}.liquid{z-index:1;left:5px;right:5px;bottom:4px;background:#f29bb9;box-shadow:inset 0 7px #ffe0eb;transition:background .24s,height .24s}.flaskLabel{z-index:2;left:13%;right:13%;bottom:15px;padding:3px 5px;border-radius:10px;background:#ffffffd9;color:#5b2540;font-size:10px;line-height:1.1;text-shadow:none}.gesture{z-index:7;left:50%;top:auto;bottom:11%;transform:translateX(-50%);max-width:48%;text-align:center;padding:6px 10px;border:1px solid #d9e8da;border-radius:15px;background:#f5fbf5eF;box-shadow:0 2px 0 #dce7dd;color:#27614c}
.panel{border-color:#d9e5db;border-radius:16px;padding:12px;background:linear-gradient(180deg,#fff,#fbfdf9);box-shadow:inset 0 0 0 1px #fff}.card{border-color:#dce6dc;border-radius:11px;background:linear-gradient(135deg,#fff,#f8fbf7)}.value{font-size:25px;letter-spacing:-.04em}.label{letter-spacing:.075em}.status{line-height:1.3}.formula{font-size:16px;line-height:1.18}.wide{min-height:40px;background:#f6fbf6;box-shadow:0 2px 0 #dce8db}.wide:hover{background:#eff8ef}.ok{color:#168255}
@media(max-width:760px){main{padding:9px;gap:7px}.lab{grid-template-columns:1fr}.stage{min-height:330px}.panel{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;padding:8px}.panel .wide{grid-column:1/-1}.flask{left:51%;width:190px}.burette{left:13%}.pipette{left:3%;top:72%;width:126px}.steps{display:none}.note{font-size:12px}.gesture{bottom:8%;max-width:60%}}
.stand-base{position:absolute;z-index:1;left:2%;bottom:6%;width:33%;height:11px;border-radius:5px;background:linear-gradient(#8c96a0,#5d6870);box-shadow:0 3px 0 #464f56}.stand-rod{position:absolute;z-index:1;left:6%;top:8%;bottom:6%;width:10px;border-radius:5px;background:linear-gradient(90deg,#9aa4ad,#6f7a82 55%,#535d64)}.clamp{position:absolute;z-index:2;left:6%;top:20%;width:12%;height:12px;border-radius:6px;background:linear-gradient(#8f99a2,#5f6a72);box-shadow:0 3px 0 #495158}.funnel{position:absolute;z-index:2;left:16%;top:6%;width:70px;height:20px;clip-path:polygon(0 0,100% 0,64% 100%,36% 100%);background:linear-gradient(#eafaff,#bfe6f0);border:1px solid #9cc3ce}.meniscus-line{position:absolute;left:-8px;right:-14px;top:0;height:0;border-top:2px dashed #c0392b;z-index:5;transition:top .24s}.eye{position:absolute;z-index:7;left:34%;top:26%;width:40px;height:28px;display:grid;place-items:center;border:2px solid #7360ad;border-radius:16px/13px;background:radial-gradient(circle,#fff 0 58%,#efeaff 60%);box-shadow:0 3px 0 #c7bce6;cursor:grab;touch-action:none;user-select:none}.eye .pupil{width:11px;height:11px;border-radius:50%;background:#4a3d84}.eye .ray{position:absolute;right:100%;top:50%;width:230px;height:0;border-top:2px dashed #b7a9e0;pointer-events:none}.eye.level{border-color:#1a9958;box-shadow:0 3px 0 #a7dcc0}.eye.level .ray{border-color:#1a9958}.eye:after{content:'EYE';position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:3px;font-size:8px;font-weight:900;color:#6a5ba0;white-space:nowrap}.tray{position:absolute;z-index:9;left:3%;bottom:4%;width:44%;display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:8px 10px;border:1px dashed #cdd9cd;border-radius:12px;background:#f4faf3e6}.tray-label{width:100%;color:#4c847c;font-size:9px;font-weight:900;letter-spacing:.1em}.tray .pipette{position:relative;left:auto;top:auto;z-index:1}.beaker-mini{width:58px;min-height:44px;padding:6px;border:2px solid #9fb0ad;border-top:0;border-radius:0 0 10px 10px;background:linear-gradient(#eefbff,#cdeef2);color:#4b6763;font-size:9px;font-weight:800;text-align:center;display:grid;place-items:end center}@media(max-width:760px){.tray{width:auto;right:3%}.eye{left:40%}.funnel{left:13%}}
</style>
</head>
<body><main>
<header><h1>KOH Titration: Interactive Endpoint Lab</h1></header>
<p class='hint'>Try this: drag the KOH pipette into the flask, swirl to mix, turn the stopcock to add HNO3, and line your eye up with the meniscus to read the burette correctly.</p>
<div class='note'><b>Quick study note:</b> At the endpoint, moles of 1.0 mol dm-3 HNO3 equal moles of KOH in the 25 cm3 aliquot, so c(KOH) = V(HNO3) / 25. Always read a burette with your eye level to the meniscus.</div>
<div class='steps'><div class='step'><b>1</b>Drag the 25 cm3 KOH pipette onto the flask.</div><div class='step'><b>2</b>Swirl the flask to mix the indicator.</div><div class='step'><b>3</b>Turn the stopcock to add HNO3.</div><div class='step'><b>4</b>Line your eye with the meniscus, then read at the endpoint.</div></div>
<section class='lab'><div id='stage' class='stage'>
<div class='stand-base'></div><div class='stand-rod'></div><div class='clamp'></div><div class='funnel'></div>
<div class='burette'><div id='meniscus' class='meniscus-line'></div><div id='stopcock' class='stopcock' role='button' tabindex='0'>drag to turn</div></div>
<div id='eye' class='eye' role='button' tabindex='0'><span class='pupil'></span><div class='ray'></div></div>
<div id='flask' class='flask' role='button' tabindex='0'><div class='flask-body'><div id='liquid' class='liquid'></div><div id='flaskLabel' class='flaskLabel'>empty flask</div></div></div>
<div class='tile'></div><div id='gesture' class='gesture'>Load the KOH sample first</div>
<div class='tray'><span class='tray-label'>BENCH TOOLS</span><button id='pipette' class='pipette' type='button'>25 cm3 KOH<br>pipette</button><div class='beaker-mini'>HNO3<br>beaker</div></div>
</div><aside class='panel'>
<div class='card'><div class='label'>HNO3 added</div><div id='volume' class='value'>0.0 cm3</div><div class='label'>pH <span id='ph'>-</span></div></div>
<div class='card'><div class='label'>Burette reading (your eye line)</div><div id='reading' class='value'>0.00 cm3</div><div id='eyeStatus' class='status'>Drag the eye level with the meniscus.</div></div>
<div class='card'><div class='label'>Lab state</div><div id='status' class='status'>Drag the pipette into the flask.</div></div>
<div class='card'><div class='label'>Calculated c(KOH)</div><div id='result' class='formula'>Load and titrate a sample.</div></div>
<button id='newUnknown' class='wide' type='button'>New unknown concentration</button>
</aside></section></main>
<script>
(function(){
  var state={loaded:false,mixed:false,acid:0,koh:.80,swirl:false,turn:false};
  var values=[.64,.72,.80,.88,.96],valueIndex=2;
  var stage=document.getElementById('stage'),pipette=document.getElementById('pipette'),flask=document.getElementById('flask');
  var valve=document.getElementById('stopcock'),eye=document.getElementById('eye'),meniscus=document.getElementById('meniscus');
  var burette=document.querySelector('.burette');
  var liquid=document.getElementById('liquid'),volume=document.getElementById('volume'),ph=document.getElementById('ph');
  var status=document.getElementById('status'),result=document.getElementById('result'),label=document.getElementById('flaskLabel');
  var gesture=document.getElementById('gesture'),reading=document.getElementById('reading'),eyeStatus=document.getElementById('eyeStatus');
  var swings=0,lastDx=0,startX=0,turnY=0,turnCarry=0;
  function bridge(message){try{window.parent.postMessage(message,'*')}catch(error){}}
  function endpoint(){return state.koh*25}
  function pH(){var diff=state.koh*.025-state.acid/1000,total=.025+state.acid/1000;if(Math.abs(diff)<.0000001)return 7;if(diff>0)return 14+Math.log10(diff/total);return-Math.log10(-diff/total)}
  function updateReading(){
    meniscus.style.top=((state.acid/50)*100)+'%';
    var b=burette.getBoundingClientRect();if(!b.height)return;var pxcm=b.height/50;
    var men=b.top+(state.acid/50)*b.height,er=eye.getBoundingClientRect(),eyc=er.top+er.height/2,diff=men-eyc;
    var apparent=Math.max(0,Math.min(50,state.acid+(diff/pxcm)*.32));
    reading.textContent=apparent.toFixed(2)+' cm3';
    var tol=b.height*.03+4;
    if(Math.abs(diff)<tol){eyeStatus.textContent='Eye level with the meniscus - accurate reading.';eyeStatus.className='status ok';eye.classList.add('level')}
    else if(diff>0){eyeStatus.textContent='Eye above the meniscus - parallax reads too high.';eyeStatus.className='status';eye.classList.remove('level')}
    else{eyeStatus.textContent='Eye below the meniscus - parallax reads too low.';eyeStatus.className='status';eye.classList.remove('level')}
  }
  function update(){
    var end=endpoint(),ratio=end>0?state.acid/end:0;
    volume.textContent=state.acid.toFixed(1)+' cm3';ph.textContent=pH().toFixed(2);
    liquid.style.background=ratio<.85?'#f29bb9':ratio<1?'#f9dce7':'#eff9f2';
    liquid.style.height=(state.loaded?52:0)+'%';
    if(!state.loaded){label.textContent='empty flask';status.textContent='Drag the pipette into the flask.';gesture.textContent='Load the KOH sample first';result.textContent='Load and titrate a sample.';updateReading();return}
    label.textContent=state.mixed?'pink KOH + indicator':'KOH added - swirl to mix';
    if(!state.mixed){status.textContent='Swirl the flask to mix the indicator.';gesture.textContent='Swirl to mix';result.textContent='Mix before using the stopcock.';updateReading();return}
    gesture.textContent='Turn the stopcock, read at eye level';
    var est=(state.acid/25).toFixed(2);
    if(state.acid<=0){status.textContent='Turn the stopcock to add HNO3.';result.textContent='Add HNO3 to estimate c(KOH).';updateReading();return}
    result.textContent='c(KOH) = '+state.acid.toFixed(1)+' / 25 = '+est+' mol dm-3';
    if(state.acid<end-.25){status.textContent='Keep adding HNO3 toward the colourless endpoint.'}
    else if(state.acid>end+.25){status.textContent='You passed the endpoint - reset and try again.'}
    else{status.textContent='Endpoint reached: the pink is now colourless.';status.className='status ok';result.textContent='Endpoint: c(KOH) = '+est+' mol dm-3 (V = '+state.acid.toFixed(1)+' cm3)'}
    updateReading();
  }
  function reset(){state.loaded=false;state.mixed=false;state.acid=0;swings=0;lastDx=0;flask.style.transform='';status.className='status';update();bridge({type:'synapse_event',control:'reset',value:true})}
  function addAcid(step){if(!state.loaded||!state.mixed)return;state.acid=Math.max(0,Math.min(40,+(state.acid+step).toFixed(1)));update();bridge({type:'synapse_event',control:'hno3_volume',value:state.acid})}
  var pdrag=false,poX=0,poY=0;
  pipette.addEventListener('pointerdown',function(event){pdrag=true;var box=pipette.getBoundingClientRect();poX=event.clientX-box.left;poY=event.clientY-box.top;pipette.classList.add('dragging');pipette.style.position='fixed';pipette.style.zIndex='30';pipette.style.width=box.width+'px';pipette.style.left=box.left+'px';pipette.style.top=box.top+'px';pipette.setPointerCapture(event.pointerId);event.preventDefault()});
  pipette.addEventListener('pointermove',function(event){if(!pdrag)return;pipette.style.left=(event.clientX-poX)+'px';pipette.style.top=(event.clientY-poY)+'px'});
  function dropPipette(event){if(!pdrag)return;pdrag=false;pipette.classList.remove('dragging');try{pipette.releasePointerCapture(event.pointerId)}catch(error){}var a=pipette.getBoundingClientRect(),f=flask.getBoundingClientRect(),x=a.left+a.width/2,y=a.top+a.height/2,hit=x>f.left&&x<f.right&&y>f.top&&y<f.bottom;pipette.style.position='';pipette.style.left='';pipette.style.top='';pipette.style.zIndex='';pipette.style.width='';if(hit&&!state.loaded){state.loaded=true;bridge({type:'synapse_event',control:'load_koh_sample',value:25})}update()}
  pipette.addEventListener('pointerup',dropPipette);pipette.addEventListener('pointercancel',dropPipette);
  flask.addEventListener('pointerdown',function(event){if(!state.loaded)return;state.swirl=true;swings=0;lastDx=0;startX=event.clientX;flask.setPointerCapture(event.pointerId);event.preventDefault()});
  flask.addEventListener('pointermove',function(event){if(!state.swirl)return;var dx=event.clientX-startX;flask.style.transform='rotate('+(dx/4)+'deg)';if(Math.abs(dx)>13&&lastDx&&Math.sign(dx)!==Math.sign(lastDx))swings++;if(Math.abs(dx)>13)lastDx=dx;if(swings>=3&&!state.mixed){state.mixed=true;bridge({type:'synapse_event',control:'swirl_mix',value:swings});update()}});
  function stopSwirl(event){if(!state.swirl)return;state.swirl=false;flask.style.transform='';try{flask.releasePointerCapture(event.pointerId)}catch(error){}update()}
  flask.addEventListener('pointerup',stopSwirl);flask.addEventListener('pointercancel',stopSwirl);
  valve.addEventListener('pointerdown',function(event){if(!state.mixed)return;state.turn=true;turnY=event.clientY;turnCarry=0;valve.setPointerCapture(event.pointerId);event.preventDefault()});
  valve.addEventListener('pointermove',function(event){if(!state.turn)return;turnCarry+=turnY-event.clientY;turnY=event.clientY;while(turnCarry>=9){addAcid(.1);turnCarry-=9}while(turnCarry<=-9){addAcid(-.1);turnCarry+=9}});
  function stopValve(event){if(!state.turn)return;state.turn=false;try{valve.releasePointerCapture(event.pointerId)}catch(error){}}
  valve.addEventListener('pointerup',stopValve);valve.addEventListener('pointercancel',stopValve);
  var edrag=false,eoY=0;
  eye.addEventListener('pointerdown',function(event){edrag=true;var box=eye.getBoundingClientRect();eoY=event.clientY-box.top;eye.setPointerCapture(event.pointerId);event.preventDefault()});
  eye.addEventListener('pointermove',function(event){if(!edrag)return;var s=stage.getBoundingClientRect();var topPx=Math.max(6,Math.min(s.height-40,event.clientY-s.top-eoY));eye.style.top=topPx+'px';updateReading();bridge({type:'synapse_event',control:'eye_level',value:+reading.textContent.replace(' cm3','')})});
  function stopEye(event){if(!edrag)return;edrag=false;try{eye.releasePointerCapture(event.pointerId)}catch(error){}}
  eye.addEventListener('pointerup',stopEye);eye.addEventListener('pointercancel',stopEye);
  document.getElementById('newUnknown').addEventListener('click',function(){valueIndex=(valueIndex+1)%values.length;state.koh=values[valueIndex];reset();bridge({type:'synapse_event',control:'new_unknown',value:state.koh})});
  try{update();window.requestAnimationFrame(function(){bridge({type:'synapse_ready'});updateReading()})}catch(error){bridge({type:'synapse_error',message:String(error.message||error).slice(0,200)})}
})();
</script></body></html>'''

KOH_TITRATION_HTML = KOH_TITRATION_HEAD

KOH_TITRATION_PLAN = ArtifactPlan(
    title='KOH Titration: Interactive Endpoint Lab',
    learning_objective='Determine the concentration of KOH from the HNO3 volume at a 1:1 endpoint.',
    variables=[Variable(name='HNO3 volume added', unit='cm3', min=0, max=40, default=0)],
    governing_model=(
        'HNO3 + KOH -> KNO3 + H2O (1:1). At endpoint, n(HNO3) = n(KOH); '
        'c(KOH) = c(HNO3) x V(HNO3) / 25 cm3, with c(HNO3) = 1.0 mol dm-3. '
        'Before/after endpoint, pH is calculated from excess OH- or H+ divided by total volume.'
    ),
    expected_behaviors=[
        'dragging the 25 cm3 KOH pipette onto the conical flask loads the sample',
        'shaking the flask mixes the phenolphthalein before acid can be added',
        'turning the stopcock changes HNO3 volume, pH, and flask colour',
        'at the colourless endpoint, c(KOH) equals V(HNO3) divided by 25',
    ],
    layout_notes=(
        'Show a retort stand and clamp holding a burette with a filling funnel, a 25 cm3 KOH '
        'pipette in a bench tray, a conical flask on a white tile, and a waste beaker. The pipette '
        'transfer, flask swirl, and stopcock turn are the required direct-manipulation interactions. '
        'A draggable eye with a line of sight teaches reading the burette meniscus at eye level; '
        'a reset and fresh-unknown button sit in the readout panel beside the reading.'
    ),
    library='none',
    interaction_mode='drag_drop',
    interaction_requirements=[
        'Drag the 25 cm3 KOH pipette onto the conical flask to load the sample.',
        'Swirl the flask left and right with a pointer gesture to mix the sample.',
        'Turn the burette stopcock, then drag the eye level with the meniscus to read it.',
    ],
    study_note=(
        'At the endpoint, the 1:1 acid and base moles are equal. For a 25 cm3 KOH aliquot and '
        '1.0 mol dm-3 HNO3, the endpoint volume in cm3 divided by 25 gives c(KOH) in mol dm-3. '
        'Always read the burette with your eye level to the bottom of the meniscus to avoid parallax.'
    ),
    steps=[
        'Drag the 25 cm3 KOH pipette onto the conical flask.',
        'Swirl the flask until the indicator is mixed.',
        'Turn the burette stopcock to add HNO3.',
        'Line your eye with the meniscus, then read c(KOH) at the colourless endpoint.',
    ],
)

_TITRATION_WORD = re.compile(r'\btitration\b', re.IGNORECASE)
_APPARATUS_WORD = re.compile(r'\b(?:apparatus|materials|burette|pipette|conical\s+flask)\b', re.IGNORECASE)
_YEAST_WORD = re.compile(r'\b(?:yeast|saccharomyces)\b', re.IGNORECASE)
_FERMENT_WORD = re.compile(r'\bferment(?:ation|ing|ed)?\b', re.IGNORECASE)
_YEAST_PRODUCT_OR_LAB_CUE = re.compile(
    r'\b(?:products?|produces?|make|makes|release[sd]?|ethanol|carbon\s+dioxide|co2|'
    r'lime\s*water|experiment|investigate|glucose|paraffin\s+oil|boiling\s+tube|'
    r'delivery\s+tube|anaerobic)\b',
    re.IGNORECASE,
)
_SPRING_WORD = re.compile(r'\bspring(?:s)?\b', re.IGNORECASE)
_HOOKE_WORD = re.compile(r"\bhooke'?s?\b", re.IGNORECASE)
_SPRING_EXT_CUE = re.compile(
    r'\b(?:extension|extend(?:s|ed|ing)?|stretch(?:es|ed|ing)?|elongat\w+|'
    r'spring\s+constant|slotted\s+mass(?:es)?|hung|hang(?:s|ing)?|newton\w*|'
    r'force\s+applied|restoring\s+force)\b',
    re.IGNORECASE,
)
_ORBIT_SIM_CORE = re.compile(
    r"\b(?:satellite|cannonball|newton'?s\s+cannon|escape\s+velocity|orbit(?:s|al|ing)?)\b",
    re.IGNORECASE,
)
_ORBIT_SIM_CONTEXT = re.compile(
    r'\b(?:launch|speed|velocity|gravity|earth|space|fall\s+back|falls?\s+back|escape\w*)\b',
    re.IGNORECASE,
)
_KOH_TEMPLATE_HASH = sha256(KOH_TITRATION_HTML.encode('utf-8')).hexdigest()
_YEAST_TEMPLATE_HASH = sha256(YEAST_FERMENTATION_HTML.encode('utf-8')).hexdigest()
_HOOKES_TEMPLATE_HASH = sha256(HOOKES_LAW_HTML.encode('utf-8')).hexdigest()
_ORBITAL_TEMPLATE_HASH = sha256(ORBITAL_SIM_HTML.encode('utf-8')).hexdigest()

_KOH_SPOT_CHECKS = [
    {
        'inputs': '25.0 cm3 KOH at 0.80 mol dm-3; 20.0 cm3 of 1.0 mol dm-3 HNO3',
        'expected': 'n acid = n base = 0.0200 mol; c(KOH) = 20.0 / 25.0 = 0.80 mol dm-3',
        'code_derived': 'endpoint() returns 0.80 x 25 = 20.0; result renders 20.0 / 25 = 0.80',
    },
    {
        'inputs': '10.0 cm3 HNO3 added to the same sample',
        'expected': '0.0100 mol OH- remains in 0.0350 L, so pH is about 13.46 and liquid is pink',
        'code_derived': 'pH() uses excess base / total volume; update() selects pink below 85 percent endpoint',
    },
    {
        'inputs': 'Pipette drop, three swirl direction changes, stopcock drag, then eye drag',
        'expected': 'sample loads, mixing unlocks acid delivery, volume/endpoint update, and the eye reading is accurate only when level with the meniscus',
        'code_derived': 'pointer handlers update loaded/mixed/acid state and emit synapse_event; updateReading compares the eye and meniscus positions and flags parallax when they are not level',
    },
]


def is_koh_titration_brief(query: str) -> bool:
    '''Recognise a KOH acid-base titration task or brief before routing.

    The trigger is simply KOH plus titration: the deterministic lab already
    supplies the acid (1.0 mol dm-3 HNO3) and apparatus, so a learner does not
    have to spell those out for the interactive titration to appear. A generic
    titration question that never mentions KOH still falls through to normal
    generation.
    '''
    lower = query.lower()
    has_koh = 'koh' in lower or 'potassium hydroxide' in lower
    return bool(has_koh and _TITRATION_WORD.search(query))


def is_yeast_fermentation_products_brief(query: str) -> bool:
    '''Recognise product-focused yeast fermentation questions and lab briefs.'''
    return bool(
        _YEAST_WORD.search(query)
        and _FERMENT_WORD.search(query)
        and _YEAST_PRODUCT_OR_LAB_CUE.search(query)
    )


def is_hookes_law_brief(query: str) -> bool:
    '''Recognise spring-extension / Hooke's law physics briefs and questions.'''
    return bool(
        _SPRING_WORD.search(query)
        and (_HOOKE_WORD.search(query) or _SPRING_EXT_CUE.search(query))
    )


def is_orbital_sim_brief(query: str) -> bool:
    '''Recognise Newton's-cannonball / orbit / escape-velocity simulation briefs.'''
    return bool(_ORBIT_SIM_CORE.search(query) and _ORBIT_SIM_CONTEXT.search(query))


def resolve_builtin_lab_for_query(query: str) -> BuiltinLab | None:
    '''Identify supported deterministic labs from the learner's actual brief.'''
    if is_koh_titration_brief(query):
        return BuiltinLab(KOH_TITRATION_ID, KOH_TITRATION_PLAN, KOH_TITRATION_HTML)
    if is_yeast_fermentation_products_brief(query):
        return BuiltinLab(YEAST_FERMENTATION_ID, YEAST_FERMENTATION_PLAN, YEAST_FERMENTATION_HTML)
    if is_hookes_law_brief(query):
        return BuiltinLab(HOOKES_LAW_ID, HOOKES_LAW_PLAN, HOOKES_LAW_HTML)
    if is_orbital_sim_brief(query):
        return BuiltinLab(ORBITAL_SIM_ID, ORBITAL_SIM_PLAN, ORBITAL_SIM_HTML)
    return None


def resolve_builtin_lab(query: str, artifact_type: str, domain: str) -> BuiltinLab | None:
    '''Return a built-in only when its deterministic intent route is selected.'''
    lab = resolve_builtin_lab_for_query(query)
    if lab is None:
        return None
    if lab.key == KOH_TITRATION_ID and artifact_type == 'virtual_experiment' and domain == 'chemistry':
        return lab
    if lab.key == YEAST_FERMENTATION_ID and artifact_type == 'virtual_experiment' and domain == 'biology':
        return lab
    if lab.key == HOOKES_LAW_ID and artifact_type == 'virtual_experiment' and domain == 'physics':
        return lab
    if lab.key == ORBITAL_SIM_ID and artifact_type == 'simulation' and domain in ('physics', 'earth_space'):
        return lab
    return None


def is_trusted_builtin_html(key: str, html: str) -> bool:
    '''Only an exact, locally stored source document can use the trusted path.'''
    expected_hash = {
        KOH_TITRATION_ID: _KOH_TEMPLATE_HASH,
        YEAST_FERMENTATION_ID: _YEAST_TEMPLATE_HASH,
        HOOKES_LAW_ID: _HOOKES_TEMPLATE_HASH,
        ORBITAL_SIM_ID: _ORBITAL_TEMPLATE_HASH,
    }.get(key)
    return expected_hash is not None and compare_digest(
        sha256(html.encode('utf-8')).hexdigest(), expected_hash
    )


def trusted_builtin_spot_checks(key: str) -> list[dict[str, str]]:
    '''Return the review evidence associated with a precise trusted source.'''
    if key == KOH_TITRATION_ID:
        return _KOH_SPOT_CHECKS
    if key == YEAST_FERMENTATION_ID:
        return YEAST_FERMENTATION_SPOT_CHECKS
    if key == HOOKES_LAW_ID:
        return HOOKES_LAW_SPOT_CHECKS
    if key == ORBITAL_SIM_ID:
        return ORBITAL_SIM_SPOT_CHECKS
    raise ValueError('unknown built-in lab key')
