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
    Field('author_email', 'reference a_owner'),
    Field('shared_task', 'boolean', default=None),
    Field('done', 'boolean', default=None)
    )

db.task.done.readable = False
db.task.done.writable = False
db.task.author_email.readable = False
db.task.author_email.writable = False
db.task.id.readable = False