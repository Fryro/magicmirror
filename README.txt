1. Integrate Email/SMS or build a native way to recieve and accept invitations to networks.
2. Change User.id field from AUTOINCREMENT to a random, 9-digit number upon user creation.
    # Ensure no overlaps!
    # Greedy approach could be an issue, if this ever has > log_2(10^9) users.
    # Ha. JK.
3. Consider adding "admin" groups, instead of strictly requiring owners to do things.
    # CONSIDER is used heavily here. Might just decide that only owner can do things.
