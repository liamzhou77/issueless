import logging

import boto3
from botocore.exceptions import ClientError
from flask import abort, current_app
from flask_login import current_user

from issueless.errors.errors import ValidationError
from issueless.models import User


def create_validation(title, description):
    return _title_description_validation(title, description)


def edit_validation(
    issue, title, description, project=None, priority=None, assignee_id=None
):
    if issue.status != 'Open' and issue.status != 'In Progress':
        raise ValidationError('You can only edit an open or in progress issue.')

    error = _title_description_validation(title, description)
    if error is not None:
        raise ValidationError(error)

    if issue.status == 'Open':
        if issue.title == title and issue.description == description:
            raise ValidationError('No changes have been made.')
    else:
        if priority != 'High' and priority != 'Medium' and priority != 'Low':
            raise ValidationError('Please provide a valid priority level.')

        assignee = User.query.get_or_404(assignee_id)
        if assignee not in project.users:
            raise ValidationError('The user you chose is not a member of the project.')

        if (
            issue.title == title
            and issue.description == description
            and priority == issue.priority
            and assignee == issue.assignee
        ):
            raise ValidationError('No changes have been made.')
        return assignee


def _title_description_validation(title, description):
    error = None
    if not title:
        error = "Please provide the issue's title."
    if len(title) > 80:
        error = "Issue's title can not be more than 80 character."
    if not description:
        error = "Please provide the issue's description."
    if len(description) > 200:
        error = "Issue's description can not be more than 200 characters."
    return error


def assign_validation(project, issue, priority, assignee_id):
    error = None

    if priority != 'High' and priority != 'Medium' and priority != 'Low':
        error = 'Please provide a valid priority level.'

    assignee = User.query.get_or_404(assignee_id)
    if assignee not in project.users:
        error = 'The user you chose is not a member of the project.'

    return error


def sizeof_fmt(num, suffix='b'):
    for unit in ['', 'k', 'm', 'g', 't', 'p', 'e', 'z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def comment_validation(text):
    error = None
    if not text:
        error = "Please provide the comment's text."
    if len(text) > 10000:
        error = "Comment can not be more than 10000 characters."
    return error


def admin_reviewer_add_notification(project, name, data, target_id=None):
    admin_reviewers = project.get_admin_reviewers()
    for user in admin_reviewers:
        if user != current_user:
            user.add_notification(name, data, target_id)


def upload_file_to_s3(file, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
    )
    error = None
    try:
        s3.upload_fileobj(
            file,
            current_app.config['S3_BUCKET_NAME'],
            key,
            ExtraArgs={'ContentType': file.content_type},
        )
    except Exception as e:
        logging.error(e)
        error = 'Problem occurred during file upload.'
    return error


def create_presigned_url(key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
    )
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': current_app.config['S3_BUCKET_NAME'], 'Key': key},
            ExpiresIn=100,
        )
    except ClientError as e:
        logging.error(e)
        abort(400)
    return url


def delete_file_in_s3(key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
    )
    try:
        s3.delete_object(Bucket=current_app.config['S3_BUCKET_NAME'], Key=key)
    except Exception as e:
        logging.error(e)
        abort(400)


def delete_issue_files_in_s3(prefix):
    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
    )
    resp = s3.list_objects_v2(
        Bucket=current_app.config['S3_BUCKET_NAME'], Prefix=prefix
    )
    try:
        s3.delete_objects(
            Bucket=current_app.config['S3_BUCKET_NAME'],
            Delete={'Objects': [{'Key': obj['Key']} for obj in resp['Contents']]},
        )
    except Exception as e:
        logging.error(e)
        abort(400)
