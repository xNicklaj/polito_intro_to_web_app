const forms = document.querySelectorAll('form')
forms.forEach(form => form.addEventListener('submit', (e) => { 
    let buttons = form.querySelectorAll('input[type="submit"]')
    form.querySelectorAll('button').forEach(b => buttons.append(b))
    
    buttons.forEach(b => b.disabled = true)
}))