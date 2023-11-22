function previewFile(fileInput, img_element) {
  img_element = document.querySelector(img_element)
  for (const file of fileInput.files) {
    const reader = new FileReader();
    reader.onload = function (e) { img_element.src = e.target.result };
    reader.readAsDataURL(file);
  }
}