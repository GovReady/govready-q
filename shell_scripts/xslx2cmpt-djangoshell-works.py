parsing


#
# WORKING PARSE AND LOAD SNIPPET TO LOAD
# CONTROL STATEMENTS FOR A SINGLE COMPONENT
#

# start python shell
python manage.py shell

# identify path to spreadsheet
fpc = "/codedata/data/dhs/govready_control_smts_sys_spec_common.xlsx"

# use panda dataframe to consume data (because xlrd no longer ready .xlsx files)
import pandas as pd
import openpyxl
fp2 = "/codedata/data/dhs/govready_control_smts_sys_spec_edits2.xlsx"
df2 = pd.read_excel(fp2, engine='openpyxl', index_col=0)

# spreadsheet has some odd formatting, so let's give ourselves keys
# so we know which rows to consume
df2.index
Index(['AC-2', 'AC-2 (1)', 'AC-2 (2)', 'AC-2 (3)', 'AC-2 (4)', 'AC-3', 'AC-6',
       'AC-6 (1)', 'AC-6 (2)', 'AC-6 (5)', 'AC-6 (9)', 'AC-6 (10)', 'AC-11',
       'AC-11 (1)', 'AC-17', 'AC-17 (1)', 'AC-17 (2)', 'AC-17 (3)',
       'AC-17 (4)', 'AU-2', 'AU-2 (3)', 'AU-6', 'AU-6 (1)', 'AU-6 (3)', 'CA-3',
       'CA-3 (5)', 'CA-5', 'CA-7', 'CA-7 (1)', 'CM-2', 'CM-2 (1)', 'CM-2 (3)',
       'CM-2 (7)', 'CM-6', 'CM-7', 'CM-7 (1)', 'CM-7 (2)', 'CM-7 (4)', 'CM-8',
       'CM-8 (1)', 'CM-8 (3)', 'CM-8 (5)', 'IA-2', 'IA-2 (1)', 'IA-2 (2)',
       'IA-2 (3)', 'IA-2 (8)', 'IA-2 (11)', 'IA-2 (12)', 'IR-4', 'IR-4 (1)',
       'IR-5', 'IR-6', 'IR-6 (1)', 'PL-2', 'PL-2 (3)', 'PL-8', 'RA-2', 'RA-3',
       'RA-5', 'RA-5 (1)', 'RA-5 (2)', 'RA-5 (5)', 'SA-9', 'SA-9 (2)', 'SA-11',
       'SC-7', 'SC-7 (3)', 'SC-7 (4)', 'SC-7 (5)', 'SC-7 (7)', 'SC-8',
       'SC-8 (1)', 'SC-12', 'SC-13', 'SC-18', 'SC-28', 'SI-2', 'SI-2 (2)',
       'SI-3', 'SI-3 (1)', 'SI-3 (2)', 'SI-4', 'SI-4 (2)', 'SI-4 (4)',
       'SI-4 (5)', 'SI-10'],
      dtype='object', name='Paragraph/ReqID')

# create an import record object
ir = ImportRecord.objects.create(name='govready-loop-2')
ir.save()

# create a component
egr = Element.objects.create(name="GovReady-Q")
egr.import_record = ir

# set up control catalogs
sc='NIST_SP-800-53_rev4'
st = "control_implementation_prototype"
egr = Element.objects.create(name="GovReady-Q", import_record = ir)
egr.save()

# small test loop
for i in df2.index[1:3]:
    i
    oscalize_control_id(i)
    df2.loc[i]['receiver Responsibility:'][0:40]

# ok, real work of importing the statements with the control
for i in df2.index[4:]:
    sid = oscalize_control_id(i)
    smt = Statement.objects.create(sid=sid,sid_class=sc,statement_type=st,import_record=ir,producer_element=egr)
    smt.remarks = df2.loc[i]['Greg Edits']
    smt.body = df2.loc[i]['receiver Responsibility:']
    smt.save()

# not sure what this snippet is
for i in df2.index:
    sid = oscalize_control_id(i)
    eg
