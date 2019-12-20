from configparser import ConfigParser
import mysql.connector
import numpy as np
import pandas as pd
import math
import os
import sys
import logging

mf_module_path = os.path.abspath(os.path.join('../python'))
if mf_module_path not in sys.path:
    sys.path.append(mf_module_path)
import mf
import mf_random
import synergy_tree
from ontology import Ontology
import pickle
from tqdm import tqdm, tqdm_notebook

# load configuration file
config = ConfigParser()
config.read('analysisConfig.properties')

# set up MySql connection
host = config['Database']['host']
user = config['Database']['user']
password = config['Database']['password']
database = config['Database']['database']

mydb = mysql.connector.connect(host=host,
                               user=user,
                               passwd=password,
                               database=database,
                               auth_plugin='mysql_native_password')
cursor = mydb.cursor(buffered=True)


def encounterOfInterest(debug=False, N=100):
    """
    Define encounters of interest. The method is not finalized yet.
    Currently, it will use all encounters in our database.
    :param debug: set to True to select a small subset for testing
    :param N: limit the number of encounters when debug is set to True. If
    debug is set to False, N is ignored.
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_encounterOfInterest')
    if debug:
        limit = 'LIMIT {}'.format(N)
    else:
        limit = ''
    # This is admissions that we want to analyze, 'LIMIT 100' in debug mode
    cursor.execute('''
                CREATE TEMPORARY TABLE IF NOT EXISTS JAX_encounterOfInterest(
                    ROW_ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY)

                SELECT 
                    DISTINCT SUBJECT_ID, HADM_ID 
                FROM admissions
                {}
                '''.format(limit))


def indexEncounterOfInterest():
    """
    Create index on encounters table.
    """
    cursor.execute(
        'CREATE INDEX JAX_encounterOfInterest_idx01 ON JAX_encounterOfInterest '
        '(SUBJECT_ID, HADM_ID)')


def diagnosisProfile():
    """
    For encounters of interest, find all of their diagnosis codes
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_diagnosisProfile')
    cursor.execute('''
                CREATE TEMPORARY TABLE IF NOT EXISTS JAX_diagnosisProfile
                SELECT 
                    DIAGNOSES_ICD.SUBJECT_ID, 
                    DIAGNOSES_ICD.HADM_ID, 
                    DIAGNOSES_ICD.ICD9_CODE, 
                    DIAGNOSES_ICD.SEQ_NUM
                FROM
                    DIAGNOSES_ICD
                RIGHT JOIN
                    JAX_encounterOfInterest
                ON 
                    DIAGNOSES_ICD.SUBJECT_ID = JAX_encounterOfInterest.SUBJECT_ID 
                    AND 
                    DIAGNOSES_ICD.HADM_ID = JAX_encounterOfInterest.HADM_ID
                ''')


def textHpoProfile(include_inferred=True):
    """
    Set up a table for patient phenotypes from text mining. By default,
    merge directly mapped HPO terms and inferred terms.
    It is currently defined as a temporary table. But in reality, it is
    created as a permanent table as it takes a long time to init, and it is
    going to be used multiple times.
    :param include_inferred: true if to include inferred terms
    """
    if include_inferred:
        cursor.execute('''
            CREATE TEMPORARY TABLE IF NOT EXISTS JAX_textHpoProfile
            WITH abnorm AS (
                SELECT
                    NOTEEVENTS.SUBJECT_ID, NOTEEVENTS.HADM_ID, NoteHpoClinPhen.MAP_TO
                FROM 
                    NOTEEVENTS 
                JOIN NoteHpoClinPhen on NOTEEVENTS.ROW_ID = NoteHpoClinPhen.NOTES_ROW_ID

                UNION ALL

                SELECT
                    NOTEEVENTS.SUBJECT_ID, NOTEEVENTS.HADM_ID, 
                    Inferred_NoteHpo.INFERRED_TO AS MAP_TO
                FROM 
                    NOTEEVENTS 
                JOIN Inferred_NoteHpo 
                    on NOTEEVENTS.ROW_ID = Inferred_NoteHpo.NOTEEVENT_ROW_ID
                )
            SELECT SUBJECT_ID, HADM_ID, MAP_TO, COUNT(*) AS OCCURRANCE, 1 AS dummy
            FROM abnorm 
            GROUP BY SUBJECT_ID, HADM_ID, MAP_TO
        ''')

    else:
        cursor.execute('''
            CREATE TEMPORARY TABLE IF NOT EXISTS JAX_p_text
            WITH abnorm AS (
                SELECT
                    NOTEEVENTS.SUBJECT_ID, NOTEEVENTS.HADM_ID, NoteHpoClinPhen.MAP_TO
                FROM 
                    NOTEEVENTS 
                JOIN NoteHpoClinPhen 
                    on NOTEEVENTS.ROW_ID = NoteHpoClinPhen.NOTES_ROW_ID)
            SELECT SUBJECT_ID, HADM_ID, MAP_TO
            FROM abnorm 
            GROUP BY SUBJECT_ID, HADM_ID, MAP_TO, COUNT(*) AS OCCURRANCE, 1 AS dummy
        ''')


def indexTextHpoProfile():
    """
    Create indeces to speed up query
    """
    # _idx01 is unnecessary if _idx3 exists
    # cursor.execute('CREATE INDEX JAX_textHpoProfile_idx01 ON JAX_textHpoProfile (SUBJECT_ID, HADM_ID)')
    cursor.execute(
        'CREATE INDEX JAX_textHpoProfile_idx02 ON JAX_textHpoProfile (MAP_TO);')
    cursor.execute(
        'CREATE INDEX JAX_textHpoProfile_idx03 ON JAX_textHpoProfile (SUBJECT_ID, HADM_ID, MAP_TO)')
    cursor.execute(
        'CREATE INDEX JAX_textHpoProfile_idx04 ON JAX_textHpoProfile (OCCURRANCE)')


def labHpoProfile(include_inferred=True):
    """
    Set up a table for lab tests-derived phenotypes. By default,
    also include phenotypes that are inferred from direct mapping.
    Similar to textHpoProfile, this could be created as a perminent table.
    """
    cursor.execute('''DROP TEMPORARY TABLE IF EXISTS JAX_labHpoProfile''')
    if include_inferred:
        cursor.execute('''
            CREATE TEMPORARY TABLE IF NOT EXISTS JAX_labHpoProfile
            WITH abnorm AS (
                SELECT
                    LABEVENTS.SUBJECT_ID, LABEVENTS.HADM_ID, LabHpo.MAP_TO
                FROM 
                    LABEVENTS 
                JOIN LabHpo on LABEVENTS.ROW_ID = LabHpo.ROW_ID
                WHERE LabHpo.NEGATED = 'F'

                UNION ALL

                SELECT 
                    LABEVENTS.SUBJECT_ID, LABEVENTS.HADM_ID, INFERRED_LABHPO.INFERRED_TO AS MAP_TO 
                FROM 
                    INFERRED_LABHPO 
                JOIN 
                    LABEVENTS ON INFERRED_LABHPO.LABEVENT_ROW_ID = LABEVENTS.ROW_ID
                )
            SELECT SUBJECT_ID, HADM_ID, MAP_TO, COUNT(*) AS OCCURRANCE, 1 AS dummy
            FROM abnorm 
            GROUP BY SUBJECT_ID, HADM_ID, MAP_TO
        ''')
    else:
        cursor.execute('''
            CREATE TEMPORARY TABLE IF NOT EXISTS JAX_labHpoProfile
            WITH abnorm AS (
                SELECT
                    LABEVENTS.SUBJECT_ID, LABEVENTS.HADM_ID, LabHpo.MAP_TO
                FROM 
                    LABEVENTS 
                JOIN LabHpo on LABEVENTS.ROW_ID = LabHpo.ROW_ID
                WHERE LabHpo.NEGATED = 'F')
            SELECT SUBJECT_ID, HADM_ID, MAP_TO, COUNT(*) AS OCCURRANCE, 1 AS dummy
            FROM abnorm 
            GROUP BY SUBJECT_ID, HADM_ID, MAP_TO
        ''')


def indexLabHpoProfile():
    # _idx01 is not necessary if _idx3 exists
    # cursor.execute('CREATE INDEX JAX_labHpoProfile_idx01 ON JAX_labHpoProfile (SUBJECT_ID, HADM_ID)')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx02 ON JAX_labHpoProfile (MAP_TO);')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx03 ON JAX_labHpoProfile (SUBJECT_ID, HADM_ID, MAP_TO)')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx04 ON JAX_labHpoProfile (OCCURRANCE)')


def rankICD():
    """
    Rank frequently seen ICD-9 codes (first three or four digits) among encounters of interest.
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_diagFrequencyRank')
    cursor.execute("""
        CREATE TEMPORARY TABLE IF NOT EXISTS JAX_diagFrequencyRank
        WITH JAX_temp_diag AS (
            SELECT DISTINCT SUBJECT_ID, HADM_ID, 
                CASE 
                    WHEN(ICD9_CODE LIKE 'V%') THEN SUBSTRING(ICD9_CODE, 1, 3) 
                    WHEN(ICD9_CODE LIKE 'E%') THEN SUBSTRING(ICD9_CODE, 1, 4) 
                ELSE 
                    SUBSTRING(ICD9_CODE, 1, 3) END AS ICD9_CODE 
            FROM JAX_diagnosisProfile)
        SELECT 
            ICD9_CODE, COUNT(*) AS N
        FROM
            JAX_temp_diag
        GROUP BY 
            ICD9_CODE
        ORDER BY N
        DESC
        """)


def rankHpoFromText(diagnosis, hpo_min_occurrence_per_encounter):
    """
    Rank frequently seen phenotypes (HPO term) from text mining among
    encounters of interest.
    An encounter may have multiple occurrences of a phenotype term. A
    phenotype is called if its occurrence
    meets a minimum threshold.
    :param hpo_min_occurrence_per_encounter: threshold for a phenotype
    abnormality to be called. Usually use 1.
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_textHpoFrequencyRank')
    cursor.execute('''
        CREATE TEMPORARY TABLE JAX_textHpoFrequencyRank            
        WITH pd AS(
            SELECT 
                JAX_textHpoProfile.*
            FROM 
                JAX_textHpoProfile 
            JOIN (
                SELECT 
                    DISTINCT SUBJECT_ID, HADM_ID
                FROM 
                    JAX_diagnosisProfile 
                WHERE 
                    ICD9_CODE LIKE '{}%') AS d
            ON 
                JAX_textHpoProfile.SUBJECT_ID = d.SUBJECT_ID AND JAX_textHpoProfile.HADM_ID = d.HADM_ID
            WHERE 
                OCCURRANCE >= {})
        SELECT 
            MAP_TO, COUNT(*) AS N, 1 AS PHENOTYPE
        FROM pd
        GROUP BY MAP_TO
        ORDER BY N DESC'''.format(diagnosis,
                                  hpo_min_occurrence_per_encounter))


def rankHpoFromLab(diagnosis, hpo_min_occurrence_per_encounter):
    """
    Rank frequently seen phenotypes (HPO term) from lab texts among
    encounters of interest.
    An encounter may have multiple occurrances of a phenotype term, such as
    from lab tests that are frequently ordered.
    A phenotype is called if its occurrance meets a minimum threshold.
    @param hpo_min_occurrence_per_encounter: threshold for a phenotype
    abnormality to be called.
    For example, if the parameter is set to 3, HP:0002153 Hyperkalemia is
    assigned iff three or more lab tests return higher than normal values
    for blood potassium concentrations
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_labHpoFrequencyRank')
    cursor.execute('''
        CREATE TEMPORARY TABLE JAX_labHpoFrequencyRank            
        WITH pd AS(
            SELECT 
                JAX_labHpoProfile.*
            FROM 
                JAX_labHpoProfile 
            JOIN (
                SELECT 
                    DISTINCT SUBJECT_ID, HADM_ID
                FROM 
                    JAX_diagnosisProfile 
                WHERE 
                    ICD9_CODE LIKE '{}%') AS d
            ON 
                JAX_labHpoProfile.SUBJECT_ID = d.SUBJECT_ID AND 
                JAX_labHpoProfile.HADM_ID = d.HADM_ID
            WHERE
                OCCURRANCE >= {})
        SELECT 
            MAP_TO, COUNT(*) AS N, 1 AS PHENOTYPE
        FROM pd
        GROUP BY MAP_TO
        ORDER BY N DESC'''.format(diagnosis,
                                  hpo_min_occurrence_per_encounter))


def createDiagnosisTable(diagnosis, primary_diagnosis_only):
    """
    Create a temporary table JAX_mf_diag. For encounters of interest,
    assign 0 or 1 to each encouter whether a diagnosis is observed.
    @param diagnosis: diagnosis code. An encounter is considered to be 1 if
    same or more detailed code is called.
    :param primary_diagnosis_only: an encounter may be associated with one
    primary diagnosis and many secondary ones.
    if value is set true, only primary diagnosis counts.
    """
    cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag')
    if primary_diagnosis_only:
        limit = 'AND SEQ_NUM=1'
    else:
        limit = ''
    cursor.execute('''
        CREATE TEMPORARY TABLE IF NOT EXISTS JAX_mf_diag 
        WITH 
            d AS (
                SELECT 
                    DISTINCT SUBJECT_ID, HADM_ID, '1' AS DIAGNOSIS
                FROM 
                    JAX_diagnosisProfile 
                WHERE ICD9_CODE LIKE '{}%' {})
            -- This is encounters with positive diagnosis

        SELECT 
            DISTINCT a.SUBJECT_ID, a.HADM_ID, 
            IF(d.DIAGNOSIS IS NULL, '0', '1') AS DIAGNOSIS
        FROM 
            JAX_encounterOfInterest AS a
        LEFT JOIN
            d ON a.SUBJECT_ID = d.SUBJECT_ID AND a.HADM_ID = d.HADM_ID       
        /* -- This is the first join for diagnosis (0, or 1) */    
        '''.format(diagnosis, limit))
    cursor.execute(
        'CREATE INDEX JAX_mf_diag_idx01 ON JAX_mf_diag (SUBJECT_ID, HADM_ID)')


def initTables(debug=False):
    """
    This combines LabHpo and Inferred_LabHpo, and combines TextHpo and
    Inferred_TextHpo.
    Only need to run once. For efficiency consideration, the tables can also
    be created as permanent.
    It is time-consuming, so call it with caution.
    """
    # init textHpoProfile and index it
    # I created perminant tables to save time; other users should enable them
    # textHpoProfile(include_inferred=True, threshold=1)
    # indexTextHpoProfile()
    # init labHpoProfile and index it
    # labHpoProfile(threshold=1, include_inferred=True, force_update=True)
    # indexLabHpoProfile()

    # define encounters to analyze
    encounterOfInterest(debug)
    indexEncounterOfInterest()
    # init diagnosisProfile
    diagnosisProfile()


def indexDiagnosisTable():
    cursor.execute(
        "ALTER TABLE JAX_mf_diag ADD COLUMN ROW_ID INT AUTO_INCREMENT PRIMARY KEY;")


def batch_query(start_index,
                end_index,
                textHpo_occurrence_min,
                labHpo_occurrence_min,
                textHpo_threshold_min,
                textHpo_threshold_max,
                labHpo_threshold_min,
                labHpo_threshold_max):
    """
    Queries databases in small batches, return diagnosis values, phenotypes
    from text data and phenotypes from lab data.
    :param start_index: minimum row_id
    :param end_index: maximum row_id
    :param textHpo_occurrence_min: minimum occurrances of a phenotype from
    text data for it to be called in one encounter
    :param labHpo_occurrance_max: maximum occurrances of a phenotype from
    lab tests for it to be called in one encounter
    :param textHpo_threshold_min: minimum number of encounters of a
    phenotypes from text data for it to be analyzed
    :param textHpo_threshold_max: maximum number of encounters of a
    phenotypes from text data for it to be analyzed
    :param labHpo_threshold_min: minimum number of encounters of a phenotype
    from lab tests for it to be analyzed
    :param labHpo_threshold_max: maximum number of encounters of a phenotype
    from lab tests for it to be analyzed
    """
    diagnosisVector = pd.read_sql_query('''
        SELECT * FROM JAX_mf_diag WHERE ROW_ID BETWEEN {} AND {}
    '''.format(start_index, end_index), mydb)

    textHpoFlat = pd.read_sql_query('''
        WITH encounters AS (
            SELECT SUBJECT_ID, HADM_ID
            FROM JAX_mf_diag 
            WHERE ROW_ID BETWEEN {} AND {}
        ), 
        textHpoOfInterest AS (
            SELECT MAP_TO 
            FROM JAX_textHpoFrequencyRank 
            WHERE N BETWEEN {} AND {}
        ), 
        joint as (
            SELECT *
            FROM encounters 
            JOIN textHpoOfInterest),
        JAX_textHpoProfile_filtered AS (
            SELECT * 
            FROM JAX_textHpoProfile 
            WHERE OCCURRANCE >= {}
        )

        SELECT L.SUBJECT_ID, L.HADM_ID, L.MAP_TO, IF(R.dummy IS NULL, 0, 1) AS VALUE
        FROM joint as L
        LEFT JOIN 
        JAX_textHpoProfile_filtered AS R
        ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.MAP_TO = R.MAP_TO  
    '''.format(start_index, end_index, textHpo_threshold_min,
               textHpo_threshold_max, textHpo_occurrence_min), mydb)

    labHpoFlat = pd.read_sql_query('''
        WITH encounters AS (
            SELECT SUBJECT_ID, HADM_ID
            FROM JAX_mf_diag 
            WHERE ROW_ID BETWEEN {} AND {}
        ), 
        labHpoOfInterest AS (
            SELECT MAP_TO 
            FROM JAX_labHpoFrequencyRank 
            WHERE N BETWEEN {} AND {}
        ), 
        joint as (
            SELECT *
            FROM encounters 
            JOIN labHpoOfInterest),
        JAX_labHpoProfile_filtered AS (
            SELECT * 
            FROM JAX_labHpoProfile 
            WHERE OCCURRANCE >= {}
        )

        SELECT L.SUBJECT_ID, L.HADM_ID, L.MAP_TO, IF(R.dummy IS NULL, 0, 1) AS VALUE
        FROM joint as L
        LEFT JOIN 
        JAX_labHpoProfile_filtered AS R
        ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.MAP_TO = R.MAP_TO
    '''.format(start_index, end_index, labHpo_threshold_min,
               labHpo_threshold_max, labHpo_occurrence_min), mydb)

    return diagnosisVector, textHpoFlat, labHpoFlat


def summarize_diagnosis_textHpo_labHpo(primary_diagnosis_only,
                                       textHpo_occurrance_min,
                                       labHpo_occurrance_min,
                                       diagnosis_threshold_min,
                                       textHpo_threshold_min,
                                       textHpo_threshold_max,
                                       labHpo_threshold_min,
                                       labHpo_threshold_max,
                                       disease_of_interest,
                                       logger):
    """
    Iterate database to get summary statistics. For each disease of
    interest, automatically determine a list of phenotypes derived from labs
    (labHpo) and a list of phenotypes from text mining (textHpo). For each
    pair of phenotypes, count the number of encounters according to whether
    the phenotypes and diagnosis are observated.
    :param primary_diagnosis_only: only primary diagnosis is analyzed
    :param textHpo_occurrance_min: minimum occurrances of a phenotype from
    text data for it to be called in one encounter
    :param labHpo_occurrance_max: maximum occurrances of a phenotype from
    lab tests for it to be called in one encounter
    :param textHpo_threshold_min: minimum number of encounters of a
    phenotypes from text data for it to be analyzed
    :param textHpo_threshold_max: maximum number of encounters of a
    phenotypes from text data for it to be analyzed
    :param labHpo_threshold_min: minimum number of encounters of a phenotype
    from lab tests for it to be analyzed
    :param labHpo_threshold_max: maximum number of encounters of a phenotype
    from lab tests for it to be analyzed
    :param disease_of_interest: either set to "calculated", or a list of
    ICD-9 codes (get all possible codes from temp table JAX_diagFrequencyRank)
    :param logger: logger for logging

    :return: three dictionaries of summary statistics, of which the keys are
    diagnosis codes and the values are instances of the SummaryXYz class.
    First dictionary, X (a list of phenotype variables) are from textHpo and
    Y are from labHpo;
    Secondary dictionary, all terms in X, Y are from textHpo;
    Third dictionary, all terms in X, Y are all from labHpo. Note that terms
    in X and Y are calculated separately for each diagnosis and may be different.
    """
    logger.info('starting iterate_in_batch()')
    batch_size = 100

    # define a set of diseases that we want to analyze
    rankICD()

    if disease_of_interest == 'calculated':
        diseaseOfInterest = pd.read_sql_query(
            "SELECT * FROM JAX_diagFrequencyRank WHERE N > {}".format(
                diagnosis_threshold_min), mydb).ICD9_CODE.values
    elif isinstance(disease_of_interest, list) and len(disease_of_interest) > 0:
        # disable the following line to analyze all diseases of interest
        # diseaseOfInterest = ['428', '584', '038', '493']
        diseaseOfInterest = disease_of_interest
    else:
        raise RuntimeError
    logger.info('diagnosis of interest: {}'.format(len(diseaseOfInterest)))

    summaries_diag_textHpo_labHpo = {}
    summaries_diag_textHpo_textHpo = {}
    summaries_diag_labHpo_labHpo = {}

    pbar = tqdm(total=len(diseaseOfInterest))
    for diagnosis in diseaseOfInterest:
        logger.info("start analyzing disease {}".format(diagnosis))

        logger.info(".......assigning values of diagnosis")
        # assign each encounter whether a diagnosis code is observed
        # create a table j1 (joint 1)
        createDiagnosisTable(diagnosis, primary_diagnosis_only)
        indexDiagnosisTable()
        # for every diagnosis, find phenotypes of interest to look at from radiology reports
        # for every diagnosis, find phenotypes of interest to look at from laboratory tests
        rankHpoFromText(diagnosis, textHpo_occurrance_min)
        rankHpoFromLab(diagnosis, labHpo_occurrance_min)
        logger.info("..............diagnosis values found")

        textHpoOfInterest = pd.read_sql_query(
            "SELECT * FROM JAX_textHpoFrequencyRank WHERE N BETWEEN {} AND {}".format(
                textHpo_threshold_min, textHpo_threshold_max),
            mydb).MAP_TO.values
        labHpoOfInterest = pd.read_sql_query(
            "SELECT * FROM JAX_labHpoFrequencyRank WHERE N BETWEEN {} AND {}".format(
                labHpo_threshold_min, labHpo_threshold_max), mydb).MAP_TO.values
        logger.info("TextHpo of interest established, size: {}".format(
            len(textHpoOfInterest)))
        logger.info("LabHpo of interest established, size: {}".format(
            len(labHpoOfInterest)))

        ## find the start and end ROW_ID for patient*encounter
        ADM_ID_START, ADM_ID_END = pd.read_sql_query(
            'SELECT MIN(ROW_ID) AS min, MAX(ROW_ID) AS max FROM JAX_mf_diag',
            mydb).iloc[0]
        batch_N = ADM_ID_END - ADM_ID_START + 1
        TOTAL_BATCH = math.ceil(batch_N / batch_size)  # total number of batches

        summaries_diag_textHpo_labHpo[diagnosis] = mf.SummaryXYz(
            textHpoOfInterest, labHpoOfInterest, diagnosis)
        summaries_diag_textHpo_textHpo[diagnosis] = mf.SummaryXYz(
            textHpoOfInterest, textHpoOfInterest, diagnosis)
        summaries_diag_labHpo_labHpo[diagnosis] = mf.SummaryXYz(
            labHpoOfInterest, labHpoOfInterest, diagnosis)

        logger.info('starting batch queries for {}'.format(diagnosis))
        for i in np.arange(TOTAL_BATCH):
            start_index = i * batch_size + ADM_ID_START
            if i < TOTAL_BATCH - 1:
                end_index = start_index + batch_size - 1
            else:
                end_index = batch_N

            diagnosisFlat, textHpoFlat, labHpoFlat = batch_query(start_index,
                                                                 end_index,
                                                                 textHpo_occurrance_min,
                                                                 labHpo_occurrance_min,
                                                                 textHpo_threshold_min,
                                                                 textHpo_threshold_max,
                                                                 labHpo_threshold_min,
                                                                 labHpo_threshold_max)

            batch_size_actual = len(diagnosisFlat)
            textHpoOfInterest_size = len(textHpoOfInterest)
            labHpoOfInterest_size = len(labHpoOfInterest)
            assert (
                len(textHpoFlat) == batch_size_actual * textHpoOfInterest_size)
            assert (
                len(labHpoFlat) == batch_size_actual * labHpoOfInterest_size)

            if batch_size_actual > 0:
                diagnosisVector = diagnosisFlat.DIAGNOSIS.values.astype(int)
                # reformat the flat vector into N x M matrix, N is batch size,
                # i.e. number of encounters, M is the length of HPO terms
                textHpoMatrix = textHpoFlat.VALUE.values.astype(int).reshape(
                    [batch_size_actual, textHpoOfInterest_size], order='F')
                labHpoMatrix = labHpoFlat.VALUE.values.astype(int).reshape(
                    [batch_size_actual, labHpoOfInterest_size], order='F')
                # check the matrix formatting is correct
                # disable the following 4 lines to speed things up
                textHpoLabelsMatrix = textHpoFlat.MAP_TO.values.reshape(
                    [batch_size_actual, textHpoOfInterest_size], order='F')
                labHpoLabelsMatrix = labHpoFlat.MAP_TO.values.reshape(
                    [batch_size_actual, labHpoOfInterest_size], order='F')
                assert (textHpoLabelsMatrix[0, :] == textHpoOfInterest).all()
                assert (labHpoLabelsMatrix[0, :] == labHpoOfInterest).all()
                if i % 100 == 0:
                    logger.info(
                        'new batch: start_index={}, end_index={}, '
                        'batch_size= {}, textHpo_size = {}, labHpo_size = {}'.
                            format(start_index, end_index, batch_size_actual,
                                   textHpoMatrix.shape[1],
                                   labHpoMatrix.shape[1]))
                summaries_diag_textHpo_labHpo[diagnosis].add_batch(
                    textHpoMatrix, labHpoMatrix, diagnosisVector)
                summaries_diag_textHpo_textHpo[diagnosis].add_batch(
                    textHpoMatrix, textHpoMatrix, diagnosisVector)
                summaries_diag_labHpo_labHpo[diagnosis].add_batch(
                    labHpoMatrix, labHpoMatrix, diagnosisVector)

        pbar.update(1)

    pbar.close()

    return summaries_diag_textHpo_labHpo, summaries_diag_textHpo_textHpo, \
           summaries_diag_labHpo_labHpo


def mf_regardless_of_diseases():
    pass


def mf_regarding_diseases(mode):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    primary_diagnosis_only = config['Analysis'][mode].getboolean('primary_diagnosis_only')

    if mode == 'test':
        # 1. build the temp tables for Lab converted HPO, Text convert HPO
        # Read the comments within the method!
        initTables(debug=True)

        # 2. iterate throw the dataset
        primary_diagnosis_only = True
        diagnosis_threshold_min = 5
        textHpo_occurrance_min, labHpo_occurrance_min = 1, 3
        textHpo_threshold_min, textHpo_threshold_max = 7, 100
        labHpo_threshold_min, labHpo_threshold_max = 7, 100
        disease_of_interest = ['428', '584', '038', '493', '*']

        summaries_diag_textHpo_labHpo, \
        summaries_diag_textHpo_textHpo, \
        summaries_diag_labHpo_labHpo = summarize_diagnosis_textHpo_labHpo(
            primary_diagnosis_only, textHpo_occurrance_min,
            labHpo_occurrance_min,
            diagnosis_threshold_min, textHpo_threshold_min,
            textHpo_threshold_max,
            labHpo_threshold_min, labHpo_threshold_max, disease_of_interest,
            logger)
        return 0

    # how to run this
    # Again, it take either too long or too much memory space to run
    logger = logging.getLogger()
    logger.setLevel(logging.WARN)

    # 1. build the temp tables for Lab converted HPO, Text convert HPO
    # Read the comments within the method!
    initTables(debug=False)

    # 2. iterate throw the dataset
    primary_diagnosis_only = True
    diagnosis_threshold_min = 3000
    textHpo_threshold_min, textHpo_threshold_max = 500, 100000
    labHpo_threshold_min, labHpo_threshold_max = 1000, 100000
    textHpo_occurrance_min, labHpo_occurrance_min = 1, 3
    disease_of_interest = ['428', '584', '038', '493']

    summaries_diag_textHpo_labHpo, \
    summaries_diag_textHpo_textHpo, \
    summaries_diag_labHpo_labHpo = summarize_diagnosis_textHpo_labHpo(
        primary_diagnosis_only, textHpo_occurrance_min,
        labHpo_occurrance_min, diagnosis_threshold_min,
        textHpo_threshold_min, textHpo_threshold_max, labHpo_threshold_min,
        labHpo_threshold_max, disease_of_interest, logger)

    if primary_diagnosis_only:
        fName_diag_textHpo_labHpo = '../../../data/mf_regarding_diseases/primary_only/summaries_diagnosis_textHpo_labHpo.obj'
        fName_diag_textHpo_textHpo = '../../../data/mf_regarding_diseases/primary_only/summaries_diagnosis_textHpo_textHpo.obj'
        fName_diag_labHpo_labHpo = '../../../data/mf_regarding_diseases/primary_only/summaries_diagnosis_labHpo_labHpo.obj'
    else:
        fName_diag_textHpo_labHpo = '../../../data/mf_regarding_diseases/primary_and_secondary/summaries_diagnosis_textHpo_labHpo.obj'
        fName_diag_textHpo_textHpo = '../../../data/mf_regarding_diseases/primary_and_secondary/summaries_diagnosis_textHpo_textHpo.obj'
        fName_diag_labHpo_labHpo = '../../../data/mf_regarding_diseases/primary_and_secondary/summaries_diagnosis_labHpo_labHpo.obj'

    with open(fName_diag_textHpo_labHpo, 'wb') as f:
        pickle.dump(summaries_diag_textHpo_labHpo, f)
    with open(fName_diag_textHpo_textHpo, 'wb') as f:
        pickle.dump(summaries_diag_textHpo_textHpo, f)
    with open(fName_diag_labHpo_labHpo, 'wb') as f:
        pickle.dump(summaries_diag_labHpo_labHpo, f)


def run():
    print(pd.read_sql_query("SELECT * FROM LABEVENTS LIMIT 5;", mydb))


if __name__ == '__main__':
    # mf_regarding_diseases('test')
    print (config['Analysis']['disease_of_interest'])
    print(config['Analysis']['regarding_diagnosis.primary_diagnosis_only'])
