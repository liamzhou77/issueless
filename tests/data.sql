INSERT INTO
  users (sub, email, username, first_name, last_name)
VALUES
  (
    'test_sub_1',
    'test1@gmail.com',
    'test_username_1',
    'David',
    'Johnson'
  ),
  (
    'test_sub_2',
    'test2@gmail.com',
    'test_username_2',
    'Wade',
    'Tom'
  ),
  (
    'test_sub_3',
    'test3@gmail.com',
    'test_username_3',
    'Ryan',
    'Cooper'
  );

INSERT INTO
  projects (title, description)
VALUES
  ('test_title_1', 'test_description_1'),
  ('test_title_2', 'test_description_2'),
  ('test_title_3', 'test_description_3');

INSERT INTO
  user_projects (user_id, project_id, role_id, timestamp)
VALUES
  -- User 1 is admin in project 1, reviewer in project 2, developer in project 3
  (1, 1, 1, 1593551080.585401),
  (1, 2, 2, 1593551080.585401),
  (1, 3, 3, 1593551080.585401),
  -- User 2 is reviewer in project 1, admin in project 2
  (2, 1, 2, 1593551080.585401),
  (2, 2, 1, 1593551080.585401),
  -- User 3 is admin in project 3
  (3, 3, 1, 1593551080.585401);

INSERT INTO
  notifications (
    name,
    target_id,
    user_id,
    timestamp,
    payload_json,
    is_read
  )
VALUES
  -- User 3 received an invitation to project 2
  (
    'invitation',
    2,
    3,
    1593406929.172222,
    '{"invitorName": "Wade Tom", "projectTitle": "test_title_2", "roleName": "Developer"}',
    FALSE
  ),
  -- User 2 received an invitation to project 3
  (
    'invitation',
    3,
    2,
    1593406942.200693,
    '{"invitorName": "Ryan Cooper", "projectTitle": "test_title_3", "roleName": "Developer"}',
    FALSE
  );