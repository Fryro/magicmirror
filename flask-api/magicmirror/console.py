from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from magicmirror.auth import login_required
from magicmirror.db import get_db

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
    print(networks)
    print(una)
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
            db.execute(
                'INSERT INTO Network (name, owner)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
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


@bp.route('/<int:network_id>/update_network', methods=('GET', 'POST'))
@login_required
def update_network(network_id):
    network = get_network(network_id)

    if (request.method == 'POST'):
        name = request.form['name']
        #invitee = request.form['invitee']
        error = None

        if (not name):
            error = 'Name is required.'

        if (error is not None):
            flash(error)
        else:
            db = get_db()
            
            #if (invitee):
            #   user = db.execute(
            #       'SELECT * FROM User WHERE name = ?', (invitee,)
            #   )

            db.execute(
                'UPDATE Network SET name = ?'
                ' WHERE id = ?',
                (name, network_id)
            )
            db.commit()
            return redirect(url_for('console.index'))

    return render_template('console/update_network.html', network=network)


@bp.route('/<int:network_id>/delete_network', methods=('POST',))
@login_required
def delete_network(network_id):
    get_network(network_id)
    db = get_db()
    db.execute('DELETE FROM UserNetworkAssociation WHERE network_id = ?', (network_id,))
    db.execute('DELETE FROM Network WHERE id = ?', (network_id,))
    db.commit()
    return redirect(url_for('console.index'))
