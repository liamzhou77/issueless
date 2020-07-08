function addAlert(message, style) {
  const alert = document.createElement('div');
  alert.className = `alert alert-${style} alert-dismissible fade show text-center`;
  alert.setAttribute('role', 'alert');
  alert.innerHTML = ` 
    ${message}
    <button
      type="button"
      class="close"
      data-dismiss="alert"
      aria-label="Close"
    >
      <span aria-hidden="true">&times;</span>
    </button>
  `;
  document
    .querySelector('.breadcrumb-bar')
    .insertAdjacentElement('afterend', alert);

  setTimeout(() => {
    $(alert).alert('close');
  }, 5000);
}

function thenFunc(resp, okFunc) {
  if (!resp.ok && resp.status !== 422) {
    window.location.href = `/errors/${resp.status}`;
  }
  return resp.json().then((data) => okFunc(data));
}

function postFetch(url, okFunc, body) {
  if (body) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json, text/html',
        'Content-type': 'application/json',
      },
      redirect: 'error',
      body: JSON.stringify(body),
    })
      .then((resp) => thenFunc(resp, okFunc))
      .catch((error) => {
        if (error.message === 'Failed to fetch') {
          window.location.href = '/auth/login';
        }
      });
  } else {
    fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'application/json, text/html',
      },
      redirect: 'error',
    })
      .then((resp) => thenFunc(resp, okFunc))
      .catch((error) => {
        if (error.message === 'Failed to fetch') {
          window.location.href = '/auth/login';
        }
      });
  }
}

function getFetch(url, okFunc) {
  fetch(url, { redirect: 'error' })
    .then((resp) => thenFunc(resp, okFunc))
    .catch((error) => {
      if (error.message === 'Failed to fetch') {
        window.location.href = '/auth/login';
      }
    });
}

function emptyFormInput() {
  const title = this[1].value;
  const description = this[2].value;
  const submitBtn = this[3];
  if (title.length === 0 || description.length === 0) {
    submitBtn.disabled = true;
  } else {
    submitBtn.disabled = false;
  }
}
