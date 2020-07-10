$('#project-edit-modal').on('show.bs.modal', function (e) {
  const titleInput = this[1];
  const descriptionInput = this[2];
  const submitBtn = this[3];

  const caller = e.relatedTarget;
  const { action, originalTitle, originalDescription } = caller.dataset;

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
        if (data.success) {
          window.location.reload(true);
        } else {
          $(this).modal('hide');
          addAlert(data.error, 'danger');
        }
      },
      { title, description }
    );
  }

  this.oninput = disableSubmitBtn;
  this.onsubmit = submit;
});
