# ruff: noqa: E501
'''The deterministic yeast-fermentation experiment document and study plan.'''

from schemas.plan import ArtifactPlan, Variable

YEAST_FERMENTATION_ID = 'yeast_fermentation_products_v1'

YEAST_FERMENTATION_HTML = (
    r'''<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Yeast Fermentation Lab</title><style>
:root{--ink:#26362f;--dim:#63736c;--line:#dce7dc;--teal:#078d80;--teal-soft:#d9f3ee;--violet:#6f5ba6;--violet-soft:#eeeaff;--gold:#c68a00;--milk:#f4f3df;--wine:#bd5d7e;--paper:#fff;--bench:#eff5ed}*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden}body{color:var(--ink);background:#f6f9f4;font:14px/1.35 system-ui,sans-serif}main{height:100%;padding:14px;display:grid;grid-template-rows:auto auto auto auto minmax(0,1fr);gap:9px;background:linear-gradient(135deg,#fcfefb,#f4f8f1)}header{display:flex;align-items:center;justify-content:space-between;gap:14px}header>div{min-width:0}.kicker{margin:0 0 3px;color:var(--teal);font-size:10px;font-weight:900;letter-spacing:.13em}h1{margin:0;color:#b67a00;font:700 clamp(20px,2.1vw,29px)/1.08 Georgia,serif;letter-spacing:-.02em}button{min-height:40px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);font-weight:800;cursor:pointer}.hint{margin:0;padding:0 2px;color:#99433e;font-weight:750}.note{padding:8px 11px;border:1px solid #e9cf88;border-radius:10px;background:linear-gradient(90deg,#fff9e9,#fffdf8)}.note b{color:#a76e00}.steps{display:flex;gap:8px}.step{flex:1;min-width:0;min-height:55px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#fff;box-shadow:0 2px 0 #eaf0e9;font-size:12px}.step b{display:inline-grid;place-items:center;width:19px;height:19px;margin-right:4px;border-radius:50%;background:var(--violet);color:#fff}.lab{min-height:0;display:grid;grid-template-columns:minmax(0,1.68fr) minmax(270px,.72fr);gap:12px}.stage,.panel{min-height:0;border:1px solid var(--line);border-radius:16px;background:#fff}.stage{position:relative;overflow:hidden;min-height:380px;background:linear-gradient(#fbfffe 0 62%,var(--bench) 62%);box-shadow:inset 0 0 0 1px #fff}.stage:before{content:'ANAEROBIC FERMENTATION STATION';position:absolute;left:20px;top:14px;color:#4c847c;font-size:10px;font-weight:900;letter-spacing:.12em}.stage:after{content:'';position:absolute;z-index:0;left:0;right:0;bottom:0;height:38%;border-top:1px solid #dbe7da;background:repeating-linear-gradient(90deg,transparent 0 45px,#fff8 45px 46px),linear-gradient(#edf4ea,#e7efE3);pointer-events:none}.delivery{position:absolute;z-index:1;border:3px dashed #9cacaa;border-bottom:0;border-radius:14px 14px 0 0;opacity:.5;transition:.25s}.delivery.active{border-color:#168f84;border-style:solid;opacity:1;box-shadow:0 0 0 3px #ccf0e9}.delivery-a{left:23%;top:29%;width:50%;height:25%}.delivery-b{left:48%;top:38%;width:42%;height:17%}.boiling{position:absolute;z-index:3;top:18%;width:92px;height:236px;border:4px solid #56716d;border-top:0;border-radius:0 0 26px 26px;background:linear-gradient(90deg,#e5f7f8,#fff 40%,#d9f0f2);box-shadow:inset 10px 0 #ffffff99,0 4px 0 #d6e0d6;overflow:visible}.tube-a{left:17%}.tube-b{left:43%}.boiling:before{content:'';position:absolute;left:calc(50% - 40px);top:-16px;width:80px;height:22px;border:4px solid #8b6840;border-radius:8px 8px 3px 3px;background:#d8b678}.boiling:after{content:attr(data-name);position:absolute;top:-43px;left:50%;transform:translateX(-50%);white-space:nowrap;color:#465a54;font-size:10px;font-weight:900;letter-spacing:.05em}.mix{position:absolute;z-index:1;left:4px;right:4px;bottom:4px;height:52%;border-radius:0 0 20px 20px;background:linear-gradient(#d8b780,#b8874e);transition:.3s}.tube-b .mix{background:linear-gradient(#f3d9a3,#d8aa64)}.mix.yeasted{background:linear-gradient(#f6e3a8,#dba860)}.oil-layer{position:absolute;z-index:2;left:5px;right:5px;bottom:51%;height:0;background:linear-gradient(#f7df65,#edbf25);opacity:0;transition:.25s}.oil-layer.sealed{height:13px;opacity:1}.tube-label{position:absolute;z-index:4;left:6px;right:6px;bottom:13px;padding:3px 4px;border-radius:8px;background:#fffdf0d9;color:#72552c;font-size:10px;font-weight:800;text-align:center}.temp{position:absolute;z-index:5;right:-20px;top:31px;width:17px;height:112px;border:2px solid #56716d;border-radius:9px;background:#f7ffff;box-shadow:inset 0 -35px #e25f60}.temp:after{content:attr(data-reading);position:absolute;top:-23px;left:-9px;white-space:nowrap;color:#4e625d;font-size:10px;font-weight:900}.lime{position:absolute;z-index:3;top:55%;width:76px;height:110px;border:4px solid #56716d;border-top:0;border-radius:0 0 18px 18px;background:linear-gradient(90deg,#e4f7f8,#fff,#dff1f2);overflow:visible}.lime-a{left:70%}.lime-b{left:86%}.lime:before{content:attr(data-name);position:absolute;top:-23px;left:50%;transform:translateX(-50%);white-space:nowrap;color:#465a54;font-size:10px;font-weight:900}.lime-water{position:absolute;left:4px;right:4px;bottom:4px;height:50%;border-radius:0 0 12px 12px;background:#bfe7f0;transition:.3s}.lime-water.cloudy{background:linear-gradient(#f5f2dc,#ece7c8);box-shadow:inset 0 5px #fffef5}.gas{position:absolute;z-index:4;left:50%;bottom:48%;width:48px;height:70px;transform:translateX(-50%);pointer-events:none}.gas i{position:absolute;bottom:0;width:8px;height:8px;border-radius:50%;background:#fff8cf;opacity:0}.gas.active i{animation:rise 1.35s infinite ease-in}.gas i:nth-child(1){left:5px;animation-delay:.1s}.gas i:nth-child(2){left:22px;animation-delay:.45s}.gas i:nth-child(3){left:36px;animation-delay:.8s}@keyframes rise{0%{transform:translateY(0) scale(.55);opacity:0}22%{opacity:1}100%{transform:translateY(-66px) scale(1.2);opacity:0}}
'''
    r'''.tool{position:absolute;z-index:8;border:2px solid #0b9b8e;border-radius:18px;background:linear-gradient(135deg,#e9fffa,#c9f0e9);box-shadow:0 4px 0 #99d6cb;color:#075f56;font-size:11px;line-height:1.1;text-align:center;touch-action:none;user-select:none}.tool.dragging{opacity:.88;box-shadow:0 10px 22px #0b8e8066;transform:scale(1.04)}.yeast-tool{left:4%;top:73%;width:106px;min-height:57px;padding:8px 12px}.yeast-tool:before{content:'';position:absolute;top:-12px;left:40px;width:22px;height:13px;border-radius:7px 7px 2px 2px;background:#cc9e54}.oil-tool{left:4%;top:88%;width:106px;min-height:43px;padding:8px}.oil-tool:before{content:'';position:absolute;top:-9px;left:41px;width:20px;height:11px;border-radius:7px 7px 2px 2px;background:#e7c44b}.lead-tool{width:91px;min-height:43px;padding:8px;border-color:#7460ad;background:linear-gradient(135deg,#f5f2ff,#e6dfff);box-shadow:0 4px 0 #c6b9e6;color:#504087}.lead-a{left:31%;top:74%}.lead-b{left:45%;top:85%}.lead-tool:before{content:'L';position:absolute;left:-13px;top:10px;width:12px;height:17px;border:2px solid #7460ad;border-right:0;border-radius:8px 0 0 8px;color:transparent}.timer{position:absolute;z-index:8;right:17%;top:10%;width:99px;height:99px;border:7px solid #7260a8;border-radius:50%;background:radial-gradient(circle,#fff 0 53%,#eeeaff 54%);box-shadow:0 4px 0 #c8bde2;touch-action:none;user-select:none}.timer:before{content:'';position:absolute;left:46px;top:14px;width:5px;height:33px;border-radius:5px;background:#7260a8;transform-origin:50% 35px;transform:rotate(var(--dial,-115deg));transition:transform .1s}.timer:after{content:'DRAG DIAL';position:absolute;left:50%;top:42px;transform:translateX(-50%);white-space:nowrap;color:#574883;font-size:9px;font-weight:900}.time-readout{position:absolute;z-index:9;right:15%;top:34%;min-width:105px;padding:5px 7px;border-radius:10px;background:#ffffffdc;color:#574883;font-size:11px;font-weight:900;text-align:center}.stage-hint{position:absolute;z-index:12;left:16px;top:34px;max-width:46%;padding:6px 10px;border:1px solid #d8e7d8;border-radius:14px;background:#f8fcf6ef;box-shadow:0 2px 0 #dce8dc;color:#28614c;font-size:11px;font-weight:800;text-align:left}.tray{position:absolute;z-index:20;left:3%;bottom:4%;width:54%;display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:8px 10px;border:1px dashed #b9c8bb;border-radius:12px;background:#f4faf3e6}.tray-label{width:100%;color:#4c847c;font-size:9px;font-weight:900;letter-spacing:.1em}.tray .tool{position:relative;left:auto;top:auto;bottom:auto;z-index:auto}.panel{padding:12px;display:grid;align-content:start;gap:9px;background:linear-gradient(#fff,#fbfdf9);box-shadow:inset 0 0 0 1px #fff}.card{padding:10px;border:1px solid var(--line);border-radius:11px;background:linear-gradient(135deg,#fff,#f8fbf7)}.label{color:var(--dim);font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.status{margin-top:4px;color:var(--violet);font-weight:800;line-height:1.3}.result{margin-top:4px;color:#385349;font:700 16px/1.17 Georgia,serif}.observations{width:100%;margin-top:5px;border-collapse:separate;border-spacing:0;overflow:hidden;border:1px solid #dce6dc;border-radius:8px;font-size:11px}.observations th,.observations td{padding:6px;border-bottom:1px solid #dce6dc;text-align:left}.observations th{color:#5f716a;background:#f0f5ef;font-size:10px}.observations tr:last-child td{border-bottom:0}.answer{border-color:#b7e5db;background:linear-gradient(135deg,#f0fff9,#fafffd)}.answer .result{color:#087c70}.reset-wide{width:100%;background:#f6fbf6;box-shadow:0 2px 0 #dce8db}@media(max-width:760px){main{padding:9px;gap:7px}.steps{display:none}.lab{grid-template-columns:1fr}.stage{min-height:390px}.panel{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;padding:8px}.panel .answer,.panel .reset-wide{grid-column:1/-1}.boiling{transform:scale(.86);transform-origin:top}.tube-a{left:16%}.tube-b{left:42%}.lime-a{left:68%}.lime-b{left:84%}.timer{right:7%;transform:scale(.82);transform-origin:top right}.time-readout{right:5%;top:31%}.stage-hint{max-width:60%}.tray{width:auto;right:3%}}
</style></head><body><main>
<header><div><p class='kicker'>INTERACTIVE BIOLOGY LAB</p><h1>Yeast Fermentation: Find the Products</h1></div></header>
<p class='hint'>Build the anaerobic setup, then drag the timer dial forward and compare the yeast tube with its control.</p>
<div class='note'><b>Key idea:</b> In an anaerobic glucose solution, yeast releases energy while making ethanol and carbon dioxide. Carbon dioxide turns limewater cloudy.</div>
<div class='steps'><div class='step'><b>1</b>Drag yeast into boiling tube A.</div><div class='step'><b>2</b>Seal both tubes with paraffin oil.</div><div class='step'><b>3</b>Drag each delivery-tube end into its limewater.</div><div class='step'><b>4</b>Turn the timer dial to incubate for 60 minutes.</div></div>
<section class='lab'><div id='stage' class='stage'>
<div id='pathA' class='delivery delivery-a'></div><div id='pathB' class='delivery delivery-b'></div>
<div id='tubeA' class='boiling tube-a' data-name='TUBE A: YEAST'><div id='mixA' class='mix'></div><div id='oilA' class='oil-layer'></div><div id='tempA' class='temp' data-reading='24.0 deg C'></div><div id='gasA' class='gas'><i></i><i></i><i></i></div><div class='tube-label'>5% glucose</div></div>
<div id='tubeB' class='boiling tube-b' data-name='TUBE B: CONTROL'><div class='mix'></div><div id='oilB' class='oil-layer'></div><div id='tempB' class='temp' data-reading='24.0 deg C'></div><div class='tube-label'>5% glucose only</div></div>
<div id='limeA' class='lime lime-a' data-name='LIMEWATER A'><div id='waterA' class='lime-water'></div></div><div id='limeB' class='lime lime-b' data-name='LIMEWATER B'><div id='waterB' class='lime-water'></div></div>
<div class='tray'><span class='tray-label'>SET-UP TOOLS &middot; DRAG ONTO THE APPARATUS</span><button id='yeast' class='tool yeast-tool' type='button'>5% yeast<br>suspension</button><button id='oil' class='tool oil-tool' type='button'>paraffin oil</button><button id='leadA' class='tool lead-tool' type='button'>tube end A</button><button id='leadB' class='tool lead-tool' type='button'>tube end B</button></div>
<div id='timer' class='timer' role='button' tabindex='0'></div><div id='timeReadout' class='time-readout'>0 / 60 min</div><div id='stageHint' class='stage-hint'>Add yeast to tube A to begin.</div>
</div><aside class='panel'>
<div class='card'><div class='label'>Lab state</div><div id='status' class='status'>Add yeast to tube A.</div></div>
<div class='card'><div class='label'>Observations</div><table class='observations'><thead><tr><th>Tube</th><th>Limewater</th><th>Smell</th></tr></thead><tbody><tr><td>A</td><td id='limeResultA'>clear</td><td id='smellA'>none</td></tr><tr><td>B</td><td id='limeResultB'>clear</td><td id='smellB'>none</td></tr></tbody></table></div>
<div class='card'><div class='label'>Temperature change</div><div id='temperatureResult' class='result'>A: 24.0 deg C | B: 24.0 deg C</div></div>
<div class='card answer'><div class='label'>Conclusion</div><div id='conclusion' class='result'>Complete the setup, then incubate.</div></div><button id='newTrial' class='reset-wide' type='button'>Run a fresh trial</button>
</aside></section></main>
'''
    r'''<script>
(function(){
  var state={yeast:false,oilA:false,oilB:false,leadA:false,leadB:false,time:0,timerDrag:false};
  var home={yeast:{left:'4%',top:'73%'},oil:{left:'4%',top:'88%'},leadA:{left:'31%',top:'74%'},leadB:{left:'45%',top:'85%'}};
  var stage=document.getElementById('stage'),yeast=document.getElementById('yeast'),oil=document.getElementById('oil');
  var leadA=document.getElementById('leadA'),leadB=document.getElementById('leadB'),tubeA=document.getElementById('tubeA'),tubeB=document.getElementById('tubeB');
  var limeA=document.getElementById('limeA'),limeB=document.getElementById('limeB'),oilA=document.getElementById('oilA'),oilB=document.getElementById('oilB');
  var mixA=document.getElementById('mixA'),pathA=document.getElementById('pathA'),pathB=document.getElementById('pathB');
  var gasA=document.getElementById('gasA'),waterA=document.getElementById('waterA'),tempA=document.getElementById('tempA'),tempB=document.getElementById('tempB');
  var timer=document.getElementById('timer'),timeReadout=document.getElementById('timeReadout'),hint=document.getElementById('stageHint'),status=document.getElementById('status');
  var limeResultA=document.getElementById('limeResultA'),limeResultB=document.getElementById('limeResultB'),smellA=document.getElementById('smellA'),smellB=document.getElementById('smellB');
  var temperatures=document.getElementById('temperatureResult'),conclusion=document.getElementById('conclusion');
  function bridge(message){try{window.parent.postMessage(message,'*')}catch(error){}}
  function contained(source,target){var a=source.getBoundingClientRect(),b=target.getBoundingClientRect(),x=a.left+a.width/2,y=a.top+a.height/2;return x>b.left&&x<b.right&&y>b.top&&y<b.bottom}
  function restore(element){element.style.position='';element.style.left='';element.style.top='';element.style.width='';element.style.zIndex='';element.style.transform='';element.classList.remove('dragging')}
  function setupComplete(){return state.yeast&&state.oilA&&state.oilB&&state.leadA&&state.leadB}
  function nextInstruction(){
    if(!state.yeast)return 'Add yeast to tube A to begin.';
    if(!state.oilA||!state.oilB)return 'Seal both boiling tubes with paraffin oil.';
    if(!state.leadA||!state.leadB)return 'Place both delivery-tube ends below the limewater surface.';
    return 'Drag across the timer dial to incubate the experiment.';
  }
  function update(){
    var temp=24+(state.time/60)*3,gas=state.time>=12&&setupComplete(),cloudy=state.time>=45&&setupComplete(),done=state.time>=60&&setupComplete();
    tempA.setAttribute('data-reading',temp.toFixed(1)+' deg C');tempB.setAttribute('data-reading','24.0 deg C');
    timer.style.setProperty('--dial',(-115+(state.time/60)*230)+'deg');timeReadout.textContent=state.time+' / 60 min';
    gasA.classList.toggle('active',gas);waterA.classList.toggle('cloudy',cloudy);
    limeResultA.textContent=cloudy?'cloudy / milky':'clear';limeResultB.textContent='clear';
    smellA.textContent=done?'ethanol smell':'none';smellB.textContent='none';
    temperatures.textContent='A: '+temp.toFixed(1)+' deg C | B: 24.0 deg C';
    if(done){status.textContent='Run complete: compare tube A with control tube B.';hint.textContent='Carbon dioxide reached limewater in tube A.';conclusion.textContent='Chemical products: carbon dioxide and ethanol. Energy was released.';return}
    if(setupComplete()&&state.time>0){status.textContent='Fermentation is underway: watch tube A, not the control.';hint.textContent=cloudy?'Limewater A is turning milky.':'Advance the dial toward 60 minutes.';conclusion.textContent='Keep incubating to reveal the products.';return}
    status.textContent=nextInstruction();hint.textContent=nextInstruction();conclusion.textContent='Complete the setup, then incubate.';
  }
  function reset(){
    state.yeast=false;state.oilA=false;state.oilB=false;state.leadA=false;state.leadB=false;state.time=0;state.timerDrag=false;
    restore(yeast,'yeast');restore(oil,'oil');restore(leadA,'leadA');restore(leadB,'leadB');mixA.classList.remove('yeasted');oilA.classList.remove('sealed');oilB.classList.remove('sealed');pathA.classList.remove('active');pathB.classList.remove('active');gasA.classList.remove('active');waterA.classList.remove('cloudy');update();bridge({type:'synapse_event',control:'reset',value:true});
  }
  function wireDrag(element,key,onDrop){
    var active=false,offsetX=0,offsetY=0;
    element.addEventListener('pointerdown',function(event){active=true;var box=element.getBoundingClientRect();offsetX=event.clientX-box.left;offsetY=event.clientY-box.top;element.classList.add('dragging');element.style.position='fixed';element.style.zIndex='40';element.style.width=box.width+'px';element.style.left=box.left+'px';element.style.top=box.top+'px';element.setPointerCapture(event.pointerId);event.preventDefault()});
    element.addEventListener('pointermove',function(event){if(!active)return;element.style.left=(event.clientX-offsetX)+'px';element.style.top=(event.clientY-offsetY)+'px'});
    function drop(event){if(!active)return;active=false;try{element.releasePointerCapture(event.pointerId)}catch(error){}var changed=onDrop();restore(element);if(changed)update()}
    element.addEventListener('pointerup',drop);element.addEventListener('pointercancel',drop);
  }
  wireDrag(yeast,'yeast',function(){if(!contained(yeast,tubeA))return false;state.yeast=true;mixA.classList.add('yeasted');bridge({type:'synapse_event',control:'add_yeast_to_tube_a',value:true});return true});
  wireDrag(oil,'oil',function(){if(contained(oil,tubeA)){state.oilA=true;oilA.classList.add('sealed');bridge({type:'synapse_event',control:'seal_tube_a',value:'paraffin_oil'});return true}if(contained(oil,tubeB)){state.oilB=true;oilB.classList.add('sealed');bridge({type:'synapse_event',control:'seal_tube_b',value:'paraffin_oil'});return true}return false});
  wireDrag(leadA,'leadA',function(){if(!contained(leadA,limeA))return false;state.leadA=true;pathA.classList.add('active');bridge({type:'synapse_event',control:'connect_delivery_tube_a',value:true});return true});
  wireDrag(leadB,'leadB',function(){if(!contained(leadB,limeB))return false;state.leadB=true;pathB.classList.add('active');bridge({type:'synapse_event',control:'connect_delivery_tube_b',value:true});return true});
  timer.addEventListener('pointerdown',function(event){if(!setupComplete()){hint.textContent=nextInstruction();return}state.timerDrag=true;timer.setPointerCapture(event.pointerId);event.preventDefault()});
  timer.addEventListener('pointermove',function(event){if(!state.timerDrag)return;var box=timer.getBoundingClientRect(),ratio=Math.max(0,Math.min(1,(event.clientX-box.left)/box.width)),next=Math.round(ratio*60);if(next!==state.time){state.time=next;update();bridge({type:'synapse_event',control:'incubation_minutes',value:state.time})}});
  function stopTimer(event){if(!state.timerDrag)return;state.timerDrag=false;try{timer.releasePointerCapture(event.pointerId)}catch(error){}if(setupComplete()&&state.time>=54&&state.time<60){state.time=60;update();bridge({type:'synapse_event',control:'incubation_minutes',value:60})}}
  timer.addEventListener('pointerup',stopTimer);timer.addEventListener('pointercancel',stopTimer);
  document.getElementById('newTrial').addEventListener('click',reset);
  try{update();window.requestAnimationFrame(function(){bridge({type:'synapse_ready'})})}catch(error){bridge({type:'synapse_error',message:String(error.message||error).slice(0,200)})}
})();
</script></body></html>'''
)

YEAST_FERMENTATION_PLAN = ArtifactPlan(
    title='Yeast Fermentation: Find the Products',
    learning_objective='Use a yeast-versus-control setup to identify carbon dioxide and ethanol as products of anaerobic fermentation.',
    variables=[Variable(name='incubation time', unit='min', min=0, max=60, default=0)],
    governing_model=(
        'C6H12O6 -> 2 C2H5OH + 2 CO2 with energy released. Tube A contains glucose and yeast under paraffin oil; tube B is a glucose-only control. Carbon dioxide bubbles into limewater and forms a cloudy calcium carbonate suspension.'
    ),
    expected_behaviors=[
        'adding yeast to tube A enables anaerobic fermentation while tube B remains the control',
        'paraffin oil seals both boiling tubes and delivery tubes carry any gas to limewater',
        'after incubation, only tube A makes carbon dioxide, clouds limewater, warms slightly, and has an ethanol smell',
        'the conclusion distinguishes chemical products from released energy',
    ],
    layout_notes='Show two labelled boiling tubes, delivery tubes, two limewater test tubes, direct-manipulation setup tools, and a pointer-operated incubation dial.',
    library='none',
    interaction_mode='drag_drop',
    interaction_requirements=[
        'Drag 5% yeast suspension into boiling tube A.',
        'Drag paraffin oil and both delivery-tube ends onto their visible target vessels.',
        'Turn the physical incubation dial with a pointer gesture to progress the run.',
    ],
    study_note='Yeast fermentation of glucose in anaerobic conditions produces ethanol and carbon dioxide while releasing energy. The limewater test is evidence for carbon dioxide; tube B is the no-yeast control.',
    steps=[
        'Drag yeast suspension into boiling tube A.',
        'Seal both tubes with paraffin oil.',
        'Connect each delivery tube to its limewater test tube.',
        'Turn the dial to 60 minutes and compare A with B.',
    ],
)

YEAST_FERMENTATION_SPOT_CHECKS = [
    {
        'inputs': 'Tube A receives yeast, is sealed with paraffin oil, is connected to limewater, and the dial reaches 60 min.',
        'expected': 'Tube A produces carbon dioxide bubbles, its limewater becomes cloudy, the temperature increases modestly, and ethanol is reported.',
        'code_derived': 'finish() marks waterA cloudy, activates gasA, sets tube A to 27.0 deg C, and renders the ethanol conclusion.',
    },
    {
        'inputs': 'Tube B contains glucose but no yeast and completes the same sealed control setup.',
        'expected': 'Tube B limewater stays clear, temperature stays at 24.0 deg C, and no ethanol smell is detected.',
        'code_derived': 'update() only changes control outputs when tube A has the yeast-driven fermentation state; B remains the comparison control.',
    },
    {
        'inputs': 'A setup action occurs outside its target, or Reset is selected.',
        'expected': 'An invalid drop does not unlock incubation; Reset restores the unassembled, 0-minute state.',
        'code_derived': 'drop handlers use getBoundingClientRect hit checks and reset() clears yeast, seals, connections, time, results, and visual classes.',
    },
]
