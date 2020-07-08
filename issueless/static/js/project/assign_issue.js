$('#issue-assign-modal').on('show.bs.modal', function (e) {
  const selectElement = this[1];
  const filterInput = this.querySelector('.filter-list-input');
  const submitBtn = this.querySelector('[type="submit"]');

  selectElement.selectedIndex = 0;
  filterInput.value = '';
  filterInput.dispatchEvent(new Event('keyup'));
  const checkedRadio = this.querySelector('.custom-control-input:checked');
  if (checkedRadio) {
    checkedRadio.checked = false;
  }
  submitBtn.disabled = true;

  this.addEventListener('submit', function (event) {
    event.preventDefault();

    const priority = selectElement.options[selectElement.selectedIndex].value;
    const assigneeId = this.querySelector('.custom-control-input:checked')
      .value;

    const caller = e.relatedTarget;
    const { action, parentId } = caller.dataset;
    postFetch(
      action,
      (data) => {
        $(this).modal('hide');
        if (data.success) {
          document.getElementById(parentId).remove();
        } else {
          addAlert(data.error, 'danger');
        }
      },
      { priority, assignee_id: assigneeId }
    );
  });
});

document
  .getElementById('issue-assign-modal')
  .addEventListener('input', function () {
    const selectElement = this[1];
    const submitBtn = this.querySelector('[type="submit"]');
    if (
      selectElement.selectedIndex === 0 ||
      !this.querySelector('.custom-control-input:checked')
    ) {
      submitBtn.disabled = true;
    } else {
      submitBtn.disabled = false;
    }
  });
