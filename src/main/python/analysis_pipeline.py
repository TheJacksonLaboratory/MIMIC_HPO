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
import yaml

# load yaml configuration file
with open('analysisConfig.yaml', 'r') as yaml_file:
    config = yaml.load(yaml_file)

base_dir = config['base_dir']
hpo_obo_path = config['hp.obo.path']
hpo = Ontology(hpo_obo_path)

# set up MySql connection
host = config['database']['host']
user = config['database']['user']
password = config['database']['password']
database = config['database']['database']

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
    # cursor.execute('CREATE INDEX JAX_textHpoProfile_idx01 ON
    # JAX_textHpoProfile (SUBJECT_ID, HADM_ID)')
    cursor.execute(
        'CREATE INDEX JAX_textHpoProfile_idx02 ON JAX_textHpoProfile (MAP_TO);')
    cursor.execute(
        'CREATE INDEX JAX_textHpoProfile_idx03 ON JAX_textHpoProfile ('
        'SUBJECT_ID, HADM_ID, MAP_TO)')
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
                    LABEVENTS.SUBJECT_ID, 
                    LABEVENTS.HADM_ID, 
                    INFERRED_LABHPO.INFERRED_TO AS MAP_TO 
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
    # cursor.execute('CREATE INDEX JAX_labHpoProfile_idx01 ON
    # JAX_labHpoProfile (SUBJECT_ID, HADM_ID)')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx02 ON JAX_labHpoProfile (MAP_TO);')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx03 ON JAX_labHpoProfile ('
        'SUBJECT_ID, HADM_ID, MAP_TO)')
    cursor.execute(
        'CREATE INDEX JAX_labHpoProfile_idx04 ON JAX_labHpoProfile (OCCURRANCE)')


def rankICD():
    """
    Rank frequently seen ICD-9 codes (first three or four digits) among
    encounters of interest.
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
                JAX_textHpoProfile.SUBJECT_ID = d.SUBJECT_ID AND 
                JAX_textHpoProfile.HADM_ID = d.HADM_ID
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


###############################################################################
# script for calculating the mutual information regardless of diseases        #
###############################################################################

def batch_query_lab_text(start_index, end_index, textHpo_occurrance_min,
                         labHpo_occurrance_min, textHpo_min, textHpo_max,
                         labHpo_min, labHpo_max):
    textHpo_flat = pd.read_sql_query('''
        WITH encounters AS (
                SELECT *
                FROM JAX_encounterOfInterest
                WHERE ROW_ID BETWEEN {} AND {}),
            phenotypes AS (
                SELECT MAP_TO
                FROM JAX_textHpoFrequencyRank
                WHERE N BETWEEN {} AND {}
            ), 
            temp AS (
                SELECT * 
                FROM encounters 
                JOIN phenotypes)

            SELECT L.SUBJECT_ID, L.HADM_ID, L.MAP_TO AS PHEN_TEXT, IF(R.dummy IS NULL, 0, 1) AS PHEN_TEXT_VALUE
            FROM temp AS L
            LEFT JOIN 
                (SELECT * FROM JAX_textHpoProfile WHERE OCCURRANCE >= {}) AS R
            ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.MAP_TO = R.MAP_TO
        '''.format(start_index, end_index, textHpo_min, textHpo_max,
                   textHpo_occurrance_min), mydb)

    labHpo_flat = pd.read_sql_query('''
        WITH encounters AS (
                SELECT *
                FROM JAX_encounterOfInterest
                WHERE ROW_ID BETWEEN {} AND {}),
            phenotypes AS (
                SELECT MAP_TO
                FROM JAX_labHpoFrequencyRank
                WHERE N BETWEEN {} AND {}
            ), 
            temp AS (
                SELECT * 
                FROM encounters 
                JOIN phenotypes)

            SELECT L.SUBJECT_ID, L.HADM_ID, L.MAP_TO AS PHEN_LAB, IF(R.dummy IS NULL, 0, 1) AS PHEN_LAB_VALUE
            FROM temp AS L
            LEFT JOIN 
                (SELECT * FROM JAX_labHpoProfile WHERE OCCURRANCE >= {}) AS R
            ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.MAP_TO = R.MAP_TO
        '''.format(start_index, end_index, labHpo_min, labHpo_max,
                   labHpo_occurrance_min), mydb)

    return textHpo_flat, labHpo_flat


def summary_textHpo_labHpo(batch_size, textHpo_occurrance_min,
                           labHpo_occurrance_min, textHpo_threshold_min,
                           textHpo_threshold_max, labHpo_threshold_min,
                           labHpo_threshold_max):
    textHpoOfInterest = pd.read_sql_query(
        "SELECT * FROM JAX_textHpoFrequencyRank WHERE N BETWEEN {} AND {}".format(
            textHpo_threshold_min, textHpo_threshold_max), mydb).MAP_TO.values
    labHpoOfInterest = pd.read_sql_query(
        "SELECT * FROM JAX_labHpoFrequencyRank WHERE N BETWEEN {} AND {}".format(
            labHpo_threshold_min, labHpo_threshold_max), mydb).MAP_TO.values
    M1 = len(textHpoOfInterest)
    M2 = len(labHpoOfInterest)

    summary_rad_lab = mf.SummaryXY(textHpoOfInterest, labHpoOfInterest)
    summary_rad_rad = mf.SummaryXY(textHpoOfInterest, textHpoOfInterest)
    summary_lab_lab = mf.SummaryXY(labHpoOfInterest, labHpoOfInterest)

    ## find the start and end ROW_ID for patient*encounter

    ADM_ID_START, ADM_ID_END = pd.read_sql_query(
        'SELECT MIN(ROW_ID) AS min, MAX(ROW_ID) AS max FROM JAX_encounterOfInterest',
        mydb).iloc[0]
    batch_N = ADM_ID_END - ADM_ID_START + 1
    TOTAL_BATCH = math.ceil(batch_N / batch_size)  # total number of batches

    print('total batches: ' + str(batch_N))
    pbar = tqdm(total=TOTAL_BATCH)
    for i in np.arange(TOTAL_BATCH):
        start_index = i * batch_size + ADM_ID_START
        if i < TOTAL_BATCH - 1:
            end_index = start_index + batch_size - 1
        else:
            end_index = batch_N
        actual_batch_size = end_index - start_index + 1
        textHpo, labHpo = batch_query_lab_text(start_index, end_index,
                                               textHpo_occurrance_min,
                                               labHpo_occurrance_min,
                                               textHpo_threshold_min,
                                               textHpo_threshold_max,
                                               labHpo_threshold_min,
                                               labHpo_threshold_max)
        textHpo_matrix = textHpo.PHEN_TEXT_VALUE.values.astype(int).reshape(
            [actual_batch_size, M1], order='F')
        labHpo_matrix = labHpo.PHEN_LAB_VALUE.values.astype(int).reshape(
            [actual_batch_size, M2], order='F')
        summary_rad_lab.add_batch(textHpo_matrix, labHpo_matrix)
        summary_rad_rad.add_batch(textHpo_matrix, textHpo_matrix)
        summary_lab_lab.add_batch(labHpo_matrix, labHpo_matrix)
        pbar.update(1)

    pbar.close()

    return summary_rad_lab, summary_rad_rad, summary_lab_lab


def pipeline_calculate_summary_statistics_for_mf_regardless_of_diseases(test_mode):
    # prepare temp tables
    encounterOfInterest(debug=test_mode)
    indexEncounterOfInterest()
    diagnosisProfile()
    rankHpoFromText('', hpo_min_occurrence_per_encounter=1)
    rankHpoFromLab('', hpo_min_occurrence_per_encounter=3)

    # populate analysis parameters
    if test_mode:
        analysis_parameters = config['analysis-test']['regardless_of_diseases']
    else:
        analysis_parameters = config['analysis-prod']['regardless_of_diseases']
    batch_size = 100
    textHpo_occurrance_min = analysis_parameters['textHpo_occurrance_min']
    labHpo_occurrance_min = analysis_parameters['labHpo_occurrance_min']
    textHpo_threshold_min = analysis_parameters['textHpo_threshold_min']
    textHpo_threshold_max = analysis_parameters['textHpo_threshold_max']
    labHpo_threshold_min = analysis_parameters['labHpo_threshold_min']
    labHpo_threshold_max = analysis_parameters['labHpo_threshold_max']

    summary_rad_lab, summary_rad_rad, summary_lab_lab = summary_textHpo_labHpo(
        batch_size, textHpo_occurrance_min, labHpo_occurrance_min,
        textHpo_threshold_min, textHpo_threshold_max, labHpo_threshold_min,
        labHpo_threshold_max)

    # save files
    save_to_dir = os.path.join(base_dir, 'data', 'mf_regardless_of_diseases')
    if test_mode:
        save_to_dir = os.path.join(save_to_dir, 'test')
    if not os.path.exists(save_to_dir):
        os.mkdir(save_to_dir)

    fname_textHpo_labHpo = 'summary_textHpo_labHpo.obj'
    fname_textHpo_textHpo = 'summary_textHpo_textHpo.obj'
    fname_labHpo_labHpo = 'summary_labHpo_labHpo.obj'

    with open(os.path.join(save_to_dir, fname_textHpo_labHpo), 'wb') as file:
        pickle.dump(summary_rad_lab, file)

    with open(os.path.join(save_to_dir, fname_textHpo_textHpo), 'wb') as file:
        pickle.dump(summary_rad_rad, file)

    with open(os.path.join(save_to_dir, fname_labHpo_labHpo), 'wb') as file:
        pickle.dump(summary_lab_lab, file)


def mf_dataframe_regardless_of_diagnosis(p1_source, p2_source,
                                         hpo_term_map):
    summary_file_name = 'summary_{}_{}.obj'.format(p1_source, p2_source)
    summary_file_path = os.path.join(base_dir, 'data',
                                     'mf_regardless_of_diseases',
                                     summary_file_name)
    with open(summary_file_path, 'rb') as f:
        summary_statistics = pickle.load(f)

    # convert to a MutualInfoXY object from summary statistics
    mf_XY = mf.MutualInfoXY(summary_statistics)

    # get a dataframe
    df_mf_XY = mf_XY.mf_labeled()

    # label termid with names
    df_mf_XY['P1_label'] = np.array(
        [hpo_term_map.get(termid) for termid in df_mf_XY.P1])
    df_mf_XY['P2_label'] = np.array(
        [hpo_term_map.get(termid) for termid in df_mf_XY.P2])

    return df_mf_XY

def filter_mf_dataframe_regardless_of_diagnosis(df_mf_XY, hpo,
                                                remove_pairs_with_same_terms,
                                                remove_reflective_pairs,
                                                remove_pairs_with_dependency,
                                                sort_by='mf'):
    # remove pairs where P1, P2 are the same
    if remove_pairs_with_same_terms:
        df_mf_XY = df_mf_XY.loc[df_mf_XY.P1 != df_mf_XY.P2, :].reset_index(
            drop=True)

    # remove reflective pairs: (a, b) and (b, a) are considered reflective pairs
    # the method is to use string comparison: always require P1 <= P2
    if remove_reflective_pairs:
        df_mf_XY = df_mf_XY.loc[df_mf_XY.P1 <= df_mf_XY.P2, :].reset_index(
            drop=True)

    # remove pairs with dependency
    has_dependency = np.repeat(False, len(df_mf_XY))
    for i in np.arange(len(df_mf_XY)):
        x = df_mf_XY.P1[i]
        y = df_mf_XY.P2[i]
        has_dependency[i] = x != y and (
        hpo.exists_path(x, y) or hpo.exists_path(y, x))

    if remove_pairs_with_dependency:
        # when does two terms in a pair has dependency: different, but there is path from one to another
        df_mf_XY = df_mf_XY.loc[np.logical_not(has_dependency), :]

    df_mf_XY = df_mf_XY.sort_values(by=sort_by,
                                    ascending=False).reset_index(drop=True)

    return df_mf_XY

def save_mf_dataframe_regardless_of_diagnosis(df_mf_XY, p1_source,
                                              p2_source):
    # save to csv file
    output_file_name = 'mf_{}_{}.csv'.format(p1_source, p2_source)
    output_file_parent_dir = os.path.join(base_dir, 'data',
                                          'mf_regardless_of_diseases')
    if not os.path.exists(output_file_parent_dir):
        os.mkdir(output_file_parent_dir)
    output_file_path = os.path.join(base_dir, 'data',
                                    'mf_regardless_of_diseases',
                                    output_file_name)
    df_mf_XY.to_csv(output_file_path)

def pipeline_interpret_mf_regardless_of_diagnosis(p1_source, p2_source, hpo,
                                                  remove_pairs_with_same_terms,
                                                  remove_reflective_pairs,
                                                  remove_pairs_with_dependency):
    # step 1: make a labeled dataframe
    hpo_term_map = hpo.term_id_2_label_map()
    df_mf_XY = mf_dataframe_regardless_of_diagnosis(p1_source, p2_source,
                                                    hpo_term_map)
    # step 2: filter unnecessary rows
    df_mf_XY = filter_mf_dataframe_regardless_of_diagnosis(df_mf_XY, hpo,
                                                           remove_pairs_with_same_terms,
                                                           remove_reflective_pairs,
                                                           remove_pairs_with_dependency)
    # step 3: save to csv
    save_mf_dataframe_regardless_of_diagnosis(df_mf_XY, p1_source,
                                              p2_source)


###############################################################################
# script for calculating the mutual information regarding a disease           #
###############################################################################
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
        # for every diagnosis, find phenotypes of interest to look at from
        # radiology reports and laboratory tests
        rankHpoFromText(diagnosis, textHpo_occurrance_min)
        rankHpoFromLab(diagnosis, labHpo_occurrance_min)
        logger.info("..............diagnosis values found")

        textHpoOfInterest = pd.read_sql_query(
            "SELECT * FROM JAX_textHpoFrequencyRank WHERE N BETWEEN {} AND {}"
                .format(textHpo_threshold_min, textHpo_threshold_max),
            mydb).MAP_TO.values
        labHpoOfInterest = pd.read_sql_query(
            "SELECT * FROM JAX_labHpoFrequencyRank WHERE N BETWEEN {} AND {}"
                .format(labHpo_threshold_min, labHpo_threshold_max), mydb).MAP_TO.values
        logger.info("TextHpo of interest established, size: {}"
                    .format(len(textHpoOfInterest)))
        logger.info("LabHpo of interest established, size: {}"
                    .format(len(labHpoOfInterest)))

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

            diagnosisFlat, textHpoFlat, labHpoFlat = \
                batch_query(start_index,
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


def pipeline_calculate_summary_statistics_for_mf_regarding_diseases(test_mode):
    logger = logging.getLogger()
    if test_mode:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARN)

    # 1. build the temp tables for Lab converted HPO, Text convert HPO
    # Read the comments within the method!
    initTables(debug=test_mode)

    # 2. iterate throw the dataset
    ## populate analysis parameters
    if test_mode:
        analysis_parameters = config['analysis-test']['regarding_diagnosis']
    else:
        analysis_parameters = config['analysis-prod']['regarding_diagnosis']
    primary_diagnosis_only = analysis_parameters['primary_diagnosis_only']
    diagnosis_threshold_min = analysis_parameters['diagnosis_threshold_min']
    textHpo_occurrance_min = analysis_parameters['textHpo_occurrance_min']
    labHpo_occurrance_min = analysis_parameters['labHpo_occurrance_min']
    textHpo_threshold_min = analysis_parameters['textHpo_threshold_min']
    textHpo_threshold_max = analysis_parameters['textHpo_threshold_max']
    labHpo_threshold_min = analysis_parameters['labHpo_threshold_min']
    labHpo_threshold_max = analysis_parameters['labHpo_threshold_max']
    disease_of_interest = analysis_parameters['disease_of_interest']

    summaries_diag_textHpo_labHpo, \
    summaries_diag_textHpo_textHpo, \
    summaries_diag_labHpo_labHpo = summarize_diagnosis_textHpo_labHpo(
        primary_diagnosis_only, textHpo_occurrance_min,
        labHpo_occurrance_min,
        diagnosis_threshold_min, textHpo_threshold_min,
        textHpo_threshold_max,
        labHpo_threshold_min, labHpo_threshold_max, disease_of_interest,
        logger)

    # save to file
    diagnosis_dir = 'primary_only' if primary_diagnosis_only else \
        'primary_and_secondary'
    save_to_dir = os.path.join(base_dir, 'data', 'mf_regarding_diseases',
                               diagnosis_dir)
    if test_mode:
        save_to_dir = os.path.join(save_to_dir, 'test')
    if not os.path.exists(save_to_dir):
        os.mkdir(save_to_dir)

    fName_diag_textHpo_labHpo = 'summaries_diagnosis_textHpo_labHpo.obj'
    fName_diag_textHpo_textHpo = 'summaries_diagnosis_textHpo_textHpo.obj'
    fName_diag_labHpo_labHpo = 'summaries_diagnosis_labHpo_labHpo.obj'

    with open(os.path.join(save_to_dir, fName_diag_textHpo_labHpo),
              'wb') as f:
        pickle.dump(summaries_diag_textHpo_labHpo, f)
    with open(os.path.join(save_to_dir, fName_diag_textHpo_textHpo), 'wb') as f:
        pickle.dump(summaries_diag_textHpo_textHpo, f)
    with open(os.path.join(save_to_dir, fName_diag_labHpo_labHpo), 'wb') as f:
        pickle.dump(summaries_diag_labHpo_labHpo, f)


def summary_statistics_to_mutualInfoXY_z(p1_source, p2_source, primary_only,
                                         diag_code):
    if primary_only:
        diag_dir = "primary_only"
    else:
        diag_dir = "primary_and_secondary"

    summaries_file_name = 'summaries_diagnosis_{}_{}.obj'.format(p1_source,
                                                                 p2_source)
    summaries_file_path = os.path.join(base_dir, 'data',
                                       'mf_regarding_diseases', diag_dir,
                                       summaries_file_name)

    with open(summaries_file_path, 'rb') as f:
        summaries = pickle.load(f)

    summary_statistics_for_diag_code = summaries.get(diag_code)
    mutualInfoXYz = mf.MutualInfoXYz(summary_statistics_for_diag_code)

    return mutualInfoXYz


def mf_dataframes_regarding_diagnosis(mutualInfoXYz, **p_values):
    """
    @param p_values: output from simulation
    """
    assert isinstance(mutualInfoXYz, mf.MutualInfoXYz)
    # unpack p values
    p_mf_Xz = p_values.get('mf_Xz')
    p_mf_Yz = p_values.get('mf_Yz')
    p_mf_XY_z = p_values.get('mf_XY_z')
    p_mf_XY_given_z = p_values.get('mf_XY_given_z')
    p_synergy = p_values.get('synergy')
    p_mf_XY_omit_z = p_values.get('mf_XY_omit_z')

    X_labels, Y_labels = mutualInfoXYz.vars_labels.values()
    M1 = len(X_labels)
    M2 = len(Y_labels)

    mf_Xz = mutualInfoXYz.mutual_info_Xz()
    mf_Yz = mutualInfoXYz.mutual_info_Yz()

    # mutual information between single phenotypes and diagnosis
    df_mf_Xz = pd.DataFrame(data={'X': X_labels, 'mf_Xz': mf_Xz})
    df_mf_Yz = pd.DataFrame(data={'Y': Y_labels, 'mf_Yz': mf_Yz})
    # add p values
    df_mf_Xz['p_mf_Xz'] = p_mf_Xz if p_mf_Xz is not None else np.repeat(-1,
                                                                        M1)
    df_mf_Yz['p_mf_Yz'] = p_mf_Yz if p_mf_Yz is not None else np.repeat(-1,
                                                                        M2)

    # joint and conditional mutual information, and synergy
    mf_XY_z = mutualInfoXYz.mutual_info_XY_z()
    mf_XY_given_z = mutualInfoXYz.mutual_info_XY_given_z()
    mf_synergy = mutualInfoXYz.synergy_XY2z()

    # mutual information between phenotypes without considering diagnosis
    mf_XY_omit_z = mutualInfoXYz.mutual_info_XY_omit_z()

    # mutual information between phenotype pairs and diagnosis
    df_mf_XY_z = pd.DataFrame()
    df_mf_XY_z['X'] = np.repeat(X_labels, M2)
    df_mf_XY_z['Y'] = np.tile(Y_labels, [M1])
    df_mf_XY_z['mf_Xz'] = np.repeat(mf_Xz, M2)
    df_mf_XY_z['mf_Yz'] = np.tile(mf_Yz, [M1])
    df_mf_XY_z['mf_XY_z'] = mf_XY_z.flat
    df_mf_XY_z[
        'synergy'] = mf_synergy.flat  # synergy = mf_XY_z - mf_Xz - mf_Yz

    # mutual information between phenotypes after omiting diagnosis or conditioned on diagnosis
    df_mf_XY_z['mf_XY_omit_z'] = mf_XY_omit_z.flat
    df_mf_XY_z['mf_XY_given_z'] = mf_XY_given_z.flat

    # ratio of conditional mutual information / mutual information without considering diagnosis
    # synergy is also equal to mf_XY_given_z - mf_XY_omit_z
    # here we use ratio, which can be considered as an alternative of the above definition of synergy
    df_mf_XY_z['mf_ratio'] = df_mf_XY_z['mf_XY_given_z'] / df_mf_XY_z[
        'mf_XY_omit_z']

    # add p values; otherwise, assign -1
    df_mf_XY_z['p_mf_Xz'] = np.repeat(p_mf_Xz,
                                      M2) if p_mf_Xz is not None else np.repeat(
        -1, M1 * M2)
    df_mf_XY_z['p_mf_Yz'] = np.tile(p_mf_Yz, [
        M1]) if p_mf_Yz is not None else np.repeat(-1, M1 * M2)
    df_mf_XY_z[
        'p_mf_XY_z'] = p_mf_XY_z.flat if p_mf_XY_z is not None else np.repeat(
        -1, M1 * M2)
    df_mf_XY_z[
        'p_synergy'] = p_synergy.flat if p_synergy is not None else np.repeat(
        -1, M1 * M2)
    df_mf_XY_z[
        'p_mf_XY_omit_z'] = p_mf_XY_omit_z.flat if p_mf_XY_omit_z is not None else np.repeat(
        -1, M1 * M2)
    df_mf_XY_z[
        'p_mf_XY_given_z'] = p_mf_XY_given_z.flat if p_mf_XY_given_z is not None else np.repeat(
        -1, M1 * M2)

    # add raw counts: 8 additional columns
    joint_dist_keys = ['+++', '++-', '+-+', '+--', '-++', '-+-', '--+',
                       '---']
    joint_dist_values = mutualInfoXYz.m2.reshape([-1, 8]).astype(int)
    raw_counts = {joint_dist_keys[i]: joint_dist_values[:, i] for i in
                  np.arange(8)}
    df_mf_XY_z = df_mf_XY_z.assign(**raw_counts)
    df_mf_XY_z['sum'] = np.sum(joint_dist_values,
                               axis=-1)  # it's a constant for all rows

    return df_mf_Xz, df_mf_Yz, df_mf_XY_z


def rename_mf_dataframes(df_mf_Xz, df_mf_Yz, df_mf_XY_z):
    # map column names to more meaningful name for this context
    name_dict = {
        'X': 'P1',
        'Y': 'P2',
        'mf_Xz': 'mf_P1_diag',
        'mf_Yz': 'mf_P2_diag',
        'mf_XY_z': 'mf_P1P2_diag',
        'mf_XY_given_z': 'mf_P1P2_given_diag',
        'mf_XY_omit_z': 'mf_P1P2_omit_diag',
        'p_mf_XY_z': 'p_mf_P1P2_diag',
        'p_mf_XY_given_z': 'p_mf_P1P2_given_diag',
        'p_mf_XY_omit_z': 'p_mf_P1P2_omit_diag',
        'mf_Xz': 'mf_P1_diag',
        'mf_Yz': 'mf_P2_diag',
        'p_mf_Xz': 'p_mf_P1_diag',
        'p_mf_Yz': 'p_mf_P2_diag'
    }

    df_mf_Xz = df_mf_Xz.rename(columns=name_dict, errors='ignore')
    df_mf_Yz = df_mf_Yz.rename(columns=name_dict, errors='ignore')
    df_mf_XY_z = df_mf_XY_z.rename(columns=name_dict, errors='ignore')

    return df_mf_Xz, df_mf_Yz, df_mf_XY_z


def filter_mf_dataframe_regarding_diagnosis(df_mf_XY_z, hpo,
                                            remove_pairs_with_same_terms,
                                            remove_reflective_pairs,
                                            remove_pairs_with_dependency,
                                            sort_by='synergy'):
    # use the same method as the one defined above, except to sort by a different column
    return filter_mf_dataframe_regardless_of_diagnosis(df_mf_XY_z, hpo,
                                                       remove_pairs_with_same_terms,
                                                       remove_reflective_pairs,
                                                       remove_pairs_with_dependency,
                                                       sort_by)


def entropy(case, control):
    total = case + control
    h = -(case / total * np.log2(case / total) + control / total * np.log2(
        control / total))
    return h


def load_p_values(p1_source, p2_source, diag_code, primary_only):
    if primary_only:
        p_values_file_name = 'p_value_{}_{}_{}_{}.obj'.format(p1_source,
                                                              p2_source,
                                                              diag_code,
                                                              'primary_only')
    else:
        p_values_file_name = 'p_value_{}_{}_{}_{}.obj'.format(p1_source,
                                                              p2_source,
                                                              diag_code,
                                                              'primary_and_secondary')

    p_values_file_path = os.path.join(base_dir, 'data',
                                      'mf_regarding_diseases',
                                      'primary_only', diag_code,
                                      p_values_file_name)
    with open(p_values_file_path, 'rb') as f:
        p = pickle.load(f)
    return p


convert_to_percent = np.vectorize(lambda x: ' {:.2f}%'.format(x * 100))


def create_dirs_if_necessary(primary_only, diag_code):
    """
    Create necessary directories for the diagnosis type and diagnosis code.
    There should be the following directories in the repo:
    data -> mf_regarding_diseases -> primary_only or primary_and_secondary -> diagnosis_code
    """
    # create a data folder under the repo
    data_dir = os.path.join(base_dir, 'data')
    if not os.path.exists(data_dir):
        os.path.mkdir(data_dir)

    # create parent dir for all outputs related to mutual information in regarding to a disease
    mf_regarding_disease_dir = os.path.join(data_dir, 'mf_regarding_diseases')
    if not os.path.exists(mf_regarding_disease_dir):
        os.mkdir(mf_regarding_disease_dir)

    # create dir for the diagnosis type (primary_only or primary_and_secondary)
    if primary_only:
        diag_type = 'primary_only'
    else:
        diag_type = 'primary_and_secondary'
    diag_type_dir = os.path.join(mf_regarding_disease_dir, diag_type)
    if not os.path.exists(diag_type_dir):
        os.mkdir(diag_type_dir)

    # create dir for the disease
    diag_dir = os.path.join(diag_type_dir, diag_code)
    if not os.path.exists(diag_dir):
        os.mkdir(diag_dir)

    # create dir for cytoscape data
    cytoscape_dir = os.path.join(diag_dir, 'cytoscape')
    if not os.path.exists(cytoscape_dir):
        os.mkdir(cytoscape_dir)


def pipeline_interpret_mf_regarding_diagnosis(p1_source, p2_source, primary_only,
                                              diag_code, hpo,
                                              remove_pairs_with_same_terms,
                                              remove_reflective_pairs,
                                              remove_pairs_with_dependency,
                                              sort_by='synergy',
                                              percentile_for_cytoscape=0.01):
    # calculate mutual information from summary statistics
    mutualInfoXYz = summary_statistics_to_mutualInfoXY_z(p1_source, p2_source,
                                                         primary_only,
                                                         diag_code)
    # load p values (calculated from simulation on Helix)
    p_values = load_p_values(p1_source, p2_source, diag_code, primary_only)
    # create dataframes
    df_mf_Xz, df_mf_Yz, df_mf_XY_z = mf_dataframes_regarding_diagnosis(
        mutualInfoXYz, **p_values)
    # rename columns according to this medical context
    df_mf_Xz, df_mf_Yz, df_mf_XY_z = rename_mf_dataframes(df_mf_Xz, df_mf_Yz,
                                                          df_mf_XY_z)
    # label HPO term ids with their names
    hpo_term_map = hpo.term_id_2_label_map()
    df_mf_Xz['P1_label'] = [hpo_term_map.get(termid) for termid in df_mf_Xz.P1]
    df_mf_Yz['P2_label'] = [hpo_term_map.get(termid) for termid in df_mf_Yz.P2]
    df_mf_XY_z['P1_label'] = [hpo_term_map.get(termid) for termid in
                              df_mf_XY_z.P1]
    df_mf_XY_z['P2_label'] = [hpo_term_map.get(termid) for termid in
                              df_mf_XY_z.P2]
    # filter synergy dataframe
    df_mf_XY_z = filter_mf_dataframe_regarding_diagnosis(df_mf_XY_z, hpo,
                                                         remove_pairs_with_same_terms,
                                                         remove_reflective_pairs,
                                                         remove_pairs_with_dependency,
                                                         sort_by)
    # sort by desired columns
    df_mf_Xz = df_mf_Xz.sort_values(by='mf_P1_diag',
                                    ascending=False).reset_index(drop=True)
    df_mf_Yz = df_mf_Yz.sort_values(by='mf_P2_diag',
                                    ascending=False).reset_index(drop=True)
    df_mf_XY_z = df_mf_XY_z.sort_values(by=sort_by,
                                        ascending=False).reset_index(drop=True)

    # output to csv file
    # make sure the parent folders all exists
    create_dirs_if_necessary(primary_only, diag_code)
    # just save df_mf_XY_z_filtered as it contains data in df_mf_Xz and df_mf_Yz
    csv_file_name = 'df_synergy_{}_{}_{}.csv'.format(p1_source, p2_source,
                                                     diag_code)
    if primary_only:
        diag_dir = 'primary_only'
    else:
        diag_dir = 'primary_and_secondary'
    csv_parent_dir = os.path.join(base_dir, 'data', 'mf_regarding_diseases',
                                  diag_dir, diag_code)
    csv_file_path = os.path.join(csv_parent_dir, csv_file_name)

    df_mf_XY_z.to_csv(csv_file_path)

    # output cytoscape files
    # Note: only show a small fraction for cytoscape rendering
    percentile = percentile_for_cytoscape
    n = math.floor(len(df_mf_XY_z) * percentile)

    df_4_cytoscape = df_mf_XY_z \
        .assign(P1=lambda x: 'Rad_' + x['P1']) \
        .assign(P2=lambda x: 'Lab_' + x['P2']) \
        .head(n=n)

    cytoscape_dir = os.path.join(base_dir, 'data', 'mf_regarding_diseases',
                                 diag_dir, diag_code, 'cytoscape')
    # edges
    edges_path = os.path.join(cytoscape_dir,
                              'edges_{}_{}_{}.csv'.format(p1_source, p2_source,
                                                          diag_code))
    df_4_cytoscape.loc[:, ['P1', 'P2', 'synergy', 'p_synergy']].to_csv(
        edges_path)

    # nodes
    nodes = pd.DataFrame(
        data={'term_id': np.concatenate([df_4_cytoscape.P1, df_4_cytoscape.P2]),
              'term_label': np.concatenate(
                  [df_4_cytoscape.P1_label, df_4_cytoscape.P2_label]),
              'type': np.repeat(['Rad', 'Lab'],
                                len(df_4_cytoscape))}).drop_duplicates()
    nodes_path = os.path.join(cytoscape_dir,
                              'nodes_{}_{}_{}.csv'.format(p1_source, p2_source,
                                                          diag_code))
    nodes.to_csv(nodes_path)

    # return this one for html rendering
    return csv_parent_dir, csv_file_path


def pipeline_simulate_to_get_p_values(primary_only, diag_code, mock=True):
    if primary_only:
        diag_dir = 'primary_only'
    else:
        diag_dir = 'primary_and_secondary'

    # define the follow three lists
    # idea is to for each disease,
    # use the summary statistics, build empirical distributions, and then
    #  generate p values for observed numbers
    fname_summary_statistics = [
        'summaries_diagnosis_textHpo_labHpo.obj',
        'summaries_diagnosis_labHpo_labHpo.obj',
        'summaries_diagnosis_textHpo_textHpo.obj']
    empirical_dist_dirs = ['{}_textHpo_labHpo'.format(diag_code),
                           '{}_labHpo_labHpo'.format(diag_code),
                           '{}_textHpo_textHpo'.format(diag_code)]
    p_value_file_names = [
        'p_value_textHpo_labHpo_{}_{}.obj'.format(diag_code, diag_dir),
        'p_value_labHpo_labHpo_{}_{}.obj'.format(diag_code, diag_dir),
        'p_value_textHpo_textHpo_{}_{}.obj'.format(diag_code, diag_dir)]
    # then download p values files to the following directory
    p_dir = os.path.join(base_dir, 'data', 'mf_regarding_diseases',
                         diag_dir, diag_code)
    if not os.path.exists(p_dir):
        os.mkdir(p_dir)

    if not mock:
        # You need to run simulation codes on cluster, and then download the
        # p value file. follow the printed instructions
        for i in range(3):
            # first, run simulation command on Helix to get empirical
            # distributions of all metrics (e.g. mutual information, synergy
            # etc) IF everything is random
            simulation_script_header = '\n'.join([
                "#!/bin/bash",
                "#PBS -q batch",
                "#PBS -l nodes=1:ppn=4",
                "#PBS -l walltime=24:00:00",
                "#PBS -l mem=32gb",
                "#PBS -m a",
                "module load Anaconda/4.2.0-c",
                "source activate py3",
                "base_dir=/projects/robinson-lab/mimic-III/mf_simulations"])

            simulation_script_command = \
                "python ${{base_dir}}/python/syn_simu_runner.py " \
                "simulate -N 32 " \
                "-i ${{base_dir}}/input_dir/{diag_dir}/{summary_statistics} " \
                "-o ${{base_dir}}/simulation_output/{diag_dir}/{output_dir} " \
                "-cpu 4 -job_id ${{PBS_ARRAYID}} -disease {diag_code}"\
                    .format(diag_dir=diag_dir,
                            summary_statistics=fname_summary_statistics[i],
                            output_dir=empirical_dist_dirs[i],
                            diag_code=diag_code)
            complete_simulation_script = '\n'.join([simulation_script_header,
                                      simulation_script_command])
            print("\n\nsave the following to a file 'simulate.ssh', and run "
                  "'qsub -t 1-500 simulate.ssh' \n")
            print(complete_simulation_script)


            # then look up the empirical distributions and find the p value
            # of the observed value (likelihood that it could be more extreme
            #  than the observed numbers), and serialize to corresponding files
            estimate_p_header = '\n'.join([
                "#!/bin/bash",
                "#PBS -q batch",
                "#PBS -l nodes=1:ppn=1",
                "#PBS -l walltime=1:00:00"
                "#PBS -l mem=64gb",
                "#PBS -m a",
                "module load Anaconda/4.2.0-c",
                "source activate py3",
                "base_dir=/projects/robinson-lab/mimic-III/mf_simulations"])
            estimate_p_script_command = \
                "python ${{base_dir}}/python/syn_simu_runner.py " \
                "estimate " \
                "-i " \
                "${{base_dir}}/input_dir/{diag_dir}/{summary_statistics} " \
                "-dist ${{base_dir}}/simulation_output/{diag_dir}/{dist_dir} " \
                "-o ${{base_dir}}/p_values/{diag_dir}/{p_value_file} " \
                "-disease {diag_code}".format(diag_dir=diag_dir,
                                              summary_statistics=fname_summary_statistics[i],
                                              dist_dir=empirical_dist_dirs[i],
                                              diag_code=diag_code,
                                              p_value_file=p_value_file_names[i])
            complete_estimate_p_script = '\n'.join([estimate_p_header, estimate_p_script_command])
            print("\nafter the previous job is done, save the following "
                  "script as 'estimate.ssh' and submit with 'qsub "
                  "estimate.ssh'")
            print(complete_estimate_p_script)
            print("\ndownload the generated p value files and save them to {} "
                  "on local machine".format(p_dir))

    else:
        # fake p value file with an empty dictionary
        p = dict()

        for i in range(3):
            with open(os.path.join(p_dir, p_value_file_names[i]), 'wb') as \
                    p_value_file:
                pickle.dump(p, p_value_file)



################################################################################
# analysis pipeline. change according to desired behavior                      #
################################################################################
def pipeline_regardless_of_disease():
    # Step 1: calculate summary statistics
    print("start calculating summary statistics...")
    testmode = True # set to false to run in production mode
    pipeline_calculate_summary_statistics_for_mf_regardless_of_diseases(
        test_mode=testmode)
    print("done calculating summary statistics")

    # Step 2: interpret summary statistics. Output csv files.
    # Note: only run this in production mode
    print("start interpreting summary statistics...")
    if testmode:
        print("test mode: no csv file is written")
    else:
        pipeline_interpret_mf_regardless_of_diagnosis('textHpo', 'labHpo', hpo,
                                                      remove_pairs_with_same_terms=False,
                                                      remove_reflective_pairs=False,
                                                      remove_pairs_with_dependency=True)
        pipeline_interpret_mf_regardless_of_diagnosis('textHpo', 'textHpo', hpo,
                                                      remove_pairs_with_same_terms=True,
                                                      remove_reflective_pairs=True,
                                                      remove_pairs_with_dependency=True)
        pipeline_interpret_mf_regardless_of_diagnosis('labHpo', 'labHpo', hpo,
                                                      remove_pairs_with_same_terms=True,
                                                      remove_reflective_pairs=True,
                                                      remove_pairs_with_dependency=True)
        print("csv files are written to {}".format(base_dir))
    print("done interpreting summary statistics")


def pipeline_regarding_diseases():
    # Step 1: calculating summary statistics for diseases of interest
    # specified in the configuration file
    # Comment out this section if the goal is to process summary statistics
    # to generate nicely rendered csv and html files
    print("start calculating summary statistics...")
    testmode = False  # set to false to run in production mode
    pipeline_calculate_summary_statistics_for_mf_regarding_diseases(
        test_mode=testmode)
    print("done calculating summary statistics")
    if testmode:
        print("Step 2 and 3 not run for test mode. Pipeline completed. "
              "Exiting.")
        return 0

    # Step 2: following the instructions printed by the function
    # below to simulate p values on Helix and download to local machine
    # if you set mock to true, it will create empty p value files for Step 3;
    #  but note that -1 will be used for all p values in this case
    pipeline_simulate_to_get_p_values(primary_only=config['primary_only'],
                                      diag_code='038', mock=False)

    # Step 3: interpret the mutual information and synergy for one diagnosis
    # list of diseases that you have calculate p values
    diag_codes = ['038']
    primary_only = config['analysis-prod']['regarding_diagnosis']['primary_diagnosis_only']

    for diag_code in diag_codes:
        # for any disease, calculate their synergy, and output a CSV
        p1_source = 'textHpo'
        p2_source = 'labHpo'
        remove_pairs_with_same_terms = False
        remove_reflective_pairs = False
        remove_pairs_with_dependency = True

        csv_dir, csv_textHpo_labHpo_path = pipeline_interpret_mf_regarding_diagnosis(
            p1_source, p2_source, primary_only, diag_code, hpo,
            remove_pairs_with_same_terms,
            remove_reflective_pairs,
            remove_pairs_with_dependency,
            sort_by='synergy',
            percentile_for_cytoscape=0.01)

        p1_source = 'labHpo'
        p2_source = 'labHpo'
        remove_pairs_with_same_terms = True
        remove_reflective_pairs = True
        remove_pairs_with_dependency = True

        _, csv_labHpo_labHpo_path = pipeline_interpret_mf_regarding_diagnosis(
            p1_source, p2_source, primary_only, diag_code, hpo,
            remove_pairs_with_same_terms,
            remove_reflective_pairs,
            remove_pairs_with_dependency,
            sort_by='synergy',
            percentile_for_cytoscape=0.01)

        p1_source = 'textHpo'
        p2_source = 'textHpo'
        remove_pairs_with_same_terms = True
        remove_reflective_pairs = True
        remove_pairs_with_dependency = True

        _, csv_labHpo_labHpo_path = pipeline_interpret_mf_regarding_diagnosis(
            p1_source, p2_source, primary_only, diag_code, hpo,
            remove_pairs_with_same_terms,
            remove_reflective_pairs,
            remove_pairs_with_dependency,
            sort_by='synergy',
            percentile_for_cytoscape=0.01)


if __name__ == '__main__':
    # run the pipeline to analyze the mutual information in regardless of any
    #  diseases.
    # Only need to run once under production mode.
    # pipeline_regardless_of_disease()

    # run the pipeline to analyze the mutual information in regarding to a
    # disease
    # pipeline_regarding_diseases()
    pipeline_simulate_to_get_p_values(True, '493', False)



