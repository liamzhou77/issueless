let since;
const notificationList = document.querySelector(
  '.notification-content .list-group'
);

function noNotification() {
  const noUnreadNotifications = document.getElementById(
    'notification-no-unread'
  );
  const noNotifications = document.getElementById(
    'notification-no-read-and-unread'
  );

  const notificationIcon = document.getElementById('notification-icon');
  const unreadNotification = document.querySelector('.notification-unread');
  if (!unreadNotification) {
    notificationIcon.textContent = 'notifications';
  } else {
    notificationIcon.textContent = 'notifications_active';
  }

  if (notificationList.classList.contains('notification-view-unread')) {
    if (!unreadNotification) {
      noUnreadNotifications.hidden = false;
      noNotifications.hidden = true;
    } else {
      noUnreadNotifications.hidden = true;
      noNotifications.hidden = true;
    }
  } else if (
    !unreadNotification &&
    !document.querySelector('.notification-read')
  ) {
    noUnreadNotifications.hidden = true;
    noNotifications.hidden = false;
  } else {
    noUnreadNotifications.hidden = true;
    noNotifications.hidden = true;
  }
}

function generateNotifications() {
  function createMediaBody(fullname, message, timestamp) {
    const mediaBody = document.createElement('div');
    mediaBody.className = 'ml-2 media-body text-truncate';
    mediaBody.innerHTML = `
      <strong class="d-block text-truncate">${fullname}</strong>
      <span class="d-block text-truncate">
        ${message}
      </span>
      <span class="notification-timestamp">${moment(
        timestamp * 1000
      ).fromNow()}</span>
    `;
    return mediaBody;
  }

  function deleteNotification(notificationId, item) {
    postFetch(`/notifications/${notificationId}/delete`, (data2) => {
      if (data2.success) {
        item.remove();
        noNotification();
      } else {
        addAlert(data2.error, 'danger');
      }
    });
  }

  let url = '/notifications';
  if (since) {
    url = `/notifications?since=${since}`;
  }
  getFetch(url, (json) => {
    if (json.success) {
      const { notifications } = json;

      for (let i = 0; i < notifications.length; i += 1) {
        const n = notifications[i];
        const {
          notificationId,
          name,
          targetId,
          data,
          data: { fullname, avatar },
          timestamp,
          isRead,
        } = n;

        if (
          (!since && i === 0) ||
          (url.includes('since') && i === notifications.length - 1)
        ) {
          since = timestamp;
        }

        const item = document.createElement('li');

        item.className = 'list-group-item p-0';
        if (isRead) {
          item.classList.add('notification-read');
        } else {
          item.classList.add('notification-unread');
        }

        const media = document.createElement('div');
        media.className = 'media align-items-center';

        const avatarImg = document.createElement('img');
        avatarImg.src = avatar;
        avatarImg.alt = fullname;
        media.appendChild(avatarImg);

        let messageHTML;
        if (name === 'invitation') {
          messageHTML = `invited you to be a <strong>${data.roleName}</strong> in <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'join project') {
          messageHTML = `joined your project <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'delete project') {
          messageHTML = `deleted <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'quit project') {
          messageHTML = `left <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'remove user') {
          messageHTML = `removed you from <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'change role') {
          messageHTML = `changed your role in <strong>${data.projectTitle}</strong> to <strong>${data.newRole}</strong>.`;
        } else if (name === 'new issue') {
          messageHTML = `created a new issue <strong>${data.issueTitle}</strong> in <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'delete issue') {
          messageHTML = `deleted the issue <strong>${data.issueTitle}</strong> in <strong>${data.projectTitle}</strong>.`;
        } else if (name === 'assign issue') {
          messageHTML = `assigned you a new issue.`;
        } else if (name === 'remove assignee') {
          messageHTML = `assigned the issue <strong>${data.issueTitle}</strong> to another member.`;
        } else if (name === 'mark open') {
          messageHTML = `marked the closed issue <strong>${data.issueTitle}</strong> as Open.`;
        } else if (name === 'mark in progress') {
          messageHTML = `marked the ${data.preStatus} issue <strong>${data.issueTitle}</strong> as In Progress.`;
        } else if (name === 'mark resolved') {
          messageHTML = `marked the issue <strong>${data.issueTitle}</strong> as Resolved.`;
        } else if (name === 'mark closed') {
          messageHTML = `marked the issue <strong>${data.issueTitle}</strong> as Closed.`;
        } else if (name === 'new comment') {
          messageHTML = `submitted a new comment.`;
        }

        const mediaBody = createMediaBody(fullname, messageHTML, timestamp);
        media.appendChild(mediaBody);

        if (name === 'invitation') {
          const btnDiv = document.createElement('div');
          btnDiv.className = 'd-flex flex-sm-column mr-3';
          const acceptBtn = document.createElement('button');
          acceptBtn.className = 'btn btn-outline-secondary btn-sm';
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
            postFetch(`/projects/${targetId}/join`, (data2) => {
              if (data2.success) {
                successFunc();
              } else {
                $('.nav-item .dropdown-toggle').dropdown('hide');
                const { error } = data2;
                if (error === 'The project has been removed.') {
                  deleteNotification(notificationId, item);
                }
                addAlert(error, 'danger');
              }
            });
          });
          btnDiv.appendChild(acceptBtn);

          const deleteBtn = document.createElement('button');
          deleteBtn.className = 'btn btn-outline-secondary btn-sm mt-1';
          deleteBtn.textContent = 'Delete';
          deleteBtn.addEventListener('click', function () {
            deleteNotification(notificationId, item);
          });
          btnDiv.appendChild(deleteBtn);

          media.appendChild(btnDiv);
        } else if (
          name === 'assign issue' ||
          name === 'mark in progress' ||
          name === 'new comment'
        ) {
          const redirectIcon = document.createElement('i');
          redirectIcon.className =
            'material-icons mx-2 notification-redirect-icon';
          redirectIcon.textContent = 'navigate_next';
          redirectIcon.addEventListener('click', function () {
            postFetch(`/notifications/read?id=${notificationId}`, (data2) => {
              if (data2.success) {
                window.location.href = `/projects/${data.projectId}/issues/${targetId}`;
              } else {
                $('.nav-item .dropdown-toggle').dropdown('hide');
                addAlert(data2.error, 'danger');
              }
            });
          });
          media.appendChild(redirectIcon);
        }

        if (!isRead) {
          const markAsReadBtn = document.createElement('button');
          markAsReadBtn.className = 'notification-marker ml-2 btn-primary';
          markAsReadBtn.setAttribute('data-toggle', 'tooltip');
          markAsReadBtn.setAttribute('data-placement', 'top');
          markAsReadBtn.setAttribute('title', 'Mark as Read');
          media.appendChild(markAsReadBtn);

          markAsReadBtn.addEventListener('click', function () {
            $(markAsReadBtn).tooltip('hide');
            postFetch(`/notifications/read?id=${notificationId}`, (data2) => {
              if (data2.success) {
                item.classList.remove('notification-unread');
                item.classList.add('notification-read');
                markAsReadBtn.remove();
                noNotification();
              } else {
                $('.nav-item .dropdown-toggle').dropdown('hide');
                addAlert(data2.error, 'danger');
              }
            });
          });
        }

        item.appendChild(media);
        if (url.includes('since')) {
          notificationList.prepend(item);
        } else {
          notificationList.appendChild(item);
        }
      }

      noNotification();
    }
  });
}

document
  .querySelector('.nav-item .dropdown-menu')
  .addEventListener('click', function (e) {
    e.stopPropagation();
  });

document
  .querySelector('.notification-content :first-child')
  .addEventListener('click', function () {
    if (this.textContent.includes('View All')) {
      notificationList.classList.remove('notification-view-unread');
      this.innerHTML = '<u>Filter by Unread</u>';
    } else if (this.textContent.includes('Filter by Unread')) {
      notificationList.classList.add('notification-view-unread');
      this.innerHTML = '<u>View All</u>';
    }
    noNotification();
  });

document
  .querySelector('.notification-content :nth-child(2')
  .addEventListener('click', function () {
    if (since) {
      postFetch(`/notifications/read?before=${since}`, (data) => {
        if (data.success) {
          document.querySelectorAll('.notification-unread').forEach((item) => {
            item.classList.remove('notification-unread');
            item.classList.add('notification-read');
            item.querySelector('.notification-marker').remove();
            noNotification();
          });
        } else {
          addAlert(data.error, 'danger');
        }
      });
    }
  });

generateNotifications();
setInterval(generateNotifications, 20000);
