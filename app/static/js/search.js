const containers = []

class FilteredContainer{
    constructor(root){
        this.root = root
        this.elements = Array.from(root.querySelectorAll('*[data-filters]')).map((e, index) => ({elem: e, index}))
        console.log(this.elements)
    }

    update(value){
        this.elements.sort((a, b) => a.index - b.index).forEach(e => {
            if(Array.from(this.root.children).includes(e.elem)) this.root.removeChild(e.elem)
            const isShown = value === '' || e.elem.getAttribute('data-filters').split(' ').map(f => f.includes(value)).includes(true)
            if(isShown) this.root.appendChild(e.elem)
        })
    }
}

const updateContainers = (val) => {
    containers.forEach(c => c.update(val.toLowerCase()))
}

document.querySelectorAll('*[data-filtering]').forEach(elem => containers.push(new FilteredContainer(elem)))

if(containers.length > 0){
    const searchField = document.querySelector('input[name="search-field"]')

    searchField.addEventListener('change', () => updateContainers(searchField.value))
    searchField.addEventListener('input', () => updateContainers(searchField.value))
}