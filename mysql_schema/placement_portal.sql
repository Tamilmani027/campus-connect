CREATE DATABASE IF NOT EXISTS placement_portal;
USE placement_portal;

CREATE TABLE companies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  website VARCHAR(255),
  sector VARCHAR(100)
);

CREATE TABLE company_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  year INT NOT NULL,
  role VARCHAR(255),
  salary VARCHAR(100),
  rounds_count INT DEFAULT 0,
  eligibility VARCHAR(255),
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE placement_rounds (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_history_id INT NOT NULL,
  round_name VARCHAR(255) NOT NULL,
  round_description VARCHAR(1000),
  difficulty_level VARCHAR(50),
  FOREIGN KEY (company_history_id) REFERENCES company_history(id) ON DELETE CASCADE
);

CREATE TABLE company_questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  question VARCHAR(2000) NOT NULL,
  category VARCHAR(50),
  difficulty VARCHAR(50),
  year INT,
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE interview_experiences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_name VARCHAR(255) NOT NULL,
  department VARCHAR(100),
  batch INT,
  company_id INT NOT NULL,
  role VARCHAR(255),
  experience_text TEXT NOT NULL,
  rounds VARCHAR(1000),
  questions_faced VARCHAR(2000),
  tips VARCHAR(1000),
  status VARCHAR(50) DEFAULT 'pending',
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL
);
