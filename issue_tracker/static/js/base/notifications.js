const dropdown = document.getElementById('notification-dropdown');

function generateNotifications() {
  dropdown.innerHTML = '';

  fetch('/notifications', { redirect: 'error' })
    .then((resp) => {
      return resp.json();
    })
    .then((json) => {
      if (json.success) {
        const { notifications } = json;
        notifications.forEach((n) => {
          const { notificationId, name, targetId, data, timestamp } = n;

          const item = document.createElement('a');
          item.className = 'dropdown-item';

          const notificationText = document.createElement('div');
          if (name === 'invitation') {
            const { invitorName, projectTitle, roleName } = data;

            notificationText.innerHTML += `<strong>${invitorName}</strong> invited you to join <strong>${projectTitle}</strong> as a <strong>${roleName}</strong>.`;
            item.appendChild(notificationText);

            const refuseBtn = document.createElement('button');
            refuseBtn.textContent = 'Refuse';
            refuseBtn.addEventListener('click', function () {
              postFetch(`/notifications/${notificationId}/delete`, () => {
                item.remove();
              });
            });
            item.appendChild(refuseBtn);

            const acceptBtn = document.createElement('button');
            acceptBtn.textContent = 'Accept';
            let successFunc;
            if (window.location.pathname === '/dashboard') {
              successFunc = () => {
                window.location.reload(true);
              };
            } else {
              successFunc = () => {
                item.remove();
              };
            }
            acceptBtn.addEventListener('click', function () {
              postFetch(`/projects/${targetId}/join`, successFunc);
            });
            item.appendChild(acceptBtn);
          } else if (name === 'project deleted') {
            const { projectTitle } = data;
            notificationText.innerHTML += `<strong>${projectTitle}</strong> was deleted.`;
          } else if (name === 'quit project') {
            const { projectTitle, userName } = data;
            notificationText.innerHTML += `<strong>${userName}</strong> left project <strong>${projectTitle}</strong>.`;
          } else if (name === 'join project') {
            const { projectTitle, userName } = data;
            notificationText.innerHTML += `<strong>${userName}</strong> joined project <strong>${projectTitle}</strong>.`;
          } else if (name === 'user removed') {
            const { projectTitle } = data;
            notificationText.innerHTML += `You are removed from project <strong>${projectTitle}</strong>.`;
          }

          if (name !== 'invitation') {
            item.appendChild(notificationText);
          }

          const time = document.createElement('div');
          time.innerHTML += `<br>${moment(timestamp).fromNow()}`;
          item.appendChild(time);

          dropdown.appendChild(item);
        });
      }
    })
    .catch((error) => {
      if (error.message === 'Failed to fetch') {
        window.location.href = '/dashboard';
      }
    });
}

generateNotifications();
setInterval(generateNotifications, 10000);
