/*
 * During testing it would sometimes happen that a form would be fired twice if double clicking on a submit button.
 * This easy fix disables all buttons and input[type="submit"] once the submit event is fired, so that it can only fire once until 
 * the page is reloaded.
 */
const forms = document.querySelectorAll('form')
forms.forEach(form => form.addEventListener('submit', (e) => { 
    let buttons = form.querySelectorAll('input[type="submit"]')
    form.querySelectorAll('button').forEach(b => buttons.append(b))
    
    buttons.forEach(b => b.disabled = true)
}))