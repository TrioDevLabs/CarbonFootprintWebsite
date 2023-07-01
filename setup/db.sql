-- Active: 1687100659996@@127.0.0.1@3306@carbonemissiondb
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;


DROP SCHEMA IF EXISTS CarbonEmissionDB;
CREATE SCHEMA IF NOT EXISTS CarbonEmissionDB;
USE CarbonEmissionDB;

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    SecurityCode VARCHAR(255) ,
    Confirmed boolean DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserSessions (
    SessionID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    LoginTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LogoutTime TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

CREATE TABLE TwoFactorAuth (
    AuthID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    OTP VARCHAR(6),
    ExpiryTime TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

CREATE TABLE HouseholdUsage (
    UsageID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    PropaneUsage DECIMAL(10,2),
    NaturalGasUsage DECIMAL(10,2),
    ElectricityUsage DECIMAL(10,2),
    FuelOilUsage DECIMAL(10,2),
    MonthYear DATE,
    Emissions FLOAT,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

CREATE TABLE Vehicles (
    VehicleID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    NumberOfVehicles INT,
    AverageMilesDriven DECIMAL(10,2),
    AverageMileage DECIMAL(10,2),
    MonthYear DATE,
    Emissions FLOAT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);



