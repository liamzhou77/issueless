const invitationForm = document.getElementById('invitation-form');
const searchInput = invitationForm[0];

function clearModal() {
  document.querySelector('.autocomplete-choice').remove();
  searchInput.hidden = false;
  searchInput.value = '';
  invitationForm[2].disabled = true;
}

function closeList(element) {
  const list = document.querySelector('.autocomplete-list');
  if (list && element !== list && element !== searchInput) {
    list.remove();
  }
}

function search() {
  const val = searchInput.value;
  let currentFocus = -1;

  function removeActive(suggestions) {
    // a function to remove the "active" class from all autocomplete items:
    suggestions.forEach((suggestion) => {
      suggestion.classList.remove('autocomplete-active');
    });
  }

  function addActive(suggestions) {
    // a function to classify an item as "active":
    if (suggestions) {
      // start by removing the "active" class on all items:
      removeActive(suggestions);
      // add class "autocomplete-active":
      suggestions[currentFocus].classList.add('autocomplete-active');
    }
  }

  function nextValidSuggestion(suggestions, direction) {
    if (direction === 'up') {
      currentFocus -= 1;
    } else if (direction === 'down') {
      currentFocus += 1;
    }

    if (currentFocus >= suggestions.length) {
      currentFocus = 0;
    } else if (currentFocus < 0) {
      currentFocus = suggestions.length - 1;
    }

    if (
      suggestions[currentFocus].className === 'autocomplete-invalid-suggestion'
    ) {
      nextValidSuggestion(suggestions, direction);
    }
  }

  const list = document.createElement('div');
  list.className = 'autocomplete-list';

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const fullnameRegex = /^[a-zA-Z]{1,50} [a-zA-Z]{1,50}$/;
  const usernameRegex = /^[a-zA-Z0-9_.+-]{1,15}\s?$/;
  const firstNameRegex = /^[a-zA-Z]{16,50}\s?$/;
  if (
    usernameRegex.test(val) ||
    firstNameRegex.test(val) ||
    fullnameRegex.test(val) ||
    emailRegex.test(val)
  ) {
    fetch(`${invitationForm.action}?search=${val}`, { redirect: 'error' })
      .then((resp) => resp.json())
      .then((data) => {
        if (data.success) {
          const { users } = data;

          if (users.length > 0) {
            users.forEach((user) => {
              const { fullname, username, avatar, joined } = user;

              const suggestion = document.createElement('div');
              suggestion.innerHTML += `<img src="${avatar}" class="avatar" alt="Avatar">${fullname} ${username}`;
              if (joined) {
                suggestion.readOnly = true;
                suggestion.innerHTML += ' joined';
                suggestion.className = 'autocomplete-invalid-suggestion';
              } else {
                suggestion.className = 'autocomplete-valid-suggestion';
                suggestion.addEventListener('click', function () {
                  const inviteBtn = invitationForm[2];
                  searchInput.value = username;
                  searchInput.hidden = true;
                  inviteBtn.disabled = false;

                  closeList();

                  const choice = document.createElement('div');
                  choice.className = 'autocomplete-choice';
                  choice.innerHTML = `
                    <img src="${avatar}" class="avatar" alt="Avatar"> ${fullname} ${username}
                    <button>delete</button>
                  `;
                  choice.lastElementChild.addEventListener('click', clearModal);
                  searchInput.insertAdjacentElement('afterend', choice);
                });
              }
              list.appendChild(suggestion);
            });
          } else {
            const suggestion = document.createElement('div');
            suggestion.textContent = `Could not find an account matching ${val}`;
            list.appendChild(suggestion);
          }
          searchInput.insertAdjacentElement('afterend', list);
        }
      })
      .catch((error) => {
        if (error.message === 'Failed to fetch') {
          window.location.href = '/dashboard';
        }
      });

    searchInput.addEventListener('keydown', function (e) {
      if (document.querySelector('.autocomplete-valid-suggestion')) {
        const suggestions = list.querySelectorAll('div');
        if (e.keyCode === 40) {
          nextValidSuggestion(suggestions, 'down');
          addActive(suggestions);
        } else if (e.keyCode === 9) {
          nextValidSuggestion(suggestions, 'down');
          addActive(suggestions);
        } else if (e.keyCode === 38) {
          nextValidSuggestion(suggestions, 'up');
          addActive(suggestions);
        } else if (e.keyCode === 13) {
          e.preventDefault();
          if (currentFocus > -1) {
            suggestions[currentFocus].click();
          }
        }
      }
    });

    document.addEventListener('click', function (e) {
      closeList(e.target);
    });
  } else {
    const suggestion = document.createElement('div');
    suggestion.textContent = `Could not find an account matching ${val}`;
    list.appendChild(suggestion);
    searchInput.insertAdjacentElement('afterend', list);
  }
}

function sendInvitation(e) {
  e.preventDefault();

  const username = searchInput.value;
  const role = this[2].value;
  postFetch(
    this.action,
    () => {
      addAlert('Invitation sent', 'success');
      $('#invitationModal').modal('hide');
      clearModal();
    },
    { username, role }
  );
}

let typingTimer;
searchInput.addEventListener('input', function () {
  closeList();
  clearTimeout(typingTimer);
  typingTimer = setTimeout(search, 250);
});
searchInput.addEventListener('click', function () {
  closeList();
  search();
});

invitationForm.addEventListener('submit', sendInvitation);
