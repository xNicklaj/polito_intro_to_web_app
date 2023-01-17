// This small piece of code loads default podcast image when an error occurs
// in the src tag of an image
document.querySelectorAll('img').forEach(i => {
    i.addEventListener('error', (e) => e.target.src = '/static/images/pod_default.jpg')
})

// This function allows to preview the image that will be sent when creating a new podcast
function previewFile(target, src){
    var reader  = new FileReader();
  
    reader.onloadend = function () {
      target.src = reader.result;
    }
  
    if (src) {
      reader.readAsDataURL(src);
    } else {
      target.src = "";
    }
}
const newpod_thumbnail_input = document.querySelector('#newpod_thumbnail_input');
const newpod_thumbnail = document.querySelector('#newpod_thumbnail');

if(newpod_thumbnail != null && newpod_thumbnail_input != null){
    newpod_thumbnail_input.addEventListener('change', () => previewFile(newpod_thumbnail, newpod_thumbnail_input.files[0]))
}