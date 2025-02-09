from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
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
    
    devices = db.execute(
        'SELECT * from Device d'
        ' JOIN DeviceUserAssociation dua on d.id = dua.device_id'
        ' WHERE dua.user_id = ?', (g.user['id'],)
    ).fetchall()

    return render_template('console/index.html', networks=networks, devices=devices)



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


def get_device(device_id, check_owner=True):
    device = get_db().execute(
        'SELECT *'
        ' FROM Device d JOIN DeviceUserAssociation dua on d.owner = dua.user_id'
        ' WHERE d.id = ?',
        (device_id,)
    ).fetchone()
    
    if (device is None):
        abort(404, f"Device id {id} doesn't exist.")

    if ((check_owner) and (device['owner'] != g.user['id'])):
        abort(403)
    
    return device


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


def get_network_devices(network_id):
    network_devices = get_db().execute(
        'SELECT *'
        ' FROM DeviceNetworkAssociation dna JOIN Device d on dna.device_id = d.id'
        ' WHERE dna.network_id = ?',
        (network_id,)
    ).fetchall()
    return network_devices



@bp.route('/<int:network_id>/manage_devices_network', methods=('GET', 'POST'))
@login_required
def manage_devices_network(network_id):
    network = get_network(network_id)
    network_devices = get_network_devices(network_id)
    for nd in network_devices:
        print(nd)

    if (request.method == 'POST'):
        new_device_id = request.form['new_device_id']
        error = None

        if (not new_device_id):
            error = 'No DeviceID was supplied.'
        
        if (error is not None):
            flash(error)
        else:
            db = get_db()
            device = db.execute(
                'SELECT * FROM Device WHERE id = ?', (new_device_id,)
            ).fetchone()
            if (device is None):
                error = "No device found with that DeviceID!"
                flash(error)
            else:
                # First, check if the device already belongs to the network.
                device_in_network = False
                for network_device in network_devices:
                    if (network_device['device_id'] == device['id']):
                        device_in_network = True
                        break

                if ((not device_in_network) and (g.user['id'] == network['owner'])):
                    db.execute(
                        'INSERT INTO DeviceNetworkAssociation (device_id, network_id)'
                        ' VALUES (?, ?)',
                        (device['id'], network_id)
                    )
                    db.commit() 
                # Re-populate this, so the display shows newly added devices.
                network_devices = get_network_devices(network_id)

        return render_template('console/manage_devices_network.html', network=network, network_devices=network_devices)

    return render_template('console/manage_devices_network.html', network=network, network_devices=network_devices)
    


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



@bp.route('/<int:network_id>/view_network', methods=('GET',))
def view_network(network_id):
    network = get_network(network_id, False)
    network_members = get_network_members(network_id)
    devices = get_network_devices(network_id)
    return(render_template('console/view_network.html', network=network, network_members=network_members, network_devices=devices))



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


@bp.route('/<int:device_id>/update_device', methods=('GET', 'POST'))
@login_required
def update_device(device_id):
    device = get_device(device_id)
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
                'UPDATE Device SET name = ?'
                ' WHERE id = ?',
                (name, device_id)
            )
            db.commit()
            return redirect(url_for('console.index'))
    
    return render_template('console/update_device.html', device=device)




@bp.route('/<int:network_id>/<int:device_id>/remove_device_from_network', methods=('POST',))
@login_required
def remove_device_from_network(network_id, device_id):
    network = get_network(network_id)
    db = get_db()
    if (g.user['id'] == network['owner']):
        db.execute('DELETE FROM DeviceNetworkAssociation WHERE network_id = ? AND device_id = ?', (network_id, device_id,))
        db.commit()
    return redirect(url_for('console.manage_devices_network', network_id=network_id))


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
        db.execute('DELETE FROM DeviceNetworkAssociation WHERE network_id = ?', (network_id,))
        db.execute('DELETE FROM UserNetworkAssociation WHERE network_id = ?', (network_id,))
        db.execute('DELETE FROM Network WHERE id = ?', (network_id,))
        db.commit()

    return redirect(url_for('console.index'))



@bp.route('/<int:device_id>/delete_device', methods=('POST',))
@login_required
def delete_device(device_id):
    device = get_device(device_id)
    if (g.user['id'] == device['owner']):
        db = get_db()
        db.execute('DELETE FROM DeviceUserAssociation WHERE device_id = ?', (device_id,))
        db.execute('DELETE FROM DeviceNetworkAssociation WHERE device_id = ?', (device_id,))
        db.execute('DELETE FROM Device WHERE id = ?', (device_id,))
        db.commit()

    return redirect(url_for('console.index'))
