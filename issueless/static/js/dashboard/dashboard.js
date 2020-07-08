if (!document.querySelector('.card-project')) {
  document.getElementById('project-list').remove();
}

document
  .getElementById('project-create-modal')
  .addEventListener('input', emptyFormInput);
