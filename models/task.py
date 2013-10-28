"""Database of to do item tasks."""

"""Get's the logged in user's first name."""
def get_name():
    if auth.user:
        return auth.user.first_name
    else:
        return 'None'

"""Get the logged in user's email."""
def get_email():
    if auth.user:
        return auth.user.email
    else:
        return 'None'

db.define_table('task',
    Field('title', 'string'),
    Field('description', 'text'),
    Field('author', 'reference a_owner'),
    Field('shared_email', 'string', default=None),
    Field('shared_task', 'boolean', default=False),
    Field('done', 'boolean', default=False),
    )

db.task.done.readable = False
db.task.done.writable = False
db.task.author.readable = False
db.task.author.writable = False
db.task.id.readable = False
db.task.shared_task.readable = False
db.task.shared_task.label = 'Assign task to someone?'
db.task.shared_email.readable = False
db.task.shared_email.writable = False
db.task.shared_email.label = 'Email task to'
db.task.shared_email.requires = [IS_IN_DB(db, db.auth_user.email, error_message='Email not registered')]
