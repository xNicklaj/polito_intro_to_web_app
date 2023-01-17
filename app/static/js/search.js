/*
 * The filtering I've implemented is very simple and intuitive. 
 * It's a keyword based search, that uses the data-filters string present in some components defined in macro.html
 * to remove or insert these components from their relative parent element.
 * 
 * The search takes into consideration only elements whose parent has the data-filtering attribute and that contain some filters,
 * creating this type of hierarchy:
 * <parent data-filtering>
 *   <child>This child is unfiltered</child>
 *   <child data-filters="filter1 filter2 filter3 ...">This child is filtered</child>
 *   <child data-filters="filter1 filter2 filter3 ...">This child is filtered</child>
 *   ...
 * </parent>
 */

const containers = []
class FilteredContainer{
    constructor(root){
        this.root = root
        this.elements = Array.from(root.querySelectorAll('*[data-filters]')).map((e, index) => ({elem: e, index}))
    }

    update(value){
        this.elements.sort((a, b) => a.index - b.index).forEach(e => {
            if(Array.from(this.root.children).includes(e.elem)) this.root.removeChild(e.elem)
            const isShown = value === '' || e.elem.getAttribute('data-filters').includes(value) > 0
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