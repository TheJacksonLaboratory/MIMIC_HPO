

CREATE TABLE ADMISSIONS (	-- rows=58976
   ROW_ID SMALLINT UNSIGNED NOT NULL,
   SUBJECT_ID MEDIUMINT UNSIGNED NOT NULL,
   HADM_ID MEDIUMINT UNSIGNED NOT NULL,
   ADMITTIME DATETIME NOT NULL,
   DISCHTIME DATETIME NOT NULL,
   DEATHTIME DATETIME,
   ADMISSION_TYPE VARCHAR(255) NOT NULL,	-- max=9
   ADMISSION_LOCATION VARCHAR(255) NOT NULL,	-- max=25
   DISCHARGE_LOCATION VARCHAR(255) NOT NULL,	-- max=25
   INSURANCE VARCHAR(255) NOT NULL,	-- max=10
   LANGUAGE VARCHAR(255),	-- max=4
   RELIGION VARCHAR(255),	-- max=22
   MARITAL_STATUS VARCHAR(255),	-- max=17
   ETHNICITY VARCHAR(255) NOT NULL,	-- max=56
   EDREGTIME DATETIME,
   EDOUTTIME DATETIME,
   DIAGNOSIS TEXT,	-- max=189
   HOSPITAL_EXPIRE_FLAG TINYINT UNSIGNED NOT NULL,
   HAS_CHARTEVENTS_DATA TINYINT UNSIGNED NOT NULL,
  UNIQUE KEY ADMISSIONS_ROW_ID (ROW_ID),	-- nvals=58976
  UNIQUE KEY ADMISSIONS_HADM_ID (HADM_ID)	-- nvals=58976
  )
  CHARACTER SET = UTF8;

LOAD DATA LOCAL INFILE 'ADMISSIONS.csv' INTO TABLE ADMISSIONS
   FIELDS TERMINATED BY ',' ESCAPED BY '\\' OPTIONALLY ENCLOSED BY '"'
   LINES TERMINATED BY '\n'
   IGNORE 1 LINES
   (@ROW_ID,@SUBJECT_ID,@HADM_ID,@ADMITTIME,@DISCHTIME,@DEATHTIME,@ADMISSION_TYPE,@ADMISSION_LOCATION,@DISCHARGE_LOCATION,@INSURANCE,@LANGUAGE,@RELIGION,@MARITAL_STATUS,@ETHNICITY,@EDREGTIME,@EDOUTTIME,@DIAGNOSIS,@HOSPITAL_EXPIRE_FLAG,@HAS_CHARTEVENTS_DATA)
 SET
   ROW_ID = @ROW_ID,
   SUBJECT_ID = @SUBJECT_ID,
   HADM_ID = @HADM_ID,
   ADMITTIME = @ADMITTIME,
   DISCHTIME = @DISCHTIME,
   DEATHTIME = IF(@DEATHTIME='', NULL, @DEATHTIME),
   ADMISSION_TYPE = @ADMISSION_TYPE,
   ADMISSION_LOCATION = @ADMISSION_LOCATION,
   DISCHARGE_LOCATION = @DISCHARGE_LOCATION,
   INSURANCE = @INSURANCE,
   LANGUAGE = IF(@LANGUAGE='', NULL, @LANGUAGE),
   RELIGION = IF(@RELIGION='', NULL, @RELIGION),
   MARITAL_STATUS = IF(@MARITAL_STATUS='', NULL, @MARITAL_STATUS),
   ETHNICITY = @ETHNICITY,
   EDREGTIME = IF(@EDREGTIME='', NULL, @EDREGTIME),
   EDOUTTIME = IF(@EDOUTTIME='', NULL, @EDOUTTIME),
   DIAGNOSIS = IF(@DIAGNOSIS='', NULL, @DIAGNOSIS),
   HOSPITAL_EXPIRE_FLAG = @HOSPITAL_EXPIRE_FLAG,
   HAS_CHARTEVENTS_DATA = @HAS_CHARTEVENTS_DATA;