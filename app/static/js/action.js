const currentURI = document.location.pathname
const isEpisode = new RegExp('pod/\\d{1,6}/\\d{1,6}').test(currentURI)
const podcastid = currentURI.slice(1).split('/')[1]
let episodeid = 0
if(isEpisode) episodeid = currentURI.slice(1).split('/')[2]

const EditorState = {
    ACTIVE: 0,
    INACTIVE: 1
}

/*
 * This Object defines a generalized editor composed of these properties:
 * - target: The target root element of the editor that will be changed into form when editor mode is enabled.
 * - watch_fields: a list of fields that need to be changed to input when the editor mode is enabled.
 * - hidden_fields: a list of fields that need to be inserted as hidden into the form when the editor mode is enabled.
 * - endpoint: the action property of the form.
 * - method: the method of the form.
 * 
 * This allows to turn virtually any container into an editor.
 */
class Editor{
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
            const input = document.createElement(c.type)
            input.value = c.node.innerText
            input.name = c.name
            input.id = c.id
            input.classList = c.node.classList + " " + c.classList
            input.name = c.name
            c.node.insertAdjacentElement('afterEnd', input)
            c.node.remove()
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

// Bind the editor for comments, episodes and podcast.

document.querySelectorAll('#comment[data-editable]').forEach(t => {
    const ed = new Editor(t, [{
        node: t.querySelector('p'),
        name: 'content',
        type: 'input',
        id: 'comment-content'
    }], [
        `<input type="hidden" value='${podcastid}' name='podcastid' />`,
        `<input type="hidden" value='${episodeid}' name='episodeid' />`,
        `<input type="hidden" value='${t.querySelector("time").getAttribute('data-timestamp')}' name='timestamp' />`
    ],
    '/api/update/comment',
    'POST')
})

const t = document.querySelector('.podcast-metadata article')
const eb = document.querySelector('#edit-btn')
if(t != null && eb != null){
    const hidden_fields = [
        `<input type="hidden" name="update_podcastid" value="${podcastid}">`,
    ]
    if(isEpisode) hidden_fields.push(`<input type="hidden" value='${episodeid}' name='update_episodeid' />`)
    const ed = new Editor(t, [{
        node: t.querySelector('.pod-meta-title'),
        name: 'update_title',
        type: 'input',
        classList: 'accent-color',
        id: ''
    },
    {
        node: t.querySelector('.pod-meta-article p'),
        name: 'update_description',
        type: 'textarea',
        classList: 'w100 secondary_color p0',
        id: ''
    }], hidden_fields,
    isEpisode ? '/api/update/episode' : '/api/update/podcast',
    'POST')
}

if(document.querySelector('#delete-btn') != null){
    document.querySelector('#delete-btn').addEventListener('click', () => {
        let targetEndpoint = `/delete/${podcastid}`
        if(isEpisode){
            targetEndpoint += `/${episodeid}`
        }
        document.location.href = targetEndpoint
    })
}