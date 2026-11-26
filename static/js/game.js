const buttons = [...document.querySelectorAll('.choice')];
const playerFighter = document.querySelector('#player-fighter');
const machineFighter = document.querySelector('#machine-fighter');
const playerSprite = document.querySelector('#player-sprite');
const machineSprite = document.querySelector('#machine-sprite');
const playerBadge = document.querySelector('#player-badge');
const machineBadge = document.querySelector('#machine-badge');
const playerAssociation = document.querySelector('#player-association');
const machineAssociation = document.querySelector('#machine-association');
const playerName = document.querySelector('#player-name');
const machineName = document.querySelector('#machine-name');
const playerScore = document.querySelector('#player-score');
const machineScore = document.querySelector('#machine-score');
const status = document.querySelector('#status');
const blackScreen = document.querySelector('#black-screen');
const overlayKicker = document.querySelector('#overlay-kicker');
const overlayTitle = document.querySelector('#overlay-title');
const overlayText = document.querySelector('#overlay-text');
const overlayButton = document.querySelector('#overlay-button');
let locked = false;
let gameOver = false;
let currentCharacters = null;

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }
function disableChoices(v){ buttons.forEach(b => b.disabled = v); }
function flip(img, yes){ img.style.transform = yes ? 'scaleX(-1)' : 'scaleX(1)'; }
function sprite(img, character, state, isMachine){
  img.src = character.sprites[state];
  flip(img, isMachine);
  // sprite de morte tem tamanho próprio (definido em app.py)
  if(state === 'death' && character.death_height){
    img.classList.add('morte');
    img.style.setProperty('--h', character.death_height);
  } else {
    img.classList.remove('morte');
    img.style.removeProperty('--h');
  }
}
function clearState(){
  playerFighter.className='fighter player';
  machineFighter.className='fighter machine';
}
function resetRoundVisuals(){
  clearState();
  if(currentCharacters){
    setFighter('player',currentCharacters.player);
    setFighter('machine',currentCharacters.machine);
  }
}
function setFighter(side, character){
  const machine = side === 'machine';
  const img = machine ? machineSprite : playerSprite;
  const badge = machine ? machineBadge : playerBadge;
  const assoc = machine ? machineAssociation : playerAssociation;
  const name = machine ? machineName : playerName;
  badge.src = character.logo;
  assoc.textContent = character.association;
  name.textContent = character.character;
  sprite(img, character, 'standing', machine);
}
function setButtonLogos(){
  for(const b of buttons){
    const c = window.GAME_DATA.characters[b.dataset.choice];
    b.querySelector('img').src = c.logo;
  }
}
async function play(choice){
  if(locked) return;
  locked=true; disableChoices(true); clearState();
  status.textContent='ESCOLHA REGISTRADA...';
  let response;
  try{
    response=await fetch('/api/play',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({choice})});
  }catch(e){
    status.textContent='ERRO DE CONEXÃO'; locked=false; disableChoices(false); return;
  }
  const data=await response.json();
  if(!response.ok || !data.ok){ status.textContent=data.error||'ESCOLHA INVÁLIDA'; locked=false; disableChoices(false); return; }

  currentCharacters = data.characters;
  setFighter('player',data.characters.player);
  setFighter('machine',data.characters.machine);
  status.textContent=`${data.player.toUpperCase()} × ${data.machine.toUpperCase()}`;
  await sleep(450);

  sprite(playerSprite,data.characters.player,'moving',false);
  sprite(machineSprite,data.characters.machine,'moving',true);
  playerFighter.classList.add('moving'); machineFighter.classList.add('moving');
  await sleep(920);

  playerFighter.classList.remove('moving'); machineFighter.classList.remove('moving');
  playerFighter.classList.add('center','defending'); machineFighter.classList.add('center','defending');
  sprite(playerSprite,data.characters.player,'defending',false);
  sprite(machineSprite,data.characters.machine,'defending',true);
  await sleep(650);

  if(data.result==='draw'){
    sprite(playerSprite,data.characters.player,'standing',false);
    sprite(machineSprite,data.characters.machine,'standing',true);
    status.textContent='EMPATE — NINGUÉM MARCOU PONTO';
  } else if(data.result==='player'){
    sprite(playerSprite,data.characters.player,'standing',false);
    sprite(machineSprite,data.characters.machine,'death',true);
    machineFighter.classList.add('dead');
    status.textContent='VOCÊ VENCEU A RODADA';
  } else {
    sprite(playerSprite,data.characters.player,'death',false);
    sprite(machineSprite,data.characters.machine,'standing',true);
    playerFighter.classList.add('dead');
    status.textContent='A MÁQUINA VENCEU A RODADA';
  }

  playerScore.textContent=data.scores.player;
  machineScore.textContent=data.scores.machine;
  await sleep(1350);

  gameOver=!!data.game_over;
  blackScreen.classList.add('show');
  overlayKicker.textContent=gameOver?'FIM DE JOGO':'RODADA ENCERRADA';
  if(gameOver){
    overlayTitle.textContent=data.winner==='player'?'VOCÊ VENCEU!':'A MÁQUINA VENCEU!';
    overlayText.textContent=`Placar final: ${data.scores.player} × ${data.scores.machine}. Primeiro a 5.`;
    overlayButton.textContent='JOGAR NOVAMENTE';
  } else {
    overlayTitle.textContent=data.result==='draw'?'EMPATE':data.result==='player'?'PONTO PARA VOCÊ':'PONTO PARA A MÁQUINA';
    overlayText.textContent=`Placar: ${data.scores.player} × ${data.scores.machine}`;
    overlayButton.textContent='ESCOLHER NOVAMENTE';
  }
}
async function reset(){
  await fetch('/api/reset',{method:'POST'});
  playerScore.textContent='0'; machineScore.textContent='0'; clearState();
  currentCharacters={
    player:window.GAME_DATA.characters.pedra,
    machine:window.GAME_DATA.characters.pedra
  };
  setFighter('player',currentCharacters.player);
  setFighter('machine',currentCharacters.machine);
  status.textContent='ESCOLHA UMA JOGADA'; gameOver=false; locked=false; disableChoices(false);
  blackScreen.classList.remove('show');
}
buttons.forEach(b=>b.addEventListener('click',()=>play(b.dataset.choice)));
overlayButton.addEventListener('click',async()=>{
  if(gameOver) await reset();
  else { blackScreen.classList.remove('show'); resetRoundVisuals(); locked=false; disableChoices(false); status.textContent='ESCOLHA UMA JOGADA'; }
});
setButtonLogos();
setFighter('player',window.GAME_DATA.characters.pedra);
setFighter('machine',window.GAME_DATA.characters.pedra);

// Parallax discreto: só o cenário acompanha o movimento do mouse.
const arena = document.querySelector('#arena');
arena.addEventListener('pointermove', event => {
  const rect = arena.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - 0.5;
  const y = (event.clientY - rect.top) / rect.height - 0.5;
  arena.style.setProperty('--parallax-x', `${-x * 16}px`);
  arena.style.setProperty('--parallax-y', `${-y * 12}px`);
});
arena.addEventListener('pointerleave', () => {
  arena.style.setProperty('--parallax-x', '0px');
  arena.style.setProperty('--parallax-y', '0px');
});
