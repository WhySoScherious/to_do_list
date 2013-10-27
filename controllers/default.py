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
    if db(db.a_owner.owner_email == get_email()).select().first() is None:
        db.a_owner.insert(owner_email = get_email())

    row = db(db.a_owner.owner_email == get_email()).select().first()
    q = ((db.task.author == row.id) & (db.task.shared_task == False)) | \
        (db.task.shared_email == get_email())

    grid = SQLFORM.grid(q,
        fields=[db.task.title],
        csv=False, create=False, editable=False,
        links=[lambda row: A('Edit',_class="btn",_href=URL("default","edit_task",args=[row.id])),
               lambda row: A('Send Task',_class="btn",_href=URL("default","send_task",args=[row.id]))],
        )
    return dict(grid=grid)

@auth.requires_login()
def assigned_task():
    row = db(db.a_owner.owner_email == get_email()).select().first()
    q = ((db.task.author == row.id) & (db.task.shared_task == True))
    
    db.task.shared_email.readable=True
    db.task.shared_email.label='Sent From'
    grid = SQLFORM.grid(q,
        fields=[db.task.title, db.task.shared_email],
        csv=False, create=False, editable=False,
        links=[lambda row: A('Edit',_class="btn",_href=URL("default","edit_task",args=[row.id]))]
        )
    return dict(grid=grid)

def check_request():
    task_id = request.args(0)
    record = db(db.task.id == task_id).select().first()
    if (record is None) or (record.author != get_id()):
        session.flash = "Invalid request"
        redirect(URL('default', 'index_user'))
    return record

@auth.requires_login()
def edit_task():
    record = check_request()

    form = SQLFORM(db.task, record,
        fields=['title', 'description', 'shared_task']
        )

    if form.process().accepted:
        if form.vars.shared_task == True:
            redirect(URL('default', 'send_task', args=(form.vars.id)))
        session.flash = 'Task updated'
        redirect(URL('default', 'index_user'))

    return dict(form=form)

@auth.requires_login()
def add_task():
    """Adds a task for a particular user."""
    form = SQLFORM(db.task)

    row = db(db.a_owner.owner_email == get_email()).select().first()
    form.vars.author = row.id
    
    if form.process().accepted:
        if form.vars.shared_task == True:
            redirect(URL('default', 'send_task', args=(form.vars.id)))
        session.flash = 'Task added'
        redirect(URL('default', 'index_user'))
    
    return dict(form=form)

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
        buttons=[TAG.button('Submit',_type="submit"),TAG.button('Cancel',_type="button",_onClick = "parent.location='%s' " % URL('dont_share', args=(request.args(0))))]
        )

    if form.process().accepted:
        if form.vars.shared_email == get_email():
            session.flash = 'Cannot enter your own email'
            redirect(URL('default', 'send_task', args=(request.args(0))))
        session.flash = 'Task sent'
        redirect(URL('default', 'index_user'))

    return dict(form=form)

@auth.requires_login()
def dont_share():
    record = check_request()
    record.update_record(shared_task = False)
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
