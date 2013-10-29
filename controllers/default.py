# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def get_email():
    """Get the logged in user's email."""
    if auth.user:
        return auth.user.email
    else:
        return 'None'

def get_id():
    """Get the logged in user's id."""
    if auth.user:
        return auth.user.id
    else:
        return 'None'
    
def index():
    """Homepage for my task list site. Guest users will default to
       this page."""
    if auth.user:
        redirect(URL('index_user'))

    return dict()

@auth.requires_login()
def index_user():
    """Main page for logged in users with task list."""
    # Get number of pending user tasks.
    pending = db((db.task.shared_email == get_email) & (db.task.pending == True)).count()

    # Check if the logged in user is in the a_owner database.
    row = db(db.a_owner.owner_email == get_email()).select().first()
    if row is None:
        db.a_owner.insert(owner_email = get_email())

    # Show tasks created by logged user, not including sent and completed tasks.
    q = ((db.task.author == row.id) & (db.task.shared_task == False) & (db.task.done == False))

    db.task.author.readable=True
    db.task.author.label='Created by'
    db.task.author.represent = lambda id, row: id.owner_email
    grid = SQLFORM.grid(q,
        fields=[db.task.title, db.task.author],
        csv=False, create=False, editable=False,
        links=[lambda row: A('Mark Complete',_class="btn",_href=URL("default","mark_complete",args=[row.id])),
               lambda row: A('Send Task',_class="btn",_href=URL("default","send_task",args=[row.id])),
               lambda row: A('Edit',_class="btn",_href=URL("default","edit_task",args=[row.id]))]
        )
    
    shared_tasks = ((db.task.shared_email == get_email()) & (db.task.pending == False) & (db.task.done == False))
    shared_grid = SQLFORM.grid(shared_tasks,
        fields=[db.task.title, db.task.author],
        csv=False, create=False, editable=False,
        links=[lambda row: A('Mark Complete',_class="btn",_href=URL("default","mark_complete",args=[row.id])),
               lambda row: A('Edit',_class="btn",_href=URL("default","edit_task",args=[row.id]))]
        )
    return dict(grid=grid, shared_grid=shared_grid, pending=pending)

@auth.requires_login()
def sent_task():
    """Show tasks logged user assigned to others."""
    # Get number of pending user tasks.
    pending = db((db.task.shared_email == get_email) & (db.task.pending == True)).count()

    row = db(db.a_owner.owner_email == get_email()).select().first()
    q = ((db.task.author == row.id) & (db.task.shared_task == True))

    db.task.shared_email.readable=True
    db.task.shared_email.label='Sent To'
    grid = SQLFORM.grid(q,
        fields=[db.task.title, db.task.shared_email],
        csv=False, create=False, editable=False, deletable=False
        )
    return dict(grid=grid, pending=pending)

@auth.requires_login()
def completed_task():
    """List of user's completed tasks."""
    # Get number of pending user tasks.
    pending = db((db.task.shared_email == get_email) & (db.task.pending == True)).count()

    row = db(db.a_owner.owner_email == get_email()).select().first()

    # Show tasks created by logged user, not including sent and completed tasks.
    q = ((db.task.author == row.id) & (db.task.shared_task == False) & (db.task.done == True)) | \
        ((db.task.shared_email == get_email()) & (db.task.done == True))

    db.task.author.readable=True
    db.task.author.label='Sent From'
    db.task.author.represent = lambda id, row: id.owner_email
    grid = SQLFORM.grid(q,
        fields=[db.task.title, db.task.author],
        csv=False, create=False, editable=False,
        links=[lambda row: A('Mark Incomplete',_class="btn",_href=URL("default","mark_incomplete",args=[row.id]))]
        )
    return dict(grid=grid, pending=pending)

@auth.requires_login()
def pending_task():
    """List of user's tasks awaiting approval."""
    row = db(db.a_owner.owner_email == get_email()).select().first()
    q = ((db.task.shared_email == row.owner_email) & (db.task.pending == True))

    db.task.author.readable=True
    db.task.author.label='Sent From'
    db.task.author.represent = lambda id, row: id.owner_email
    grid = SQLFORM.grid(q,
        fields=[db.task.title, db.task.author],
        csv=False, create=False, editable=False, deletable=False,
        links=[lambda row: A('Accept',_class="btn",_href=URL("default","accept_task",args=[row.id])),
               lambda row: A('Reject',_class="btn",_href=URL("default","reject_task",args=[row.id]))]
        )
    return dict(grid=grid)

def check_request():
    """Check if the URL request was made by user who owns task."""
    task_id = request.args(0)
    record = db(db.task.id == task_id).select().first()
    if record is None or (get_email() != record.author.owner_email and record.shared_email != get_email()):
        session.flash = "Invalid request"
        redirect(URL('default', 'index_user'))
    return record

@auth.requires_login()
def edit_task():
    """Edits a task requested."""
    record = check_request()

    form = SQLFORM(db.task, record,
        fields=['title', 'description'],
        buttons=[TAG.button('Submit',_type="submit"),
                 TAG.button('Cancel',_type="button",_onClick = "parent.location='%s' " % URL('index_user'))]
        )

    if form.process().accepted:
        if form.vars.shared_task == True:
            redirect(URL('default', 'send_task', args=(form.vars.id)))
        session.flash = 'Task updated'
        redirect(URL('default', 'dont_share', args=(form.vars.id)))

    return dict(form=form)

@auth.requires_login()
def add_task():
    """Adds a task for a particular user."""
    form = SQLFORM(db.task,
        buttons=[TAG.button('Submit',_type="submit"),
                 TAG.button('Cancel',_type="button",_onClick = "parent.location='%s' " % URL('index_user'))]
        )

    # Assign a_owner to task being added.
    row = db(db.a_owner.owner_email == get_email()).select().first()
    form.vars.author = row.id
    
    if form.process().accepted:
        # If the user assigns task, go to send_task form.
        if form.vars.shared_task == True:
            redirect(URL('default', 'send_task', args=(form.vars.id)))
        session.flash = 'Task added'
        redirect(URL('default', 'index_user'))
    
    return dict(form=form)

def form_processing(form):
    # Do not let user assign task to themself.
    if form.vars.shared_email == get_email():
        form.errors.shared_email = "Cannot send to yourself"

@auth.requires_login()
def send_task():
    """Asks for email for user to send task to."""
    record = check_request()

    db.task.shared_email.readable = True
    db.task.shared_email.writable = True
    db.task.title.writable = False
    db.task.description.writable = False
    form = SQLFORM(db.task, record,
        fields=['title', 'description', 'shared_email'],
        buttons=[TAG.button('Submit',_type="submit"),
                 TAG.button('Cancel',_type="button",_onClick = "parent.location='%s' " % URL('dont_share', args=(request.args(0))))]
        )

    if form.process(onvalidation=form_processing).accepted:
        record.update_record(shared_task=True)
        record.update_record(pending=True)
        session.flash = 'Task sent'
        redirect(URL('default', 'index_user'))

    return dict(form=form)

@auth.requires_login()
def accept_task():
    record = check_request()
    record.update_record(pending = False)
    redirect(URL('default', 'pending_task'))

@auth.requires_login()
def reject_task():
    record = check_request()
    record.update_record(pending = False)
    record.update_record(shared_email = None)
    record.update_record(shared_task = False)
    redirect(URL('default', 'pending_task'))

@auth.requires_login()
def mark_complete():
    record = check_request()
    record.update_record(done = True)
    redirect(URL('default', 'index_user'))

@auth.requires_login()
def mark_incomplete():
    record = check_request()
    record.update_record(done = False)
    redirect(URL('default', 'completed_task'))

@auth.requires_login()
def dont_share():
    """User who cancels request to send task is sent here to set task
       as not shared."""
    record = check_request()
    if record.shared_email is None:
        record.update_record(shared_task = False)
        record.update_record(shared_email = None)
    redirect(URL('default', 'index_user'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
