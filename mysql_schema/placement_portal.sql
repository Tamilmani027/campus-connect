CREATE DATABASE IF NOT EXISTS placement_portal;
USE placement_portal;

CREATE TABLE file_storage (
  id INT AUTO_INCREMENT PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_size INT NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE companies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  website VARCHAR(255),
  sector VARCHAR(100),
  logo_file_id INT,
  profile_doc_id INT,
  FOREIGN KEY (logo_file_id) REFERENCES file_storage(id) ON DELETE SET NULL,
  FOREIGN KEY (profile_doc_id) REFERENCES file_storage(id) ON DELETE SET NULL
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

CREATE TABLE resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(150) NOT NULL,
  url VARCHAR(500),
  description TEXT,
  category VARCHAR(50) DEFAULT 'GENERAL',
  file_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES file_storage(id) ON DELETE SET NULL
);

CREATE TABLE resume_samples (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(150) NOT NULL,
  url VARCHAR(500),
  file_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES file_storage(id) ON DELETE SET NULL
);

CREATE TABLE announcements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(150) NOT NULL,
  content TEXT NOT NULL,
  file_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES file_storage(id) ON DELETE SET NULL
);

CREATE TABLE study_plans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  duration_days INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  plan_id INT NOT NULL,
  day_number INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  reference_link VARCHAR(500),
  FOREIGN KEY (plan_id) REFERENCES study_plans(id) ON DELETE CASCADE
);

CREATE TABLE student_subscriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL, -- Assuming students table exists or will be created
  plan_id INT NOT NULL,
  start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  current_day INT DEFAULT 1,
  completed_tasks TEXT, -- JSON array of task IDs
  FOREIGN KEY (plan_id) REFERENCES study_plans(id) ON DELETE CASCADE
);

CREATE TABLE questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  type VARCHAR(50) NOT NULL, -- CODING, APTITUDE, HR
  difficulty VARCHAR(50) NOT NULL DEFAULT 'MEDIUM',
  topic VARCHAR(100),
  company_tags VARCHAR(500),
  options JSON, -- For Aptitude
  correct_option VARCHAR(5),
  solution TEXT,
  test_cases JSON, -- For Coding
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_progress (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  question_id INT NOT NULL,
  status VARCHAR(20) DEFAULT 'ATTEMPTED',
  submission_code TEXT,
  user_notes TEXT,
  is_bookmarked BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE forum_threads (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  tags VARCHAR(200),
  views INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE forum_replies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  thread_id INT NOT NULL,
  student_id INT, -- Null if admin
  admin_id INT, -- Null if student
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (thread_id) REFERENCES forum_threads(id) ON DELETE CASCADE
);

CREATE TABLE bookmarks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL, -- Generic user ID (usually student)
  entity_type VARCHAR(50) NOT NULL, -- 'interview_experience', 'question', 'resource'
  entity_id INT NOT NULL,
  note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: 'students' table is referenced but not explicitly created in the initial dump.
-- Ensuring 'students' table exists for relationships if it was missing or implied.
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  college VARCHAR(200),
  department VARCHAR(100),
  year_of_passing INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
