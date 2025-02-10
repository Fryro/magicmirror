Things to do before this functions:
1. Create a CA. I did this using XCA. Then create a keypair + cert.
2. Create a serverside cert and key, signed by your CA.
3. Place the service cert + key in ./flask-api/secrets. Verify the .gitignore.
4. Modify the ./flask-api/run.sh script to use your cert and key.
5. Should be off to the races!
6. For tailscale users, if you're testing locally, make sure to use `tailscale serve 5000` or equivalent functionality so you don't have to worry about localhost/ssl issues.


TODO:
1. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
2. Basic device stuff is complete.
    I've decided that logging in as a user is enough for now.
    This is mostly coerced from the fact that mTCL is not fully supported in Flask.
    The server is authenticated using TCP and the CA cert. The device is trusted
        because it has login credentials.
