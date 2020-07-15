document.querySelectorAll('.file-delete-form').forEach((form) => {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    postFetch(form.action, (data) => {
      if (data.success) {
        form.closest('.list-group-item').remove();
      }
    });
  });
});
