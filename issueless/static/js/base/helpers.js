function addAlert(message, style) {
  const alert = document.createElement('div');
  alert.innerHTML = ` 
    <div class="alert alert-${style} fade show" role="alert">
      ${message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`;
  document.querySelector('nav').insertAdjacentElement('afterend', alert);

  setTimeout(function () {
    alert.remove();
  }, 3000);
}

function postFetch(url, successFunc, body) {
  function then(resp) {
    const contentType = resp.headers.get('content-type');
    if (contentType && contentType.indexOf('application/json') !== -1) {
      return resp.json().then((data) => {
        if (data.success) {
          successFunc();
        } else {
          addAlert(data.error, 'danger');
        }
      });
    }
    return resp.text().then((html) => {
      const temp = document.createElement('html');
      temp.innerHTML = html;
      const error = temp.querySelector('p').textContent;
      addAlert(error, 'danger');
    });
  }

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
      .then((resp) => then(resp))
      .catch((error) => {
        if (error.message === 'Failed to fetch') {
          window.location.reload(true);
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
      .then((resp) => then(resp))
      .catch((error) => {
        if (error.message === 'Failed to fetch') {
          window.location.reload(true);
        }
      });
  }
}
