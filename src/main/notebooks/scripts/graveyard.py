# def diagnosisTextHpo(phenotype):
#     """
#     Assign 0 or 1 to each encounter whether a phenotype is observed from radiology reports
#     @phenotype: an HPO term id
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_textHpo')
#     """
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_textHpo
#         SELECT
#             L.*, IF(R.MAP_TO IS NULL, '0', '1') AS PHEN_TXT
#         FROM JAX_mf_diag AS L
#         LEFT JOIN
#             (SELECT *
#             FROM JAX_textHpoProfile
#             WHERE JAX_textHpoProfile.MAP_TO = '{}') AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID
#     '''.format(phenotype))
#     """
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_textHpo
#         WITH L AS (SELECT JAX_mf_diag.*, '{}' AS PHEN_TXT FROM JAX_mf_diag)
#         SELECT
#             L.*, IF(R.dummy IS NULL, '0', '1') AS PHEN_TXT_VALUE
#         FROM L
#         LEFT JOIN
#             JAX_textHpoProfile AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.PHEN_TXT = R.MAP_TO
#     '''.format(phenotype))
#     cursor.execute('CREATE INDEX JAX_mf_diag_textHpo_idx01 ON JAX_mf_diag_textHpo (SUBJECT_ID, HADM_ID)')

# def diagnosisAllTextHpo(threshold_min, threshold_max):
#     """
#     For phenotypes of interest, defined with two parameters, assign 0 or 1 to each encounter whether a phenotype is observated from text data
#     @param threshold_min: minimum threshold of encounter count for a phenotype to be interesting.
#     @param threshold_max: maximum threshold of encounter count for a phenotype to be interesting.
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_allTextHpo')
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_allTextHpo
#         WITH
#             P AS (SELECT MAP_TO AS PHEN_TXT FROM JAX_textHpoFrequencyRank WHERE N BETWEEN {} AND {}),
#             L AS (SELECT * FROM JAX_mf_diag JOIN P)
#         SELECT
#             L.*, IF(R.dummy IS NULL, '0', '1') AS PHEN_TXT_VALUE
#         FROM L
#         LEFT JOIN
#             JAX_textHpoProfile AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.PHEN_TXT = R.MAP_TO
#     '''.format(threshold_min, threshold_max))
#     cursor.execute('CREATE INDEX JAX_mf_diag_allTextHpo_idx01 ON JAX_mf_diag_allTextHpo (SUBJECT_ID, HADM_ID, PHEN_TXT)')

# def diagnosisLabHpo(phenotype):
#     """
#     Assign 0 or 1 to each encounter whether a phenotype is observed from lab tests
#     @phenotype: an HPO term id
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_labHpo')
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_labHpo
#         WITH L AS (SELECT JAX_mf_diag.*, '{}' AS PHEN_LAB FROM JAX_mf_diag)
#         SELECT
#             L.*, IF(R.dummy IS NULL, '0', '1') AS PHEN_LAB_VALUE
#         FROM L
#         LEFT JOIN
#              JAX_labHpoProfile AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.PHEN_LAB = R.MAP_TO
#     '''.format(phenotype))
#     cursor.execute('CREATE INDEX JAX_mf_diag_labHpo_idx01 ON JAX_mf_diag_labHpo (SUBJECT_ID, HADM_ID)')

# def diagnosisAllLabHpo(threshold_min, threshold_max):
#     """
#     For phenotypes of interest, defined with two parameters, assign 0 or 1 to each encounter whether a phenotype is observated from lab tests
#     @param threshold_min: minimum threshold of encounter count for a phenotype to be interesting.
#     @param threshold_max: maximum threshold of encounter count for a phenotype to be interesting.
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_allLabHpo')
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_allLabHpo
#         WITH
#             P AS (SELECT MAP_TO AS PHEN_LAB FROM JAX_labHpoFrequencyRank WHERE N BETWEEN {} AND {}),
#             L AS (SELECT * FROM JAX_mf_diag JOIN P)
#         SELECT
#             L.*, IF(R.dummy IS NULL, '0', '1') AS PHEN_LAB_VALUE
#         FROM L
#         LEFT JOIN
#              JAX_labHpoProfile AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.PHEN_LAB = R.MAP_TO
#     '''.format(threshold_min, threshold_max))
#     cursor.execute('CREATE INDEX JAX_mf_diag_allLabHpo_idx01 ON JAX_mf_diag_allLabHpo (SUBJECT_ID, HADM_ID)')

# def diagnosisTextLab(phenotype):
#     """
#     Merge temporary tables to create one in which each encounter is assigned with 0 or 1 for diagnosis code, phenotype from text data and phenotype from lab tests.
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_txtHpo_labHpo')
#     result = cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_txtHpo_labHpo
#         WITH L AS (SELECT JAX_mf_diag_textHpo.*, '{}' AS PHEN_LAB FROM JAX_mf_diag_textHpo)
#         SELECT L.*, IF(R.dummy IS NULL, '0', '1') AS PHEN_LAB_VALUE
#         FROM L
#         LEFT JOIN
#             JAX_labHpoProfile AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID AND L.PHEN_LAB = R.MAP_TO
#     '''.format(phenotype))


# def diagnosisAllTextAllLab():
#     """
#     Merge temporary tables to create one in which each encounter is assigned with 0 or 1 for diagnosis code, all phenotypes of interest from text data, and all phenotypes from lab tests
#     """
#     cursor.execute('DROP TEMPORARY TABLE IF EXISTS JAX_mf_diag_allTxtHpo_allLabHpo')
#     cursor.execute('''
#         CREATE TEMPORARY TABLE JAX_mf_diag_allTxtHpo_allLabHpo
#         SELECT L.SUBJECT_ID, L.HADM_ID, L.DIAGNOSIS, L.PHEN_TXT, L.PHEN_TXT_VALUE, R.PHEN_LAB, R.PHEN_LAB_VALUE
#         FROM JAX_mf_diag_allTextHpo AS L
#         JOIN JAX_mf_diag_allLabHpo AS R
#         ON L.SUBJECT_ID = R.SUBJECT_ID AND L.HADM_ID = R.HADM_ID
#     ''')


# def initSummaryStatisticTables():
#     """
#     Init summary statistics tables.
#     """
#     # define empty columns to store summary statistics
#     summary_statistics1_radiology = pd.DataFrame(data={'DIAGNOSIS_CODE':[],
#                        'PHENOTYPE':[],
#                        'DIAGNOSIS_VALUE':[],
#                        'PHENOTYPE_VALUE':[],
#                        'N':[]},
#                 columns = ['DIAGNOSIS_CODE', 'PHENOTYPE', 'DIAGNOSIS_VALUE', 'PHENOTYPE_VALUE', 'N'])

#     summary_statistics1_lab = pd.DataFrame(data={'DIAGNOSIS_CODE':[],
#                        'PHENOTYPE':[],
#                        'DIAGNOSIS_VALUE':[],
#                        'PHENOTYPE_VALUE':[],
#                        'N':[]},
#                 columns = ['DIAGNOSIS_CODE', 'PHENOTYPE', 'DIAGNOSIS_VALUE', 'PHENOTYPE_VALUE', 'N'])

#     summary_statistics2 = pd.DataFrame(data={'DIAGNOSIS_CODE':[],
#                        'PHEN_TXT':[],
#                        'PHEN_LAB':[],
#                        'DIAGNOSIS_VALUE':[],
#                        'PHEN_TXT_VALUE':[],
#                        'PHEN_LAB_VALUE':[],
#                        'N':[]},
#                 columns = ['DIAGNOSIS_CODE', 'PHEN_TXT', 'PHEN_LAB', 'DIAGNOSIS_VALUE', 'PHEN_TXT_VALUE', 'PHEN_LAB_VALUE', 'N'])

#     return summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2

# def iterate(primary_diagnosis_only, diagnosis_threshold_min, textHpo_threshold_min, labHpo_threshold_min, logger):
#     logger.info('starting iterating...................................')
#     N = pd.read_sql_query("SELECT count(*) FROM JAX_encounterOfInterest", mydb)
#     # init empty tables to hold summary statistics
#     summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2 = initSummaryStatisticTables()

#     # define a set of diseases that we want to analyze
#     rankICD()

#     diseaseOfInterest = pd.read_sql_query("SELECT * FROM JAX_diagFrequencyRank WHERE N > {}".format(diagnosis_threshold_min), mydb).ICD9_CODE.values
#     diseaseOfInterest = ['428']
#     # define encounters to analyze
#     logger.info('diseases of interest established: {}'.format(len(diseaseOfInterest)))
#     for diagnosis in diseaseOfInterest:
#         logger.info("start analyzing disease {}".format(diagnosis))

#         # assign each encounter whether a diagnosis code is observed
#         # create a table j1 (joint 1)
#         createDiagnosisTable(diagnosis, primary_diagnosis_only)
#         # for every diagnosis, find phenotypes of interest to look at from radiology reports
#         # for every diagnosis, find phenotypes of interest to look at from laboratory tests
#         rankHpoFromText(diagnosis)
#         rankHpoFromLab(diagnosis)

#         textHpoOfInterest = pd.read_sql_query("SELECT * FROM JAX_textHpoFrequencyRank WHERE N > {}".format(textHpo_threshold_min), mydb).MAP_TO.values
#         labHpoOfInterest = pd.read_sql_query("SELECT * FROM JAX_labHpoFrequencyRank WHERE N > {}".format(labHpo_threshold_min), mydb).MAP_TO.values
#         logger.info("TextHpo of interest established, size: {}".format(len(textHpoOfInterest)))
#         logger.info("LabHpo of interest established, size: {}".format(len(labHpoOfInterest)))
#         for textHpo in textHpoOfInterest:
#             logger.info("iteration: TextHpo--{}".format(textHpo))
#             # assign each encounter whether a phenotype is observed from radiology reports
#             diagnosisTextHpo(textHpo)
#             result1_text = pd.read_sql_query('''
#                 SELECT
#                     '{}' AS DIAGNOSIS_CODE, '{}' AS PHENOTYPE, DIAGNOSIS AS DIAGNOSIS_VALUE, PHEN_TXT_VALUE AS PHENOTYPE_VALUE, COUNT(*) AS N
#                 FROM JAX_mf_diag_textHpo
#                 GROUP BY
#                     DIAGNOSIS, PHEN_TXT_VALUE
#             '''.format(diagnosis, textHpo), mydb)
#             summary_statistics1_radiology = summary_statistics1_radiology.append(result1_text)
#             # summary statistics for p1
#             # calculate I(p1;D)
#             for labHpo in labHpoOfInterest:
#                 logger.info(".........LabHpo--{}".format(labHpo))
#                 diagnosisLabHpo(labHpo)
#                 result1_lab = pd.read_sql_query('''
#                     SELECT
#                         '{}' AS DIAGNOSIS_CODE, '{}' AS PHENOTYPE, DIAGNOSIS AS DIAGNOSIS_VALUE, PHEN_LAB_VALUE AS PHENOTYPE_VALUE, COUNT(*) AS N
#                     FROM
#                         JAX_mf_diag_labHpo
#                     GROUP BY DIAGNOSIS, PHEN_LAB_VALUE
#                 '''.format(diagnosis, labHpo), mydb)
#                 summary_statistics1_lab = summary_statistics1_lab.append(result1_lab)

#                 # assign each encounter whether a phenotype is observed from lab tests
#                 diagnosisTextLab(labHpo)
#                 result2 = pd.read_sql_query('''
#                     SELECT
#                         '{}' AS DIAGNOSIS_CODE,
#                         '{}' AS PHEN_TXT,
#                         '{}' AS PHEN_LAB,
#                         DIAGNOSIS AS DIAGNOSIS_VALUE,
#                         PHEN_TXT_VALUE,
#                         PHEN_LAB_VALUE,
#                         COUNT(*) AS N
#                     FROM JAX_mf_diag_txtHpo_labHpo
#                     GROUP BY DIAGNOSIS, PHEN_TXT_VALUE, PHEN_LAB_VALUE
#                 '''.format(diagnosis, textHpo, labHpo), mydb)
#                 summary_statistics2 = summary_statistics2.append(result2)
#     logger.info('end iterating.....................................')
#     return N, summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2


# def iterate_batch(primary_diagnosis_only, diagnosis_threshold_min, textHpo_threshold_min, textHpo_threshold_max, labHpo_threshold_min, labHpo_threshold_max, logger):
#     logger.info('starting iterating...................................')
#     N = pd.read_sql_query("SELECT count(*) FROM JAX_encounterOfInterest", mydb)
#     # init empty tables to hold summary statistics
#     summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2 = initSummaryStatisticTables()

#     # define a set of diseases that we want to analyze
#     rankICD()

#     diseaseOfInterest = pd.read_sql_query("SELECT * FROM JAX_diagFrequencyRank WHERE N > {}".format(diagnosis_threshold_min), mydb).ICD9_CODE.values
#     diseaseOfInterest = ['428']
#     logger.info('diseases of interest established: {}'.format(len(diseaseOfInterest)))

#     for diagnosis in diseaseOfInterest:
#         logger.info("start analyzing disease {}".format(diagnosis))

#         logger.info(".......assigning values of diagnosis")
#         # assign each encounter whether a diagnosis code is observed
#         # create a table j1 (joint 1)
#         createDiagnosisTable(diagnosis, primary_diagnosis_only)
#         # for every diagnosis, find phenotypes of interest to look at from radiology reports
#         # for every diagnosis, find phenotypes of interest to look at from laboratory tests
#         rankHpoFromText(diagnosis)
#         rankHpoFromLab(diagnosis)
#         logger.info("..............diagnosis values found")

#         logger.info(".......assigning values of TextHpo")
#         diagnosisAllTextHpo(textHpo_threshold_min, textHpo_threshold_max)
#         result1_text = pd.read_sql_query("""
#             SELECT '{}' AS DIAGNOSIS_CODE,
#                 PHEN_TXT AS PHENOTYPE,
#                 DIAGNOSIS AS DIAGNOSIS_VALUE,
#                 PHEN_TXT_VALUE AS PHENOTYPE_VALUE,
#                 COUNT(*) AS N
#             FROM JAX_mf_diag_allTextHpo
#             GROUP BY DIAGNOSIS, PHEN_TXT, PHEN_TXT_VALUE
#         """.format(diagnosis), mydb)
#         logger.info("..............TextHpo values found")
#         summary_statistics1_radiology = summary_statistics1_radiology.append(result1_text)


#         logger.info(".......assigning values of LabHpo")
#         diagnosisAllLabHpo(labHpo_threshold_min, labHpo_threshold_max)
#         result1_lab = pd.read_sql_query("""
#             SELECT
#                 '{}' AS DIAGNOSIS_CODE,
#                 PHEN_LAB AS PHENOTYPE,
#                 DIAGNOSIS AS DIAGNOSIS_VALUE,
#                 PHEN_LAB_VALUE AS PHENOTYPE_VALUE,
#                 COUNT(*) AS N
#             FROM JAX_mf_diag_allLabHpo
#             GROUP BY DIAGNOSIS, PHEN_LAB, PHEN_LAB_VALUE
#         """.format(diagnosis), mydb)
#         logger.info("..............LabHpo values found")
#         summary_statistics1_lab = summary_statistics1_lab.append(result1_lab)

#         logger.info(".......building diagnosis-TextHpo-LabHpo joint distribution")
#         diagnosisAllTextAllLab()
#         result2 = pd.read_sql_query("""
#             SELECT
#                 '{}' AS DIAGNOSIS_CODE,
#                 PHEN_TXT,
#                 PHEN_LAB,
#                 DIAGNOSIS AS DIAGNOSIS_VALUE,
#                 PHEN_TXT_VALUE,
#                 PHEN_LAB_VALUE,
#                 COUNT(*) AS N
#             FROM JAX_mf_diag_allTxtHpo_allLabHpo
#             GROUP BY DIAGNOSIS, PHEN_LAB, PHEN_LAB_VALUE, PHEN_TXT, PHEN_TXT_VALUE
#         """.format(diagnosis) , mydb)
#         logger.info("..............diagnosis-TextHpo-LabHpo joint distribution built")
#         summary_statistics2 = summary_statistics2.append(result2)

#     logger.info('end iterating.....................................')
#     return N, summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2

# how to run this
# it takes either too long or too much memory space to run
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 1. build the temp tables for Lab converted HPO, Text convert HPO
# Read the comments within the method!
#initTables(debug=False)
# 2. iterate the database t (for debug, use parameter values: 0, 10, 15, for production, use parameter values: 0, 10000, 10000
#N, summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2 = iterate(diagnosis_threshold_min=0, textHpo_threshold_min=10, labHpo_threshold_min=15, logger=logger)
#N, summary_statistics1_radiology, summary_statistics1_lab, summary_statistics2 = iterate(diagnosis_threshold_min=0, textHpo_threshold_min=1000, labHpo_threshold_min=1000, logger=logger)

# 2b. use the batch method
#N2, summary_statistics1_radiology2, summary_statistics1_lab2, summary_statistics22 = iterate_batch(diagnosis_threshold_min=0, textHpo_threshold_min=0, textHpo_threshold_max=100, labHpo_threshold_min=0, labHpo_threshold_max=100, logger=logger)
#N2, summary_statistics1_radiology2, summary_statistics1_lab2, summary_statistics22 = iterate_batch(diagnosis_threshold_min=0, textHpo_threshold_min=1000, textHpo_threshold_max=100000, labHpo_threshold_min=1000, labHpo_threshold_max=100000, logger=logger)