DROP TABLE IF EXISTS D_LAB2HPO_MAP_ERR;
CREATE TABLE D_LAB2HPO_MAP_ERR (	-- rows=755
   ERR_ID VARCHAR(7) NOT NULL, -- error code
   ERR_LABEL VARCHAR(255) NOT NULL, -- error label
   PRIMARY KEY (ERR_ID)
  );

INSERT IGNORE INTO D_LAB2HPO_MAP_ERR(ERR_ID, ERR_LABEL)
VALUES 
    ('ERROR1', 'local id not mapped to loinc'),
    ('ERROR2', 'malformed loinc id'),
    ('ERROR3', 'loinc code not annotated'),
    ('ERROR4', 'interpretation code not mapped to hpo'),
    ('ERROR5', 'unable to interpret'),
    ('ERROR6', 'unrecognized unit');