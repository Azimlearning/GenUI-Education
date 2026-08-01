# ruff: noqa: E501
"""The deterministic Hooke's law spring-extension experiment and study plan."""

from schemas.plan import ArtifactPlan, Variable

HOOKES_LAW_ID = 'hookes_law_spring_extension_v1'

HOOKES_LAW_HTML = (
    r'''<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Hooke's Law Spring Lab</title><style>
:root{--ink:#26362f;--dim:#63736c;--line:#dce7dc;--teal:#078d80;--teal-soft:#d9f3ee;--violet:#6f5ba6;--gold:#c68a00;--steel:#5a6f74;--paper:#fff;--bench:#eef4ec}*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden}body{color:var(--ink);background:#f6f9f4;font:14px/1.35 system-ui,sans-serif}main{height:100%;padding:14px;display:grid;grid-template-rows:auto auto auto auto minmax(0,1fr);gap:9px;background:linear-gradient(135deg,#fcfefb,#f4f8f1)}header{display:flex;align-items:center;gap:14px}header>div{min-width:0}.kicker{margin:0 0 3px;color:var(--teal);font-size:10px;font-weight:900;letter-spacing:.13em}h1{margin:0;color:#b67a00;font:700 clamp(20px,2.1vw,29px)/1.08 Georgia,serif;letter-spacing:-.02em}button{min-height:40px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);font-weight:800;cursor:pointer}.hint{margin:0;padding:0 2px;color:#99433e;font-weight:750}.note{padding:8px 11px;border:1px solid #e9cf88;border-radius:10px;background:linear-gradient(90deg,#fff9e9,#fffdf8)}.note b{color:#a76e00}.steps{display:flex;gap:8px}.step{flex:1;min-width:0;min-height:55px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#fff;box-shadow:0 2px 0 #eaf0e9;font-size:12px}.step b{display:inline-grid;place-items:center;width:19px;height:19px;margin-right:4px;border-radius:50%;background:var(--violet);color:#fff}.lab{min-height:0;display:grid;grid-template-columns:minmax(0,1.62fr) minmax(255px,.74fr);gap:12px}.stage,.panel{min-height:0;border:1px solid var(--line);border-radius:16px;background:#fff}.stage{position:relative;overflow:hidden;min-height:380px;background:linear-gradient(#fbfffe 0 66%,var(--bench) 66%);box-shadow:inset 0 0 0 1px #fff}.stage:before{content:'SPRING EXTENSION BENCH';position:absolute;left:20px;top:14px;color:#4c847c;font-size:10px;font-weight:900;letter-spacing:.12em}
.stand-base{position:absolute;left:12%;bottom:34%;width:210px;height:12px;border-radius:5px;background:linear-gradient(#8c96a0,#5d6870);box-shadow:0 3px 0 #464f56}.stand-rod{position:absolute;left:16%;top:9%;bottom:34%;width:11px;border-radius:5px;background:linear-gradient(90deg,#9aa4ad,#6f7a82 55%,#535d64);box-shadow:2px 0 0 #cfd6db inset}.clamp{position:absolute;left:16%;top:12%;width:23%;height:15px;border-radius:6px;background:linear-gradient(#8f99a2,#5f6a72);box-shadow:0 3px 0 #495158}
.rig{position:absolute;left:30%;top:calc(12% + 15px);display:flex;flex-direction:column;align-items:center;z-index:3}.spring{width:34px;height:64px;border-radius:8px;background:repeating-linear-gradient(-38deg,#8b969d 0 4px,#c7ced3 4px 9px);box-shadow:inset 0 0 0 1px #7f8990;transition:height .22s cubic-bezier(.34,1.2,.5,1)}.hanger{position:relative;width:66px;height:11px;margin-top:2px;border-radius:0 0 8px 8px;background:linear-gradient(#c9a24d,#a97f22);box-shadow:0 3px 0 #8a6512}.hanger:before{content:'';position:absolute;left:50%;top:-9px;width:2px;height:9px;background:#7f8990;transform:translateX(-50%)}.readbadge{position:absolute;left:74px;top:-9px;white-space:nowrap;padding:3px 7px;border-radius:9px;background:#ecefff;color:#4a3d84;font-size:11px;font-weight:900;box-shadow:0 2px 0 #d3cbf0}.disc{width:52px;height:15px;margin-top:3px;border-radius:7px;background:linear-gradient(#4c565d,#2c343a);box-shadow:0 2px 0 #1b2126,inset 0 1px 0 #6b7780;color:#e7edf1;font-size:9px;font-weight:800;display:grid;place-items:center;letter-spacing:.04em}
.ruler{position:absolute;left:45%;top:12%;width:34px;height:52%;border:1px solid #d8c98d;border-radius:6px;background:linear-gradient(#fffdf3,#fdf6df);box-shadow:0 2px 0 #eadfba;z-index:2}.ruler i{position:absolute;left:0;right:44%;height:1px;background:#c9b979}.ruler span{position:absolute;right:3px;font-size:8px;font-weight:800;color:#8a7328;transform:translateY(-6px)}.ruler:after{content:'cm';position:absolute;left:4px;top:3px;font-size:8px;font-weight:900;color:#a98f34}
.tray{position:absolute;left:4%;right:4%;bottom:5%;height:22%;border:1px dashed #b9c8bb;border-radius:12px;background:#f4faf3cc;display:flex;align-items:center;gap:12px;padding:0 14px;z-index:4}.tray-label{color:#4c847c;font-size:10px;font-weight:900;letter-spacing:.08em;writing-mode:vertical-rl;transform:rotate(180deg)}.mass{width:74px;min-height:50px;padding:7px;border:2px solid #37414a;border-radius:12px;background:linear-gradient(135deg,#59636b,#333c43);box-shadow:0 4px 0 #222a30;color:#eef3f6;font-size:11px;font-weight:800;text-align:center;line-height:1.15;cursor:grab;touch-action:none;user-select:none}.mass:before{content:'';position:absolute}.mass.dragging{opacity:.9;box-shadow:0 10px 22px #0b1c2455;transform:scale(1.04);cursor:grabbing}.tray-copy{color:var(--dim);font-size:11px;line-height:1.3}.tray-copy b{color:var(--ink)}
.panel{padding:12px;display:grid;align-content:start;gap:9px;background:linear-gradient(#fff,#fbfdf9);box-shadow:inset 0 0 0 1px #fff}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:9px}.card{padding:10px;border:1px solid var(--line);border-radius:11px;background:linear-gradient(135deg,#fff,#f8fbf7)}.label{color:var(--dim);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.value{margin-top:3px;font-size:21px;font-weight:800;color:var(--teal);font-variant-numeric:tabular-nums}.kcard{border-color:#b7e5db;background:linear-gradient(135deg,#f0fff9,#fafffd)}.kcard .value{color:#087c70}.status{margin-top:4px;color:var(--violet);font-weight:800;line-height:1.3}.readings{width:100%;margin-top:5px;border-collapse:separate;border-spacing:0;overflow:hidden;border:1px solid #dce6dc;border-radius:8px;font-size:11px}.readings th,.readings td{padding:6px;border-bottom:1px solid #dce6dc;text-align:left;font-variant-numeric:tabular-nums}.readings th{color:#5f716a;background:#f0f5ef;font-size:10px}.readings tr:last-child td{border-bottom:0}.btns{display:flex;gap:8px}.btns button{flex:1;background:#f6fbf6;box-shadow:0 2px 0 #dce8db}
@media(max-width:760px){main{padding:9px;gap:7px}.steps{display:none}.lab{grid-template-columns:1fr}.stage{min-height:360px}.panel{padding:8px}.stand-rod{left:12%}.clamp{left:12%}.rig{left:26%}.ruler{left:44%}}
</style></head><body><main>
<header><div><p class='kicker'>INTERACTIVE PHYSICS LAB</p><h1>Hooke's Law: Spring Extension</h1></div></header>
<p class='hint'>Try this: pick a mass, drag it onto the hanger, read the extension, then keep adding masses and watch force divided by extension stay constant.</p>
<div class='note'><b>Key idea:</b> A spring obeys F = k x. Each added weight stretches the spring in proportion to its force, so force divided by extension is the constant spring constant k.</div>
<div class='steps'><div class='step'><b>1</b>Choose a slotted mass and drag it onto the hanger.</div><div class='step'><b>2</b>Read the new extension on the ruler.</div><div class='step'><b>3</b>Add more masses one at a time.</div><div class='step'><b>4</b>Check that force / extension stays constant.</div></div>
<section class='lab'><div id='stage' class='stage'>
<div class='clamp'></div><div class='stand-rod'></div><div class='stand-base'></div>
<div class='ruler' id='ruler'></div>
<div class='rig'><div id='spring' class='spring'></div><div id='hanger' class='hanger'><div id='readbadge' class='readbadge'>x = 0.0 cm</div></div><div id='stack'></div></div>
<div class='tray'><div class='tray-label'>MASSES</div><button id='mass' class='mass' type='button'>100 g<br>slotted mass</button><div class='tray-copy'>Drag a mass onto the hanger. <b>g = 9.8 m/s&sup2;</b>, spring constant <b>k = 49 N/m</b>. Supply is unlimited.</div></div>
</div><aside class='panel'>
<div class='card'><div class='readrow'><div class='label'>Mass to add</div><div id='sizeVal' class='value'>100 g</div></div><input id='massSize' class='slider' type='range' min='20' max='200' step='20' value='100'></div>
<div class='grid2'><div class='card'><div class='label'>Total load</div><div id='massVal' class='value'>0 g</div></div><div class='card'><div class='label'>Force</div><div id='forceVal' class='value'>0.00 N</div></div></div>
<div class='grid2'><div class='card'><div class='label'>Extension</div><div id='extVal' class='value'>0.0 cm</div></div><div class='card kcard'><div class='label'>k = F / x</div><div id='kVal' class='value'>-</div></div></div>
<div class='card'><div class='label'>Lab state</div><div id='status' class='status'>Drag a mass onto the hanger.</div></div>
<div class='card'><div class='label'>Readings</div><table class='readings'><thead><tr><th>Total (g)</th><th>Force (N)</th><th>Ext (cm)</th></tr></thead><tbody id='rows'></tbody></table></div>
<div class='btns'><button id='removeOne' type='button'>Remove last</button><button id='resetSpring' type='button'>Reset the spring</button></div>
</aside></section></main>
<script>
(function(){
  var G=9.8,K=49,MAXW=8,PXCM=5,BASE=64;
  var weights=[],current=100;
  var stage=document.getElementById('stage'),massChip=document.getElementById('mass');
  var spring=document.getElementById('spring'),hanger=document.getElementById('hanger'),stack=document.getElementById('stack');
  var readbadge=document.getElementById('readbadge'),ruler=document.getElementById('ruler');
  var massVal=document.getElementById('massVal'),forceVal=document.getElementById('forceVal');
  var extVal=document.getElementById('extVal'),kVal=document.getElementById('kVal');
  var status=document.getElementById('status'),rows=document.getElementById('rows');
  var sizeVal=document.getElementById('sizeVal'),massSize=document.getElementById('massSize');
  var drag=false,offsetX=0,offsetY=0;
  function bridge(message){try{window.parent.postMessage(message,'*')}catch(error){}}
  function totalG(){var sum=0;for(var i=0;i<weights.length;i++)sum+=weights[i];return sum}
  function forceOf(grams){return grams/1000*G}
  function extCmOf(grams){return forceOf(grams)/K*100}
  function buildRuler(){for(var c=0;c<=24;c+=2){var y=c*PXCM+4;var line=document.createElement('i');line.style.top=y+'px';ruler.appendChild(line);var tag=document.createElement('span');tag.style.top=y+'px';tag.textContent=c;ruler.appendChild(tag)}}
  function renderStack(){while(stack.firstChild)stack.removeChild(stack.firstChild);for(var i=0;i<weights.length;i++){var d=document.createElement('div');d.className='disc';d.textContent=weights[i]+' g';stack.appendChild(d)}}
  function renderRows(){while(rows.firstChild)rows.removeChild(rows.firstChild);var run=0;for(var i=0;i<weights.length;i++){run+=weights[i];var tr=document.createElement('tr');[String(run),forceOf(run).toFixed(2),extCmOf(run).toFixed(1)].forEach(function(text){var td=document.createElement('td');td.textContent=text;tr.appendChild(td)});rows.appendChild(tr)}}
  function update(){
    var g=totalG(),ext=extCmOf(g),f=forceOf(g);
    spring.style.height=(BASE+ext*PXCM)+'px';
    massVal.textContent=g+' g';forceVal.textContent=f.toFixed(2)+' N';extVal.textContent=ext.toFixed(1)+' cm';
    kVal.textContent=g>0?(f/(ext/100)).toFixed(0)+' N/m':'-';
    readbadge.textContent='x = '+ext.toFixed(1)+' cm';
    renderStack();renderRows();
    if(g===0){status.textContent='Drag a mass onto the hanger.';return}
    if(weights.length<MAXW){status.textContent=g+' g gives '+ext.toFixed(1)+' cm. F / x = '+(f/(ext/100)).toFixed(0)+' N/m. Add another mass.';return}
    status.textContent='However you split the load, F / x stays constant at '+K+' N/m. That is Hooke\'s law.';
  }
  function addMass(){if(weights.length>=MAXW)return;weights.push(current);update();bridge({type:'synapse_event',control:'add_mass',value:totalG()})}
  function inHanger(){var a=massChip.getBoundingClientRect(),b=hanger.getBoundingClientRect(),x=a.left+a.width/2,y=a.top+a.height/2;return x>b.left-40&&x<b.right+40&&y>b.top-50&&y<b.bottom+80}
  massChip.addEventListener('pointerdown',function(event){drag=true;var box=massChip.getBoundingClientRect();offsetX=event.clientX-box.left;offsetY=event.clientY-box.top;massChip.classList.add('dragging');massChip.style.position='fixed';massChip.style.zIndex='9';massChip.style.width=box.width+'px';massChip.style.left=box.left+'px';massChip.style.top=box.top+'px';massChip.setPointerCapture(event.pointerId);event.preventDefault()});
  massChip.addEventListener('pointermove',function(event){if(!drag)return;massChip.style.left=(event.clientX-offsetX)+'px';massChip.style.top=(event.clientY-offsetY)+'px'});
  function drop(event){if(!drag)return;drag=false;massChip.classList.remove('dragging');try{massChip.releasePointerCapture(event.pointerId)}catch(error){}var hit=inHanger();massChip.style.position='';massChip.style.left='';massChip.style.top='';massChip.style.zIndex='';massChip.style.width='';if(hit)addMass()}
  massChip.addEventListener('pointerup',drop);massChip.addEventListener('pointercancel',drop);
  massSize.addEventListener('input',function(){current=+massSize.value;sizeVal.textContent=current+' g';massChip.innerHTML=current+' g<br>slotted mass';bridge({type:'synapse_event',control:'mass_size',value:current})});
  document.getElementById('removeOne').addEventListener('click',function(){if(weights.length===0)return;weights.pop();update();bridge({type:'synapse_event',control:'remove_mass',value:totalG()})});
  document.getElementById('resetSpring').addEventListener('click',function(){weights=[];update();bridge({type:'synapse_event',control:'reset',value:true})});
  try{buildRuler();update();window.requestAnimationFrame(function(){bridge({type:'synapse_ready'})})}catch(error){bridge({type:'synapse_error',message:String(error.message||error).slice(0,200)})}
})();
</script></body></html>'''
)

HOOKES_LAW_PLAN = ArtifactPlan(
    title="Hooke's Law: Spring Extension",
    learning_objective="Show that a spring's extension is proportional to the load, and find the spring constant from force divided by extension.",
    variables=[Variable(name='load', unit='g', min=0, max=600, default=0)],
    governing_model=(
        "Hooke's law F = k x with k = 49 N/m and g = 9.8 m/s^2. Each 100 g slotted mass "
        'adds a weight of 0.1 kg x 9.8 = 0.98 N, extending the spring by x = F / k = '
        '0.98 / 49 = 0.0200 m = 2.0 cm. Extension is directly proportional to force, so '
        'F / x stays constant at 49 N/m across the loads.'
    ),
    expected_behaviors=[
        'dragging a 100 g mass onto the hanger adds 0.98 N and 2.0 cm of extension',
        'each further mass adds an equal 2.0 cm step, showing extension is proportional to force',
        'force divided by extension stays constant at 49 N/m for every load',
        'removing a mass or resetting returns the spring to its shorter length',
    ],
    layout_notes=(
        'Show a retort stand with a clamped spring, a hanger, and a centimetre ruler beside the '
        'spring, with a tray of draggable 100 g slotted masses below. Dragging a mass onto the '
        'hanger is the required direct-manipulation interaction; a remove and reset button sit in '
        'the readout panel with the load, force, extension, and spring-constant cards.'
    ),
    library='none',
    interaction_mode='drag_drop',
    interaction_requirements=[
        'Drag a 100 g slotted mass onto the spring hanger to add load.',
        'Add masses one at a time and read the extension against the ruler.',
    ],
    study_note=(
        "A spring obeys Hooke's law: its extension is proportional to the force stretching it. "
        'Equal 100 g masses each add an equal 2.0 cm extension, so force divided by extension is '
        'the constant spring constant, here 49 N/m.'
    ),
    steps=[
        'Drag a 100 g mass onto the hanger.',
        'Read the new extension on the ruler.',
        'Add more masses one at a time.',
        'Check that force divided by extension stays constant.',
    ],
)

HOOKES_LAW_SPOT_CHECKS = [
    {
        'inputs': '100 g total load (0.98 N) on a k = 49 N/m spring',
        'expected': 'extension = F / k = 0.98 / 49 = 0.0200 m = 2.0 cm; F / x = 49 N/m',
        'code_derived': 'extCmOf(100) = (0.98 / 49) x 100 = 2.0 cm; forceOf(100) = 0.98 N and kVal renders 49 N/m',
    },
    {
        'inputs': '300 g total load (2.94 N) on the same spring',
        'expected': 'extension = 2.94 / 49 = 0.0600 m = 6.0 cm; F / x is still 49 N/m',
        'code_derived': 'extCmOf(300) = 6.0 cm and forceOf(300) = 2.94 N, so kVal recomputes F / x as 49 N/m',
    },
    {
        'inputs': 'Drag a mass onto the hanger, then release it outside the hanger',
        'expected': 'a valid drop adds the chosen mass and stretches the spring; a miss leaves the load unchanged',
        'code_derived': 'pointer handlers use getBoundingClientRect hit testing to push the mass and emit synapse_event; a miss restores the chip without changing state',
    },
]
