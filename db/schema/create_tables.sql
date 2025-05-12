-- 1. Social media platforms
CREATE TABLE SocialMedia (
  MediaName VARCHAR(50) PRIMARY KEY
);

-- 2. Users
CREATE TABLE User (
  MediaName       VARCHAR(50),
  Username        VARCHAR(40),
  FirstName       VARCHAR(50),
  LastName        VARCHAR(50),
  CountryOfBirth  VARCHAR(50),
  CountryOfResidence VARCHAR(50),
  Age             INT,
  Gender          ENUM('Male','Female','Other'),
  IsVerified      BOOLEAN,
  PRIMARY KEY (MediaName, Username),
  FOREIGN KEY (MediaName) REFERENCES SocialMedia(MediaName)
);

-- 3. Posts (composite PK enforces one‐post‐per‐user‐per‐time)
CREATE TABLE Post (
  MediaName    VARCHAR(50),
  Username     VARCHAR(40),
  TimePosted   DATETIME,
  TextContent  TEXT     NOT NULL,
  City         VARCHAR(50),
  State        VARCHAR(50),
  Country      VARCHAR(50),
  Likes        INT DEFAULT 0    CHECK (Likes    >= 0),
  Dislikes     INT DEFAULT 0    CHECK (Dislikes >= 0),
  HasMultimedia BOOLEAN,
  PRIMARY KEY (MediaName, Username, TimePosted),
  FOREIGN KEY (MediaName, Username) 
    REFERENCES User(MediaName, Username)
);

-- 4. Reposts (relationship with attribute RepostTime)
CREATE TABLE Repost (
  OrigMedia      VARCHAR(50),
  OrigUser       VARCHAR(40),
  OrigTime       DATETIME,
  ReposterMedia  VARCHAR(50),
  ReposterUser   VARCHAR(40),
  RepostTime     DATETIME,
  PRIMARY KEY (
    OrigMedia, OrigUser, OrigTime,
    ReposterMedia, ReposterUser, RepostTime
  ),
  FOREIGN KEY (OrigMedia, OrigUser, OrigTime)
    REFERENCES Post(MediaName, Username, TimePosted),
  FOREIGN KEY (ReposterMedia, ReposterUser)
    REFERENCES User(MediaName, Username)
);

-- 5. Institutes
CREATE TABLE Institute (
  InstituteName VARCHAR(100) PRIMARY KEY
);

-- 6. Projects
CREATE TABLE Project (
  ProjectName      VARCHAR(100) PRIMARY KEY,
  ManagerFirstName VARCHAR(50),
  ManagerLastName  VARCHAR(50),
  InstituteName    VARCHAR(100),
  StartDate        DATE,
  EndDate          DATE,
  FOREIGN KEY (InstituteName) REFERENCES Institute(InstituteName),
  CHECK (EndDate >= StartDate)
);

-- 7. Fields (unique per project)
CREATE TABLE Field (
  ProjectName VARCHAR(100),
  FieldName   VARCHAR(50),
  PRIMARY KEY (ProjectName, FieldName),
  FOREIGN KEY (ProjectName) REFERENCES Project(ProjectName)
);

-- 8. Which posts each project will analyze (relationship)
CREATE TABLE ProjectPost (
  ProjectName VARCHAR(100),
  MediaName   VARCHAR(50),
  Username    VARCHAR(40),
  TimePosted  DATETIME,
  PRIMARY KEY (ProjectName, MediaName, Username, TimePosted),
  FOREIGN KEY (ProjectName)             REFERENCES Project(ProjectName),
  FOREIGN KEY (MediaName, Username, TimePosted)
    REFERENCES Post(MediaName, Username, TimePosted)
);

-- 9. Analysis results for each (Project, Field, Post)
CREATE TABLE PostAnalysis (
  ProjectName VARCHAR(100),
  FieldName   VARCHAR(50),
  MediaName   VARCHAR(50),
  Username    VARCHAR(40),
  TimePosted  DATETIME,
  Value       TEXT,
  PRIMARY KEY (ProjectName, FieldName, MediaName, Username, TimePosted),
  FOREIGN KEY (ProjectName, FieldName)
    REFERENCES Field(ProjectName, FieldName),
  FOREIGN KEY (MediaName, Username, TimePosted)
    REFERENCES Post(MediaName, Username, TimePosted)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (ProjectName, MediaName, Username, TimePosted)
    REFERENCES ProjectPost(ProjectName, MediaName, Username, TimePosted)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
