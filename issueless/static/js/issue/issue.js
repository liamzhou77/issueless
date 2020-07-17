document.querySelectorAll('.comment-timestamp').forEach((elem) => {
  const { timestamp } = elem.dataset;
  elem.textContent = moment(timestamp * 1000).fromNow();
});
