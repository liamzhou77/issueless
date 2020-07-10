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

  const caller = e.relatedTarget;
  this.action = caller.dataset.action;
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
