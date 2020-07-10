$('#issue-edit-modal').on('show.bs.modal', function (e) {
  const titleInput = this[1];
  const descriptionInput = this[2];
  const submitBtn = this.querySelector('[type="submit"]');
  const secondSection = document.getElementById('issue-edit-second-section');

  const caller = e.relatedTarget;
  const { action, originalTitle, originalDescription } = caller.dataset;

  titleInput.value = originalTitle;
  descriptionInput.value = originalDescription;
  submitBtn.disabled = true;

  if (caller.classList.contains('issue-open-edit-link')) {
    secondSection.hidden = true;

    this.oninput = function () {
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
    };

    this.onsubmit = function (event) {
      event.preventDefault();

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
    };
  } else {
    secondSection.hidden = false;

    const selectPriority = this[3];
    const filterInput = this.querySelector('.filter-list-input');
    const { originalPriority, originalAssigneeId } = caller.dataset;

    selectPriority.value = originalPriority;
    filterInput.value = '';
    filterInput.dispatchEvent(new Event('keyup'));
    const checkedRadio = this.querySelector('.custom-control-input:checked');
    if (checkedRadio) {
      checkedRadio.checked = false;
    }
    this.querySelector(
      `.custom-control-input[value="${originalAssigneeId}"]`
    ).checked = true;

    this.oninput = function () {
      const title = titleInput.value;
      const description = descriptionInput.value;
      const checkedMember = this.querySelector('.custom-control-input:checked');
      if (
        title.length === 0 ||
        description.length === 0 ||
        selectPriority.selectedIndex === 0 ||
        !checkedMember ||
        (title === originalTitle &&
          description === originalDescription &&
          selectPriority.value === originalPriority &&
          checkedMember.value === originalAssigneeId)
      ) {
        submitBtn.disabled = true;
      } else {
        submitBtn.disabled = false;
      }
    };

    this.onsubmit = function (event) {
      event.preventDefault();

      const title = titleInput.value;
      const description = descriptionInput.value;
      const priority =
        selectPriority.options[selectPriority.selectedIndex].value;
      const selectedMember = this.querySelector(
        '.custom-control-input:checked'
      );
      const assigneeId = selectedMember.value;

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
        { title, description, priority, assignee_id: assigneeId }
      );
    };
  }
});
