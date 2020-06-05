INSERT INTO
  users (sub, email, first_name, last_name)
VALUES
  (
    'test_sub_1',
    'test1@gmail.com',
    'test_first_name_1',
    'test_last_name_1'
  ),
  (
    'test_sub_2',
    'test2@gmail.com',
    'test_first_name_2',
    'test_last_name_2'
  ),
  (
    'test_sub_3',
    'test3@gmail.com',
    'test_first_name_3',
    'test_last_name_3'
  );

INSERT INTO
  projects (title, description)
VALUES
  ('test_title_1', 'test_description_1'),
  ('test_title_2', 'test_description_2'),
  ('test_title_3', 'test_description_3');

INSERT INTO
  user_project (user_id, project_id, role_id, timestamp)
VALUES
  -- User 1 is admin in project 1, reviewer in project 2, developer in project 3
  (1, 1, 1, '2020-06-05 04:00:27.219008'),
  (1, 2, 2, '2020-06-05 04:00:27.219008'),
  (1, 3, 3, '2020-06-05 04:00:27.219008'),
  -- User 2 is reviewer in project 1, admin in project 2
  (2, 1, 2, '2020-06-05 04:00:27.219008'),
  (2, 2, 1, '2020-06-05 04:00:27.219008'),
  -- User 3 is admin in project 3
  (3, 3, 1, '2020-06-05 04:00:27.219008');

INSERT INTO
  notifications (
    name,
    target_id,
    user_id,
    timestamp,
    payload_json
  )
VALUES
  -- User 3 received an invitation to project 2
  (
    'invitation',
    2,
    3,
    '2020-06-02 05:59:22.344978',
    '{"invitorName": "test_first_name_2 test_last_name_2", "projectTitle": "test_title_2", "roleName": "Developer"}'
  ),
  -- User 2 received an invitation to project 3
  (
    'invitation',
    3,
    2,
    '2020-06-02 05:59:22.344978',
    '{"invitorName": "test_first_name_3 test_last_name_3", "projectTitle": "test_title_3", "roleName": "Developer"}'
  );