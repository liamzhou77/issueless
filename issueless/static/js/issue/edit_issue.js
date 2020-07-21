function disabledEditBtn() {
  const titleInput = this[1];
  const descriptionInput = this[2];
  const selectPriority = this[3];
  const submitBtn = this.querySelector('[type="submit"]');

  const {
    originalTitle,
    originalDescription,
    originalPriority,
    originalAssigneeId,
  } = this.dataset;

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
}

function editIssue(e) {
  e.preventDefault();

  const titleInput = this[1];
  const descriptionInput = this[2];
  const selectPriority = this[3];
  const submitBtn = this.querySelector('[type="submit"]');

  const title = titleInput.value;
  const description = descriptionInput.value;
  const priority = selectPriority.options[selectPriority.selectedIndex].value;
  const selectedMember = this.querySelector('.custom-control-input:checked');
  const assigneeId = selectedMember.value;

  postFetch(
    this.action,
    (data) => {
      $(this).modal('hide');
      if (data.success) {
        document.getElementById('issue-title').textContent = title;
        document.getElementById('issue-description').textContent = description;
        if (priority === 'High') {
          document.getElementById('issue-priority').innerHTML =
            'High &#x1F525;';
        } else {
          document.getElementById('issue-priority').innerHTML = priority;
        }
        const avatar = document.getElementById('issue-assignee');
        const { src, fullname } = selectedMember.dataset;

        avatar.src = src;
        avatar.alt = fullname;
        avatar.setAttribute('title', fullname);
        avatar.setAttribute('data-original-title', fullname);
        $(avatar).tooltip('update');

        this.setAttribute('data-original-title', title);
        this.setAttribute('data-original-description', description);
        this.setAttribute('data-original-priority', priority);
        this.setAttribute('data-original-assignee-id', assigneeId);
        submitBtn.disabled = true;
      } else {
        addAlert(data.error, 'danger');
      }
    },
    { title, description, priority, assignee_id: assigneeId }
  );
}

document
  .getElementById('issue-edit-modal')
  .addEventListener('input', disabledEditBtn);
document
  .getElementById('issue-edit-modal')
  .addEventListener('submit', editIssue);
