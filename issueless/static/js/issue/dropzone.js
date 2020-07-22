Dropzone.options.issueDropzone = {
  maxFilesize: 5,
  init() {
    this.on('error', function (file, errorMessage) {
      const errorElem = document.createElement('h6');
      errorElem.className = 'text-danger px-3 font-weight-normal text-center';
      errorElem.textContent = errorMessage;
      this.element.insertAdjacentElement('afterend', errorElem);
      setTimeout(() => {
        errorElem.remove();
      }, 5000);
      this.removeFile(file);
    });
    this.on('success', function (file, json) {
      const elem = file.previewElement;
      const { filename, size } = json;
      const { projectId, issueId } = elem.dataset;
      const downloadLink = `/projects/${projectId}/issues/${issueId}/uploads/${filename}`;
      const deleteLink = `/projects/${projectId}/issues/${issueId}/uploads/${filename}/delete`;

      const filenameElem = elem.querySelector('.dz-filename');
      filenameElem.textContent = filename;
      filenameElem.href = downloadLink;

      elem.querySelector('.dz-size').textContent = size;

      const dropdownItems = elem.querySelectorAll('.dropdown-item');
      dropdownItems[0].href = downloadLink;
      const form = dropdownItems[1].parentElement;
      form.action = deleteLink;
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        postFetch(form.action, (data) => {
          if (data.success) {
            form.closest('.list-group-item').remove();
          }
        });
      });
    });
  },
};
