
CREATE TABLE pv_users.userSession 
(
    sessionId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT REFERENCES users (userId),
    token NVARCHAR(256) NOT NULL,
    lastLogin datetime NOT NULL,
    sessionStatus BIT NOT NULL
);

CREATE TABLE pv_users.users
(
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userName NVARCHAR(10) NOT NULL,
    userPassword BINARY(32) NOT NULL,
    userEmail NVARCHAR(256) NOT NULL

);








