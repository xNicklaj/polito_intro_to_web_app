const rangeInputs = document.querySelectorAll('input[type="range"]')
const playBtn = document.querySelector('#mp-play-button')
const audio = document.querySelector('audio')
const progressBar = document.querySelector('#mp-progress-bar')
const volumeBar = document.querySelector('#mp-volume-bar')
const volumeIcon = document.querySelector('.mp-volume-wrapper i')
let tickid = 0

function handleInputChange(e) {
    let target = e.target
    if (e.target.type !== 'range') {
      target = document.getElementById('range')
    } 
    const min = target.min
    const max = target.max
    const val = target.value
    
    target.style.backgroundSize = (val - min) * 100 / (max - min) + '% 100%'
    target.value = val
}
document.querySelector("#mp-volume-bar").style.backgroundSize = '100% 100%'
rangeInputs.forEach(input => {
  input.addEventListener('input', handleInputChange)
})

class MediaPlayer{
  constructor(){
    this.ntick = 0
  }

  resetTick(){
    this.ntick = 0
  }

  tick(){
    const tickdata = new FormData()
    tickdata.append('isPlaying', !audio.paused)
    tickdata.append('currentTime', audio.currentTime)
    tickdata.append('playID', document.querySelector('.mp-play-meta a:first-child').href.split('pod')[1].slice(1).replace('/', '_'))
    tickdata.append('tickid', this.ntick)
    fetch("/tickupdate", {
      method: 'POST',
      body: tickdata
    })
    this.ntick += 1
  }
}

mp = new MediaPlayer()

playBtn.addEventListener('click', () => {
  if(audio.paused){
    audio.play()
  }
  else{
    audio.pause()
  }
})

audio && audio.addEventListener('timeupdate', (e) =>{
  const prog = (audio.currentTime) / (audio.duration) * (progressBar.max - progressBar.min)
  progressBar.style.backgroundSize = prog + '% 100%'
  progressBar.value = prog
  mp.tick() 
})

audio && audio.addEventListener('play', () => {
  mp.tick()
  document.querySelector('.mp-play-wrapper .compositeplay i:last-child').classList = 'bi-pause-fill pausetransform'
})


audio && audio.addEventListener('pause', () => {
  mp.tick()
  document.querySelector('.mp-play-wrapper .compositeplay i:last-child').classList = 'bi-play-fill'
})

audio && audio.addEventListener('volumechange', () => {
  vol = audio.volume
  localStorage.setItem('volume', vol)
  if(audio.volume === 0){
    volumeIcon.classList.add('bi-volume-mute')
  }else{
    volumeIcon.classList.remove('bi-volume-mute')
  }
})

progressBar.addEventListener('input', (e) => {
  const prog = (e.target.value - e.target.min) / (e.target.max - e.target.min)
  audio.currentTime = prog * audio.duration
})

volumeBar.addEventListener('input', (e) => {
  const prog = (e.target.value - e.target.min) / (e.target.max - e.target.min)
  audio.volume = prog
})

window.addEventListener('load', (e) =>{
  if(audio){
    audio.volume = localStorage.getItem('volume')||1
    volumeBar.value = (audio.volume) * (volumeBar.max - volumeBar.min)
    volumeBar.style.backgroundSize = ((audio.volume)*100) + '% 100%'
  if(audio.volume === 0) volumeIcon.classList.add('bi-volume-mute')
  }
  if(audio && audio.hasAttribute('autoplay')){
    if(audio.hasAttribute('data-currentTime')){
      audio.currentTime = audio.getAttribute('data-currentTime')
    }
    audio.removeAttribute('mute')
  }
})