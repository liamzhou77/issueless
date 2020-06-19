const projectForm = document.getElementById('edit-project-form');
const title = projectForm[0];
const description = projectForm[1];
const editBtn = projectForm[2];
title.setAttribute('data-original', title.value);
description.setAttribute('data-original', description.value);

function disableSubmitBtn() {
  if (
    title.value === 0 ||
    description.value === 0 ||
    (title.value === title.dataset.original &&
      description.value === description.dataset.original)
  ) {
    editBtn.disabled = true;
  } else {
    editBtn.disabled = false;
  }
}

function editProject(e) {
  e.preventDefault();

  const titleVal = title.value;
  const descriptionVal = description.value;
  postFetch(
    this.action,
    () => {
      addAlert('Edit Successfully.', 'success');

      editBtn.disabled = true;
      title.setAttribute('data-original', titleVal);
      description.setAttribute('data-original', descriptionVal);
    },
    { title: titleVal, description: descriptionVal }
  );
}

projectForm.addEventListener('input', disableSubmitBtn);
projectForm.addEventListener('submit', editProject);
