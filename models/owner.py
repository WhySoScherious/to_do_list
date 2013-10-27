"""Database of a user's to-do list."""

db.define_table('a_owner',
    Field('owner_email', 'string'),
    )

db.a_owner.owner_email.readable = False
db.a_owner.owner_email.writable = False
