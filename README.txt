Current TODO:
1. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
2. Add a way to remove users from networks. (jinja loop over all users in network, add remove button with confirmation popup).
3. Change User.id field from AUTOINCREMENT to a random, 9-digit number upon user creation.
    # Ensure no overlaps!
    # Greedy approach could be an issue, if this ever has > log_2(10^9) users.
    # Ha. JK.
4. 
