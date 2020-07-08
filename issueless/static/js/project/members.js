document.querySelectorAll('.member-remove-btn').forEach((btn) => {
  const { action, userId } = btn.dataset;
  btn.addEventListener('click', function () {
    postFetch(
      action,
      (data) => {
        if (data.success) {
          btn.parentElement.parentElement.remove();

          const avatars = document.querySelectorAll(
            `.avatars li[data-user-id='${userId}']`
          );
          if (avatars.length > 0) {
            avatars.forEach((avatar) => {
              avatar.remove();
            });
          }

          const memberCount = document.getElementById('member-count');
          if (memberCount) {
            const newCount = Number(memberCount.textContent.substring(1)) - 1;
            if (newCount === 0) {
              memberCount.parentElement.parentElement.remove();
            } else {
              memberCount.textContent = `+${newCount}`;
            }
          }
        } else {
          addAlert(data.error, 'danger');
        }
      },
      { user_id: userId }
    );
  });
});

document.querySelectorAll('.member-change-role-btn').forEach((btn) => {
  const { action, userId } = btn.dataset;
  btn.addEventListener('click', function () {
    postFetch(
      action,
      (data) => {
        if (data.success) {
          const roleSpan = btn.previousElementSibling.querySelector(
            '.text-body'
          );
          const icon = btn.firstElementChild;

          const preRole = roleSpan.textContent;
          let newTooltipText;
          if (preRole === 'Reviewer') {
            roleSpan.textContent = 'Developer';
            newTooltipText = 'Promote';
            icon.textContent = 'arrow_circle_up';
          } else {
            roleSpan.textContent = 'Reviewer';
            newTooltipText = 'Demote';
            icon.textContent = 'arrow_circle_down';
          }
          btn.setAttribute('title', newTooltipText);
          btn.setAttribute('data-original-title', newTooltipText);
          $(btn).tooltip('update');
          $(btn).tooltip('hide');
        } else {
          addAlert(data.error, 'danger');
        }
      },
      { user_id: userId }
    );
  });
});
