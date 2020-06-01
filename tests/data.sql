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
  user_project
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 3),
  (2, 1, 2);