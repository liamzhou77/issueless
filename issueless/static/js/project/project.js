document.querySelectorAll('.issue-list-collapse').forEach((collapse) => {
  $(collapse).on('show.bs.collapse', function () {
    document.querySelector(
      `[href="#${this.id}"]`
    ).firstElementChild.textContent = 'remove';
  });

  $(collapse).on('hide.bs.collapse', function () {
    document.querySelector(
      `[href="#${this.id}"]`
    ).firstElementChild.textContent = 'add';
  });
});

document.querySelectorAll('.issue-description-collapse').forEach((elem) => {
  $(elem).on('show.bs.collapse', function (e) {
    e.stopPropagation();
    const toggleIcon = document.querySelector(`[href="#${this.id}"]`)
      .firstElementChild;
    toggleIcon.textContent = 'expand_less';
    toggleIcon.setAttribute('title', 'Hide Description');
    toggleIcon.setAttribute('data-original-title', 'Hide Description');
    $(toggleIcon).tooltip('update');
    $(toggleIcon).tooltip('show');
  });
  $(elem).on('hide.bs.collapse', function (e) {
    e.stopPropagation();
    const toggleIcon = document.querySelector(`[href="#${this.id}"]`)
      .firstElementChild;
    toggleIcon.textContent = 'expand_more';
    toggleIcon.setAttribute('title', 'Show Description');
    toggleIcon.setAttribute('data-original-title', 'Show Description');
    $(toggleIcon).tooltip('update');
    $(toggleIcon).tooltip('show');
  });
});

document
  .getElementById('issue-add-modal')
  .addEventListener('input', emptyFormInput);
