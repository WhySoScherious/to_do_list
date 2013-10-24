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
    Field('author', 'string', default=get_name()),
    Field('author_email', 'string', default=get_email()),
    Field('done', 'boolean', default=None)
    )

db.task.done.readable = False
db.task.done.writable = False
db.task.author_email.readable = False
db.task.author_email.writable = False
db.task.id.readable = False
db.task.author.writable = False