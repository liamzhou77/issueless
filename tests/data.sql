INSERT INTO
  users (sub, email, first_name, last_name)
VALUES
  (
    'test_sub_1',
    'test_email_1',
    'test_first_name_1',
    'test_last_name_1'
  ),
  (
    'test_sub_2',
    'test_email_2',
    'test_first_name_2',
    'test_last_name_2'
  ),
  (
    'test_sub_3',
    'test_email_3',
    'test_first_name_3',
    'test_last_name_3'
  );

INSERT INTO
  projects (title, description)
VALUES
  ('test_title_1', 'test_description_1'),
  ('test_title_2', 'test_description_2');

INSERT INTO
  user_project
VALUES
  (1, 1),
  (1, 2);