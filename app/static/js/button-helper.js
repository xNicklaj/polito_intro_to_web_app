/*
 * This very useful piece of code allows me to create buttons that on click send post requests and eventually
 * redirect without having to wrap them around forms.
 */
document.querySelectorAll('*[data-post]').forEach(i => i.addEventListener('click', (e) => {
        const url = i.getAttribute('data-post')
        if(url === null || url === '') return
        fetch(url,{
            method: 'POST'
        }).then(r => {
            if(r.redirected)
                if(document.location.href === r.url) 
                    document.location.reload()
                else
                    document.location.href = r.url
        })
}))