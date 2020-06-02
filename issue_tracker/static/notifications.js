notificationDropdown = document.getElementById('notification-dropdown');

function generate_notifications() {
  fetch('/notifications')
    .then((rsp) => rsp.json())
    .then((notifications) => {
      let output = '';
      notifications.forEach(function (n) {
        const {
          notification_id,
          name,
          target_id,
          data: { invitor_name, project_title, role_name },
          timestamp,
        } = n;

        if (name === 'invitation') {
          output += `
              <span class="dropdown-item" href="">
                <strong>${invitor_name}</strong> invited you to join <strong>${project_title}</strong> as a <strong>${role_name}</strong>.
                
                <form action="/notifications/${notification_id}/delete?next=${window.location.pathname}" method="post">
                  <button type="submit"">Refuse</button>
                </form>
                <button>Accept</button>
              </span>
          `;
        }
      });
      notificationDropdown.innerHTML = output;
    });
}

setInterval(generate_notifications(), 10000);
generate_notifications();
