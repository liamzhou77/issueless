function disableSubmitBtn() {
  if (this[0].value.length === 0 || this[1].value.length === 0) {
    this[2].disabled = true;
  } else {
    this[2].disabled = false;
  }
}

const projectForm = document.getElementById('create-project-form');
projectForm.addEventListener('input', disableSubmitBtn);
