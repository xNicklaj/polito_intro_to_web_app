/* Tables */
CREATE TABLE USER (
    Username VARCHAR(64) NOT NULL,
    Display_Name VARCHAR(64) NOT NULL,
    Is_Creator BOOLEAN NOT NULL,
    Password TEXT NOT NULL,
    PRIMARY KEY (Username)
);
CREATE TABLE PODCAST (
    PodcastID INTEGER NOT NULL,
    Description TEXT NOT NULL,
    Title VARCHAR(64) NOT NULL,
    Thumbnail TEXT NOT NULL,
    USER_Username VARCHAR(64) NOT NULL,
    PRIMARY KEY (PodcastID),
    FOREIGN KEY (USER_Username) REFERENCES USER(Username)
);
CREATE TABLE EPISODE (
    PODCAST_PodcastID INTEGER NOT NULL,
    Title VARCHAR(64) NOT NULL,
    Release_Date DATETIME NOT NULL,
    Track TEXT NOT NULL,
    Description TEXT NOT NULL,
    PRIMARY KEY (PODCAST_PodcastID, Title),
    FOREIGN KEY (PODCAST_PodcastID) REFERENCES PODCAST(PodcastID)
);
CREATE TABLE COMMENT (
    EPISODE_PODCAST_PodcastID INTEGER NOT NULL,
    EPISODE_Title VARCHAR(64) NOT NULL,
    USER_Username VARCHAR(64) NOT NULL,
    Date_Published DATETIME NOT NULL,
    Content TEXT NOT NULL,
    PRIMARY KEY (EPISODE_PODCAST_PodcastID, EPISODE_Title, USER_Username, Date_Published),
    FOREIGN KEY (EPISODE_PODCAST_PodcastID) REFERENCES EPISODE(PODCAST_PodcastID),
    FOREIGN KEY (EPISODE_Title) REFERENCES EPISODE(Title),
    FOREIGN KEY (USER_Username) REFERENCES USER(Username)
);
CREATE TABLE CATEGORY (
    Name VARCHAR(64) NOT NULL,
    PRIMARY KEY (Name)
);
CREATE TABLE FOLLOWING (
    USER_Username VARCHAR(64) NOT NULL,
    PODCAST_PodcastID INTEGER NOT NULL,
    PRIMARY KEY (USER_Username, PODCAST_PodcastID),
    FOREIGN KEY (USER_Username) REFERENCES USER(Username),
    FOREIGN KEY (PODCAST_PodcastID) REFERENCES PODCAST(PodcastID)
);
CREATE TABLE PODCAST_CATEGORY (
    PODCAST_PodcastID INTEGER NOT NULL,
    CATEGORY_Name VARCHAR(64) NOT NULL,
    PRIMARY KEY (PODCAST_PodcastID, CATEGORY_Name),
    FOREIGN KEY (PODCAST_PodcastID) REFERENCES PODCAST(PodcastID),
    FOREIGN KEY (CATEGORY_Name) REFERENCES CATEGORY(Name)
);