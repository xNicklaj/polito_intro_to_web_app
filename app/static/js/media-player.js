const rangeInputs = document.querySelectorAll('input[type="range"]')
const playBtn = document.querySelector('#mp-play-button')
const audio = document.querySelector('audio')
const progressBar = document.querySelector('#mp-progress-bar')
const volumeBar = document.querySelector('#mp-volume-bar')
const volumeIcon = document.querySelector('.mp-volume-wrapper i')
let tickid = 0

// This input handler handles the style of the range bars, and is purely cosmetic. It can be ignored.
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


/*
 * Defines a ticking mechanism that syncs the current state of the media player with the server, so that whenever the client
 * moves to another page in the website, the state syncs up and starts from where it was left in the previous page.
 * While this works very well, it's not exactly inexepensive, since right now it runs every time the browser detects a change in the
 * currentTime property of the audio tag.
 * A good and efficient solution could be to wrap the tick in a debouncer that allows it to run say only once every second, although it does
 * lead to little desyncs upon resume.
 */
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
    fetch("/api/tickupdate", {
      method: 'POST',
      body: tickdata
    })
    this.ntick += 1
  }
}

mp = new MediaPlayer()

// Handle the click on the custom start / stop button
playBtn.addEventListener('click', () => {
  if(audio.paused){
    audio.play()
  }
  else{
    audio.pause()
  }
})

// Update the progress bar on every timeupdate event fired by the audio
audio && audio.addEventListener('timeupdate', (e) =>{
  const prog = (audio.currentTime) / (audio.duration) * (progressBar.max - progressBar.min)
  progressBar.style.backgroundSize = prog + '% 100%'
  progressBar.value = prog
  mp.tick() 
})

// Resume ticking when the audio is restarted, both manually and via javascript.
audio && audio.addEventListener('play', () => {
  mp.tick()
  document.querySelector('.mp-play-wrapper .compositeplay i:last-child').classList = 'bi-pause-fill pausetransform'
})


// Stop ticking when the audio is stopped, both manually and via javascript.
audio && audio.addEventListener('pause', () => {
  mp.tick()
  document.querySelector('.mp-play-wrapper .compositeplay i:last-child').classList = 'bi-play-fill'
})

// Set some cosmetic in the progressbar when the volume changes
audio && audio.addEventListener('volumechange', () => {
  vol = audio.volume
  localStorage.setItem('volume', vol)
  if(audio.volume === 0){
    volumeIcon.classList.add('bi-volume-mute')
  }else{
    volumeIcon.classList.remove('bi-volume-mute')
  }
})

// Set currentTime when seeking through the progress bar
progressBar.addEventListener('input', (e) => {
  const prog = (e.target.value - e.target.min) / (e.target.max - e.target.min)
  audio && (audio.currentTime = prog * audio.duration)
})

// Set audio volume when seeking through the volume bar
volumeBar.addEventListener('input', (e) => {
  const prog = (e.target.value - e.target.min) / (e.target.max - e.target.min)
  audio && (audio.volume = prog)
})

// Load last used volume and use the autoplay-mute trick to resume playing on page load.
window.addEventListener('load', (e) =>{
  if(audio){
    audio.volume = localStorage.getItem('volume')||1
    volumeBar.value = (audio.volume) * (volumeBar.max - volumeBar.min)
    volumeBar.style.backgroundSize = ((audio.volume)*100) + '% 100%'
  if(audio.volume === 0) volumeIcon.classList.add('bi-volume-mute')
  }
  if(audio && audio.hasAttribute('autoplay')){
    audio.removeAttribute('mute')
    if(audio.hasAttribute('data-currentTime')){
      audio.currentTime = audio.getAttribute('data-currentTime')
    }
    else audio.currentTime = 0
  }
})