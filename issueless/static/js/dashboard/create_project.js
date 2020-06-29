function disableCreateBtn() {
  const title = this[1].value;
  const description = this[2].value;
  const submitBtn = this[3];
  if (title.length === 0 || description.length === 0) {
    submitBtn.disabled = true;
  } else {
    submitBtn.disabled = false;
  }
}

document
  .getElementById('project-create-modal')
  .addEventListener('input', disableCreateBtn);
