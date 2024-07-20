

1) First, install MySQL.

2) Then, use this command:
```
CREATE DATABASE farm_management;

USE farm_management;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Farmer', 'Worker') NOT NULL
);

CREATE TABLE Farmer (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255)
);

CREATE TABLE Farm (
    farm_id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    size DECIMAL(10,2) NOT NULL,
    farmer_id INT,
    FOREIGN KEY (farmer_id) REFERENCES Farmer(farmer_id)
);

CREATE TABLE Worker (
    worker_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(255),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE Crop (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    variety VARCHAR(100),
    planting_date DATE,
    expected_harvest_date DATE,
    description TEXT,
    part_of_country VARCHAR(100),
    soil_type VARCHAR(100),
    images VARCHAR(255),
    farm_id INT,
    FOREIGN KEY (farm_id) REFERENCES Farm(farm_id)
);

CREATE TABLE CropInventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT,
    quantity INT,
    FOREIGN KEY (crop_id) REFERENCES Crop(crop_id)
);

CREATE TABLE Messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id VARCHAR(100),
    worker_name VARCHAR(100),
    farmer_name VARCHAR(100),
    money DECIMAL(10,2),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

To run the program, use the following command in the terminal: 
streamlit run login.py
