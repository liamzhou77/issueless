const autocompleteList = document.querySelector('.autocomplete-list');
const autocompleteListContainer = autocompleteList.parentElement.parentElement;
const autocompleteSelected = document.querySelector('.autocomplete-selected');

const inviteForm = document.getElementById('user-invite-modal');
const inviteInput = inviteForm[1];
const inviteBtn = inviteForm[4];

function clearInviteModal() {
  autocompleteListContainer.hidden = false;
  inviteInput.value = '';
  inviteBtn.disabled = true;
  autocompleteSelected.hidden = true;
}

function inviteAutocomplete() {
  function createMediaElement(innerHTML) {
    const mediaDiv = document.createElement('div');
    mediaDiv.classList.add('media', 'media-member', 'mb-0');
    mediaDiv.innerHTML = innerHTML;
    return mediaDiv;
  }

  function createAutocompleteItem(className, mediaInnerHTML) {
    const item = document.createElement('a');
    item.className = className;
    item.appendChild(createMediaElement(mediaInnerHTML));
    return item;
  }

  const searchTerm = inviteInput.value;
  let currentFocus = -1;

  function itemClick(inputVal, mediaInnerHTML) {
    autocompleteListContainer.hidden = true;
    autocompleteSelected.innerHTML = '';
    inviteBtn.disabled = false;
    inviteInput.value = inputVal;
    autocompleteSelected.hidden = false;
    autocompleteSelected.appendChild(createMediaElement(mediaInnerHTML));
    autocompleteSelected
      .querySelector('a')
      .addEventListener('click', clearInviteModal);
  }

  function removeActive(items) {
    items.forEach((item) => {
      item.classList.remove('autocomplete-active');
    });
  }

  function addActive(items) {
    removeActive(items);
    items[currentFocus].classList.add('autocomplete-active');
  }

  function nextValid(items, direction) {
    if (direction === 'up') {
      currentFocus -= 1;
    } else if (direction === 'down') {
      currentFocus += 1;
    }

    if (currentFocus >= items.length) {
      currentFocus = 0;
    } else if (currentFocus < 0) {
      currentFocus = items.length - 1;
    }

    if (items[currentFocus].classList.contains('disabled')) {
      nextValid(items, direction);
    }
  }

  autocompleteList.innerHTML = '';

  if (/^[^\s@]+@[^\s@]+$/.test(searchTerm)) {
    const item = createAutocompleteItem(
      'list-group-item border-0 p-2 list-group-item-action',
      `
        <i class="material-icons-outlined" alt="Email">email</i>
        <div class="media-body text-small">
          <strong class="mb-0 d-block text-dark">${searchTerm}</strong>
          <span>Invite to ${inviteInput.dataset.projectTitle}</span>
        </div>
      `
    );

    item.addEventListener('click', function () {
      itemClick(
        searchTerm,
        `
          <i class="material-icons-outlined">email</i>
          <div class="media-body text-small">
            <strong class="mb-0 d-block">${inviteInput.value}</strong>
          </div>
          <a href="#" class="material-icons ml-auto">close</a>
        `
      );
    });

    autocompleteList.appendChild(item);
  } else {
    getFetch(`${inviteForm.action}?search=${searchTerm}`, (data) => {
      autocompleteList.hidden = false;
      if (data.success) {
        const { users } = data;

        if (users.length > 0) {
          users.forEach((user) => {
            const { fullname, username, avatar, joined } = user;

            let className;
            let mediaInnerHTML = `
              <img src="${avatar}" alt="${fullname}" />
              <div class="media-body text-small">
                <strong class="mb-0 d-block text-dark">${fullname}</strong>
                <span>${username}</span>
              </div>
            `;
            if (joined) {
              className = 'list-group-item border-0 p-2 bg-gray disabled';
              mediaInnerHTML += '<span class="ml-auto mr-4">joined</span>';
            } else {
              className = 'list-group-item border-0 p-2 list-group-item-action';
            }
            const item = createAutocompleteItem(className, mediaInnerHTML);

            if (!joined) {
              item.addEventListener('click', function () {
                itemClick(
                  username,
                  `
                    <img src="${avatar}" alt="${fullname}" />
                    <div class="media-body text-small">
                      <strong class="mb-0 d-block">${fullname}</strong>
                      <span>${username}</span>
                    </div>
                    <a href="#" class="material-icons ml-auto">close</a>
                  `
                );
              });
            }

            autocompleteList.appendChild(item);
          });
        } else {
          const item = document.createElement('li');
          item.className =
            'list-group-item text-small text-dark border-0 font-weight-bold text-truncate';
          item.innerHTML = `Could not find an Issueless account matching <strong>${searchTerm}</strong>`;
          autocompleteList.appendChild(item);
        }
      } else {
        $(inviteForm).modal('hide');
        addAlert(data.error, 'danger');
      }
    });
  }

  inviteInput.addEventListener('keydown', function (e) {
    if (autocompleteList.querySelector('.list-group-item-action')) {
      const items = autocompleteList.querySelectorAll('a');
      if (e.keyCode === 40) {
        nextValid(items, 'down');
        addActive(items);
      } else if (e.keyCode === 38) {
        nextValid(items, 'up');
        addActive(items);
      } else if (e.keyCode === 13) {
        e.preventDefault();
        if (currentFocus > -1) {
          items[currentFocus].click();
        }
      }
    }
  });

  document.addEventListener('click', function (e) {
    if (e.target !== autocompleteList && e.target !== inviteInput) {
      autocompleteList.hidden = true;
    }
  });
}

function sendInvitation(e) {
  e.preventDefault();

  const target = inviteInput.value;
  const role = this.querySelector('.form-check-input:checked').value;

  postFetch(
    this.action,
    (data) => {
      $(inviteForm).modal('hide');
      if (data.success) {
        clearInviteModal();
        inviteForm[2].checked = true;
        inviteForm[3].checked = false;
        addAlert('Invitation sent', 'success');
      } else {
        addAlert(data.error, 'danger');
      }
    },
    { target, role }
  );
}

let inviteTypingTimer;
inviteInput.addEventListener('input', function () {
  clearTimeout(inviteTypingTimer);
  if (this.value) {
    inviteTypingTimer = setTimeout(inviteAutocomplete, 250);
  }
});

inviteInput.addEventListener('click', function () {
  if (this.value) {
    autocompleteList.hidden = false;
  }
});

inviteForm.addEventListener('submit', sendInvitation);
