Things to do before this functions:
1. Create a CA. I did this using XCA. Then create a keypair + cert.
2. Create a serverside cert and key, signed by your CA.
3. Place the service cert + key in ./flask-api/secrets. Verify the .gitignore.
4. Modify the ./flask-api/run.sh script to use your cert and key.
5. Should be off to the races!
6. For tailscale users, if you're testing locally, make sure to use `tailscale serve 5000` or equivalent functionality so you don't have to worry about localhost/ssl issues.


TODO:
0? Change from using session variables for continued access to JWTs.
    # Then I can set expiry conditions!
    # Not auto-authenticate on future requests!
    # Etc! Plus it's new and fancy and good learning.
1. Make endpoints for devices. Time to actually handle the parts where:
    # # # SERVER-SIDE RESPONSIBILITIES # # #
    # Devices register with the server via user login on the device (Done)
    # Endpoint to which devices send publications to the server. Should contains:
    #   Content (Pictures? Text? Etc.)
    #   Destinations (Networks upon which to publish content)
    #   Scheduling?
    #
    # # # CLIENT-SIDE RESPONSIBILITIES # # #
    # Devices should have a way to create new content, and publish it to the server.
    #   Content: Images? Text? Audio?
    #   Destinations: Select which networks upon which to publish content.
    #   Scheduling?
    #
    # Devices can view information that has previously been sent to their networks
    #   Devices can choose which networks to view (all, none, or any combination)
    #   This populates a local scrolling feed, based on selections.
    #   New publications to networks that aren't current selected are indicated.
    #   New publications to networks that ARE currently selected pop up bigly.
    # 
    # Should devices have a way to access the admin console?
    #
    # # # HUMAN-SIDE RESPONSIBILITIES # # #
    # Devices need to be provisioned on creation.
    #   CA cert.
    #   Client software.
    #   Anything else...

2. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
    # Right now, this is one-sided. 
    # You give me your UserID, and I can add you to my networks.
    # Still requires an exchange of information, but I think invites are nicer.

Basic device stuff is complete.
    I've decided that logging in as a user is enough for now.
    This is mostly coerced from the fact that mTCL is not fully supported in Flask.
    The server is authenticated using TCP and the CA cert. The device is trusted
        because it has login credentials.
