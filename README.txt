1. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
2. Devices time, baby! Work on adding/removing devices in a reasonable way.
    # Devices should register with the server and be provisioned a unique [Device.id].
    # Devices should have an add/remove interface identical to the user management interface.
    #   This means devices should store their ID locally after being provisioned, and this should be given to network admins/owners.
3. Consider adding "admin" groups, instead of strictly requiring owners to do things.
    # Easy enough; add an association table for admins. Columns: network_id, user_id. Both foreign keys.
    # Could just be an extension of existing association table for users/networks. Just add a 'priv' field, 0-1-2 = member, admin, owner.
