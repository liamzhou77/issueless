notificationDropdown = document.getElementById('notification-dropdown');

function generate_notifications() {
  fetch('/notifications')
    .then((rsp) => rsp.json())
    .then((notifications) => {
      let output = '';

      notifications.forEach(function (n) {
        const { notificationId, name, targetId, data, timestamp } = n;

        output += '<span class="dropdown-item">';

        if (name === 'invitation') {
          const { invitorName, projectTitle, roleName } = data;
          output += `
            <strong>${invitorName}</strong> invited you to join <strong>${projectTitle}</strong> as a <strong>${roleName}</strong>.
            
            <form action="/notifications/${notificationId}/delete?next=${window.location.pathname}" method="post">
              <button type="submit">Refuse</button>
            </form>
            <form action="/projects/${targetId}/add-member?next=${window.location.pathname}" method="post">
              <button type="submit">Accept</button>
            </form>
          `;
        } else if (name == 'project deleted') {
          const projectTitle = data.projectTitle;
          output += `<strong>${projectTitle}</strong> has been deleted.</strong>`;
        }
        output += '<br>' + moment(timestamp).fromNow();
        output += '</span>';
      });
      notificationDropdown.innerHTML = output;
    });
}

setInterval(generate_notifications(), 10000);
generate_notifications();
