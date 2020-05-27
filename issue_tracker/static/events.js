// Changes the project form's action based on which button is clicked.
const projectForm = document.getElementById('project-form');
const titleInput = document.getElementById('project-title');
const descriptionInput = document.getElementById('project-description');

const createProjectBtn = document.getElementById('create-project-btn');
createProjectBtn.addEventListener('click', function () {
  $('#projectModal').modal('toggle');
  projectForm.action = '/projects/create';
  titleInput.value = '';
  descriptionInput.value = '';
});

const projectList = document.getElementById('project-list');
projectList.addEventListener('click', function (e) {
  if (e.target.matches('.edit-project-btn')) {
    $('#projectModal').modal('toggle');
    const btn = e.target;
    const id = btn.dataset.id;
    const title = btn.dataset.title;
    const description = btn.dataset.description;

    projectForm.action = `/projects/${id}/update`;
    titleInput.value = title;
    descriptionInput.value = description;
  }
});
