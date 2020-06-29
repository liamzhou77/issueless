const editProjectForm = document.getElementById('project-edit-modal');

function disableEditBtn() {
  const titleInput = this[1];
  const descriptionInput = this[2];
  const submitBtn = this[3];

  const title = titleInput.value;
  const description = descriptionInput.value;
  const { originalTitle, originalDescription } = this.dataset;

  if (
    title.length === 0 ||
    description.length === 0 ||
    (title === originalTitle && description === originalDescription)
  ) {
    submitBtn.disabled = true;
  } else {
    submitBtn.disabled = false;
  }
}

function submit(e) {
  e.preventDefault();

  const titleInput = this[1];
  const descriptionInput = this[2];
  const submitBtn = this[3];

  const title = titleInput.value;
  const description = descriptionInput.value;
  postFetch(
    this.action,
    (data) => {
      $(this).modal('hide');
      if (data.success) {
        submitBtn.disabled = true;

        document.querySelector('.page-header h1').textContent = title;
        document.querySelector('.page-header p').textContent = description;
        this.setAttribute('data-original-title', title);
        this.setAttribute('data-original-description', description);
      } else {
        addAlert(data.error, 'danger');
      }
    },
    { title, description }
  );
}

editProjectForm.addEventListener('input', disableEditBtn);
editProjectForm.addEventListener('submit', submit);
