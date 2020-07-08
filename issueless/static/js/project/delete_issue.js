document.querySelectorAll('.issue-delete-form').forEach((form) =>
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    postFetch(this.action, (data) => {
      if (data.success) {
        document.getElementById(this.dataset.parentId).remove();
      } else {
        addAlert(data.error, 'danger');
      }
    });
  })
);
