
CREATE TABLE IF NOT EXISTS D_LAB2HPO_MAP_ERR (	-- rows=755
   ERR_ID VARCHAR(6) NOT NULL, -- error code
   ERR_LABEL VARCHAR(20) NOT NULL, -- error label
   PRIMARY KEY (ERR_ID)
  );

INSERT IGNORE INTO D_LAB2HPO_MAP_ERR(ERR_ID, ERR_LABEL)
VALUES 
    ('ERROR1', 'local id not mapped to loinc'),
    ('ERROR2', 'malformed loinc id'),
    ('ERROR3', 'loinc code not annotated'),
    ('ERROR4', 'interpretation code not mapped to hpo'),
    ('ERROR5', 'ERROR 5: unable to interpret'),
    ('ERROR6', 'unrecognized unit');