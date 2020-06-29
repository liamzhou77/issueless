$('#project-edit-modal').on('show.bs.modal', function (e) {
  const titleInput = this[1];
  const descriptionInput = this[2];
  const submitBtn = this[3];

  const caller = e.relatedTarget;
  const {
    action,
    projectCardId,
    originalTitle,
    originalDescription,
  } = caller.dataset;

  titleInput.value = originalTitle;
  descriptionInput.value = originalDescription;
  submitBtn.disabled = true;

  function disableSubmitBtn() {
    const title = titleInput.value;
    const description = descriptionInput.value;
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

  function submit(error) {
    error.preventDefault();

    const title = titleInput.value;
    const description = descriptionInput.value;
    postFetch(
      action,
      (data) => {
        $(this).modal('hide');
        if (data.success) {
          document.getElementById(
            `project-title-${projectCardId}`
          ).textContent = title;
          caller.setAttribute('data-original-title', title);
          caller.setAttribute('data-original-description', description);
        } else {
          addAlert(data.error, 'danger');
        }
      },
      { title, description }
    );
  }

  this.oninput = disableSubmitBtn;
  this.onsubmit = submit;
});
