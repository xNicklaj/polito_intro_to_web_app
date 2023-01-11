const btns = document.querySelectorAll('.cat-btn-wrapper button')
btns.forEach(b => b.addEventListener('click', (e) => {
    chk = document.querySelector(`input[name="${e.target.getAttribute('for')}"]`)
    if(chk === null) return
    chk.checked = !chk.checked
    chk.dispatchEvent(new Event('change'))
    e.preventDefault() 
}))
const chkbx = document.querySelectorAll('.cat-btn-wrapper input')
chkbx.forEach(c => c.addEventListener('change', (e) => {
    const btn = document.querySelector(`.cat-btn-wrapper button[for="${e.target.name}"]`)
    if(e.target.checked) btn.classList.add("bg-accent-color", "fg-dark")
    else btn.classList.remove("bg-accent-color", "fg-dark")
}))