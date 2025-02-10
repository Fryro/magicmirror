DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Device;
DROP TABLE IF EXISTS Network;
DROP TABLE IF EXISTS UserNetworkAssociation;
DROP TABLE IF EXISTS DeviceNetworkAssociation;
DROP TABLE IF EXISTS DeviceUserAssociation;

CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE Device (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    owner INTEGER NOT NULL,
    owner_name TEXT NOT NULL,
    FOREIGN KEY (owner) REFERENCES User (id)
);

CREATE TABLE Network (
    id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL,
    owner INTEGER NOT NULL,
    owner_name TEXT NOT NULL,
    FOREIGN KEY (owner) REFERENCES User (id)
);

CREATE TABLE UserNetworkAssociation (
    user_id INTEGER,
    network_id INTEGER, 
    FOREIGN KEY (user_id) references User (id),
    FOREIGN KEY (network_id) REFERENCES Network (id)
);

CREATE TABLE DeviceNetworkAssociation (
    device_id INTEGER,
    network_id INTEGER,
    FOREIGN KEY (device_id) REFERENCES Device (id),
    FOREIGN KEY (network_id) REFERENCES Network (id)
);

CREATE TABLE DeviceUserAssociation (
    user_id INTEGER,
    device_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (device_id) REFERENCES Device (id)
);
