import pathlib
import pandas
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
from rest_framework import serializers

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.statements import DetailedStatementSerializer
from controls.models import Poam, System

structlog.configure(logger_factory=LoggerFactory())
logger = get_logger()
class SimplePoamSerializer(ReadOnlySerializer):
    statement = serializers.SerializerMethodField('get_statement')

    def get_statement(self, poam):
        smt = {
            'sid': poam.statement.sid,
            'sid_class': poam.statement.sid_class,
            'source': poam.statement.source,
            'pid': poam.statement.pid,
            'body': poam.statement.body,
            'statement_type': poam.statement.statement_type,
            'remarks': poam.statement.remarks,
            'status': poam.statement.status,
            'version': poam.statement.version,
            'created': poam.statement.created,
            'updated': poam.statement.updated,
            # 'parent': poam.statement.parent,
            # 'prototype': poam.statement.prototype,
            # 'producer_element': poam.statement.producer_element,
            # 'consumer_element': poam.statement.consumer_element,
            # 'mentioned_elements': poam.statement.mentioned_elements,
            'uuid': poam.statement.uuid,
            'import_record': poam.statement.import_record,
            # 'change_log': poam.statement.change_log,
            # 'history': poam.statement.history,
        }
        return smt
    class Meta:
        model = Poam
        fields = ['poam_id', 'controls', 'weakness_name', 'weakness_detection_source', 'weakness_source_identifier',
                  'remediation_plan', 'scheduled_completion_date', 'milestones','milestone_changes',
                  'risk_rating_original', 'risk_rating_adjusted', 'poam_group', 'statement']

class SimpleSpreadsheetPoamSerializer(ReadOnlySerializer):
    spreadsheet_poams = serializers.SerializerMethodField('get_spreadsheet_poams')

    def get_spreadsheet_poams(self, system):
        print(2, "======== system.id, system", system.id, system)
        poams_list = []
        counter = 1;
        fn = "local/poams_list.xlsx"
        if pathlib.Path(fn).is_file():
            try:
                df_dict = pandas.read_excel(fn, header=1)
                for index, row in df_dict.iterrows():
                    # import ipdb; ipdb.set_trace()
                    if system.id == row.get('CSAM ID', ""):
                        poam_dict = {
                            "id": index,
                            "csam_id": row.get('CSAM ID', ""),
                            "inherited": "No",
                            "org": row.get('Org', ""),
                            "sub_org": row.get('Sub Org', ""),
                            "system_name": row.get('System Name', ""),
                            "poam_id": row.get('POAM ID', ""   ),
                            "poam_title": row.get('POAM Title', ""),
                            "system_type": row.get('System Type', ""),
                            "detailed_weakness_description": row.get('Detailed Weakness Description', ""),
                            "status": row.get('Status', "")
                        }
                        counter += 1
                        # Enhance data
                        # Test for control inheritance
                        inherited = "No"
                        if "CA-8" in row.get('POAM Title', ""):
                            poam_dict['inherited'] = "Yes"
                            poam_dict['system_name'] = f"{poam_dict['system_name']} inherits from Central Log Server"
                        poams_list.append(poam_dict)
            except FileNotFoundError as e:
                logger.error(f"Error reading file {fn}: {e}")
            except Exception as e:
                logger.error(f"Other Error reading file {fn}: {e}")
        return poams_list
    class Meta:
        model = System
        fields = ['spreadsheet_poams']

class SimpleUpdatePoamSpreadsheetSerializer(WriteOnlySerializer):
    row = serializers.IntegerField(max_value=None, min_value=None)
    column = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    value = serializers.CharField(min_length=None, max_length=None, allow_blank=True, trim_whitespace=True)
    
    class Meta:
        model = System
        fields = ['row', 'column', 'value']
class DetailedPoamSerializer(SimplePoamSerializer):
    statement = DetailedStatementSerializer()

    class Meta:
        model = Poam
        fields = SimplePoamSerializer.Meta.fields + ['statement']
