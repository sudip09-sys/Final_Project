-- Reference schema. SQLAlchemy creates the equivalent tables on startup.
-- Always back up an existing database before applying schema changes.
CREATE TABLE people (
 id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
 student_id VARCHAR(32) NOT NULL UNIQUE,
 name VARCHAR(100) NOT NULL,
 cohort VARCHAR(80) NOT NULL,
 embedding TEXT NULL,
 consented_at DATETIME NULL,
 created_at DATETIME NOT NULL
) ENGINE=InnoDB;
CREATE TABLE class_sessions (
 id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(100) NOT NULL,
 cohort VARCHAR(80) NOT NULL,
 opened_at DATETIME NOT NULL,
 is_open BOOLEAN NOT NULL
) ENGINE=InnoDB;
CREATE TABLE attendance (
 id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
 person_id INTEGER NOT NULL,
 session_id INTEGER NOT NULL,
 marked_at DATETIME NOT NULL,
 method VARCHAR(16) NOT NULL,
 distance FLOAT NULL,
 note VARCHAR(200) NOT NULL,
 CONSTRAINT uq_attendance UNIQUE(person_id, session_id),
 FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE,
 FOREIGN KEY(session_id) REFERENCES class_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE TABLE audit (
 id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
 at DATETIME NOT NULL,
 action VARCHAR(64) NOT NULL,
 detail VARCHAR(200) NOT NULL
) ENGINE=InnoDB;
