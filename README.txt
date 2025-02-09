1. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
2. Basic device stuff is complete.
    # Devices generate a priv/pub asym keypair upon fabrication (when I make it and run the software lol).
    # User logs into device with user/pass. This will cause the device to contact auth server.
    #   If valid credentials, then auth server registers the device + device/user association in database.
    #   Request then returns a JSON containing the Device's provisioned ID.
    #   This is important, make sure it works!
    #
    #   TODO: Write device software
    #   So far, expecations for the device software are:
    #   Store an asym keypair locally.
    #   Have a login page, required before anything else is accessed (besides maybe device name).
    #   After logging in, store provisioned device ID somewhere locally. This is the device's identifier, and the key is authentication.
3. Consider adding "admin" groups, instead of strictly requiring owners to do things.
    # Easy enough; add an association table for admins. Columns: network_id, user_id. Both foreign keys.
    # Could just be an extension of existing association table for users/networks. Just add a 'priv' field, 0-1-2 = member, admin, owner.
