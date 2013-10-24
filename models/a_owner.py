"""Database of a user's to-do list."""

db.define_table('a_owner',
    Field('owner_email', 'string'),
    Field('my_items', 'reference task'),
    Field('shared_items', 'reference task'),
    )

db.a_owner.owner_email.readable = False
db.a_owner.owner_email.writable = False