from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from magicmirror.auth import login_required
from magicmirror.db import get_db

from random import randint

bp = Blueprint('console', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    
    networks = db.execute(
        'SELECT * FROM Network n'
        ' JOIN UserNetworkAssociation una on n.id = una.network_id'
        ' WHERE una.user_id = ?', (g.user['id'],)
    ).fetchall()
    
    una = db.execute(
        'SELECT * FROM UserNetworkAssociation'
    ).fetchall()
    return render_template('console/index.html', networks=networks)



@bp.route('/create_network', methods=('GET', 'POST'))
@login_required
def create_network():
    if (request.method == 'POST'):
        name = request.form['name']
        error = None

        if (not name):
            error = 'name is required.'

        if (error is not None):
            flash(error)
        else:
            db = get_db()
            networks = db.execute(
                'SELECT * FROM Network'
            ).fetchall()
            new_network_id = get_new_network_id(networks)

            db.execute(
                'INSERT INTO Network (id, name, owner_name, owner)'
                ' VALUES (?, ?, ?, ?)',
                (new_network_id, name, g.user['username'], g.user['id'])
            )
            network_id = db.execute(
                'SELECT last_insert_rowid()'
            ).fetchone()[0]
            db.execute(
                'INSERT INTO UserNetworkAssociation (user_id, network_id)'
                ' VALUES (?, ?)',
                (g.user['id'], network_id)
            )
            db.commit()
            return redirect(url_for('console.index'))

    return render_template('console/create_network.html')


def get_network(network_id, check_owner=True):
    network = get_db().execute(
        'SELECT *' 
        ' FROM Network n JOIN UserNetworkAssociation una ON n.owner = una.user_id'
        ' WHERE n.id = ?',
        (network_id,)
    ).fetchone()

    if (network is None):
        abort(404, f"Network id {id} doesn't exist.")

    if ((check_owner) and (network['owner'] != g.user['id'])):
        abort(403)

    return network


def get_network_members(network_id):
    network_users = get_db().execute(
        'SELECT *'
        ' FROM UserNetworkAssociation una JOIN User u on una.user_id = u.id'
        ' WHERE una.network_id = ?',
        (network_id,)
    ).fetchall()

    return network_users

def get_new_network_id(networks):
    taken_network_ids = []
    for network in networks:
        taken_network_ids.append(network['id'])
    while True:
        new_network_id = randint(0, 999999999)
        if (new_network_id not in taken_network_ids):
            break
    return new_network_id




@bp.route('/<int:network_id>/manage_members_network', methods=('GET', 'POST'))
@login_required
def manage_members_network(network_id):
    network = get_network(network_id)
    network_members = get_network_members(network_id)

    if (request.method == 'POST'):
        invitee = request.form['invitee']
        error = None

        if (not invitee):
            error = 'Invitee UserID is required.'


        if (error is not None):
            flash(error)
        else:
            db = get_db()
            
            user = db.execute(
                'SELECT * FROM User WHERE id = ?', (invitee,)
            ).fetchone()
            
            if (user is None):
                error = "No user found with that UserID!"
                flash(error)
            else:
                # Invite the User, somehow...
                # First, check if the user is already a member of the network.
                user_is_a_member = False
                for network_member in network_members:
                    if (network_member['user_id'] == user['id']):
                        user_is_a_member = True
                        break

                if ((not user_is_a_member) and (g.user['id'] == network['owner'])):
                    db.execute(
                        'INSERT INTO UserNetworkAssociation (user_id, network_id)'
                        ' VALUES (?, ?)',
                        (user['id'], network_id)
                    )
                    db.commit() 
                # Re-populate this, so the fresh display shows new members.
                network_members = get_network_members(network_id)

        return render_template('console/manage_members_network.html', network=network, network_members=network_members)

    return render_template('console/manage_members_network.html', network=network, network_members=network_members)




@bp.route('/<int:network_id>/update_network', methods=('GET', 'POST'))
@login_required
def update_network(network_id):
    network = get_network(network_id)
    db = get_db()

    if (request.method == 'POST'):
        name = request.form['name']
        error = None

        if (not name):
            error = 'Name is required.'

        if (error is not None):
            flash(error)
        else:
            db = get_db()

            db.execute(
                'UPDATE Network SET name = ?'
                ' WHERE id = ?',
                (name, network_id)
            )
            db.commit()
            return redirect(url_for('console.index'))
    
    return render_template('console/update_network.html', network=network)



@bp.route('/<int:network_id>/<int:user_id>/remove_user_from_network', methods=('POST',))
@login_required
def remove_user_from_network(network_id, user_id):
    network = get_network(network_id)
    db = get_db()
    if ((user_id != network['owner']) and (g.user['id'] == network['owner'])):
        db.execute('DELETE FROM UserNetworkAssociation WHERE network_id = ? AND user_id = ?', (network_id, user_id,))
        db.commit()
    return redirect(url_for('console.manage_members_network', network_id=network_id))


@bp.route('/<int:network_id>/delete_network', methods=('POST',))
@login_required
def delete_network(network_id):
    network = get_network(network_id)
    
    if (g.user['id'] == network['owner']):
        db = get_db()
        db.execute('DELETE FROM UserNetworkAssociation WHERE network_id = ?', (network_id,))
        db.execute('DELETE FROM Network WHERE id = ?', (network_id,))
        db.commit()

    return redirect(url_for('console.index'))
