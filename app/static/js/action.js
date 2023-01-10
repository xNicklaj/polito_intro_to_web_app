const currentURI = document.location.pathname
const isEpisode = new RegExp('pod/\\d{1,6}/\\d{1,6}').test(currentURI)
const podcastid = currentURI.slice(1).split('/')[1]
let episodeid = 0
if(isEpisode) episodeid = currentURI.slice(1).split('/')[2]

const EditorState = {
    ACTIVE: 0,
    INACTIVE: 1
}

class Editor{
    constructor(){
        this.target = document.querySelector('.podcast-metadata')
        this.originalDOM = this.target.children[0]
        this.editorState = EditorState.INACTIVE
        const btn = this.target.querySelector('#edit-btn')
        if(btn == null) return
        btn.addEventListener('click', (e) => {
            if(this.editorState === EditorState.INACTIVE){
                let targetEndpoint = "#"
                if(isEpisode){
                    targetEndpoint = "/api/update/episode"
                }
                else targetEndpoint = "/api/update/podcast"
                this.editorState = EditorState.ACTIVE
                this.edit(targetEndpoint, isEpisode)
            }
            else{
                this.revert()
                this.editorState.INACTIVE
            }
            e.preventDefault()
        })
    }

    edit(endpoint='#', isEpisode=false){
        this.target.removeChild(this.originalDOM)
        this.target.innerHTML = `<form method='POST' action='${endpoint}'></form>`
        this.target.children[0].addEventListener('submit', this.onSubmit)
        this.target.children[0].appendChild(this.originalDOM.cloneNode(true))

        const presTitle = this.target.children[0].querySelector('h2').innerText
        this.target.children[0].querySelector('h2').innerHTML = `<input type="text" value="${presTitle}" name="update_title" class="accent-color"/>`
        const presDescription = this.target.children[0].querySelector('p').innerText
        this.target.children[0].querySelector('p').innerHTML = `<textarea type="text" name="update_description" class="w100 secondary-color p0">${presDescription}</textarea>`

        this.target.children[0].insertAdjacentHTML("beforeend", `<input type="hidden" name="update_podcastid" value="${podcastid}"/>`)
        if(isEpisode){
            this.target.children[0].insertAdjacentHTML("beforeend", `<input type="hidden" name="update_episodeid" value="${episodeid}"/>`)
        }
        this.target.children[0].querySelector('h2 input').focus()
    }

    revert(){
        this.target.innerHTML = ""
        this.target.children = this.originalDOM
    }
    
    onSubmit(e){
        this.revert()
    }
}

const editor = new Editor()
if(document.querySelector('#delete-btn') != null){
    document.querySelector('#delete-btn').addEventListener('click', () => {
        let targetEndpoint = `/delete/${podcastid}`
        if(isEpisode){
            targetEndpoint += `/${episodeid}`
        }
        document.location.href = targetEndpoint
    })
}


class NewEditor{
    constructor(target, watch_fields, hidden_fields, endpoint, method){
        this.target = target
        this.watch_fields = watch_fields
        this.hidden_fields = hidden_fields
        this.endpoint = endpoint
        this.method = method
        this.originalDOM = Array.from(this.target.children)
        this.editorState = EditorState.INACTIVE

        this.bindEdit()
    }

    edit(){
        const parent = this.target.parentElement
        const form = document.createElement('form')
        let visibilitySet = false
        form.action = this.endpoint
        form.method = this.method
        form.id = this.target.id
        this.originalDOM.forEach(c => form.appendChild(c))
        this.target.insertAdjacentElement('afterEnd', form)
        this.target.remove()
        this.hidden_fields.forEach(f => form.insertAdjacentHTML('beforeend', f))
        this.watch_fields.forEach(c => {
            const parent = c.node.parentElement
            c.node.remove()
            const input = document.createElement(c.type)
            input.value = c.node.innerText
            input.name = c.name
            input.id = c.id
            input.classList = c.node.classList
            input.name = c.name
            parent.appendChild(input)
            if(!visibilitySet) (visibilitySet = true) && input.focus()
        })
        this.editorState = EditorState.ACTIVE
    }

    bindEdit(){
        const editBtn = this.target.querySelector('#edit-btn')
        editBtn.addEventListener('click', (e) => {
            if(this.editorState === EditorState.INACTIVE){
                editBtn.children[0].classList = 'bi-check2 accent-color'
                this.edit()
                e.preventDefault()
            }
        })
    }
}

document.querySelectorAll('#comment[data-editable]').forEach(t => {
    const ed = new NewEditor(t, [{
        node: t.querySelector('p'),
        name: 'content',
        type: 'input',
        id: 'comment-content'
    }], [
        `<input type="hidden" value='${podcastid}' name='podcastid' />`,
        `<input type="hidden" value='${episodeid}' name='episodeid' />`,
        `<input type="hidden" value='${t.querySelector("div span").getAttribute('data-timestamp')}' name='timestamp' />`
    ],
    '/api/update/comment',
    'POST')
})