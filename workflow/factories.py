from dataclasses import dataclass, field
import re
from hashlib import blake2b
import uuid
import logging
import json
import os
from .models import WorkflowImage

"""

Current format:
rule: Hide small org internal SOC question +viewque:(org.internal_soc, False) -setans:(org.internal_soc, some value)

Alternate formats:
rule: hide small org internal SOC question if($org.size = Small) true=$viewque(org.internal_soc, False) false=$SETANS(org.internal_soc, some value)
rule: hide small org internal SOC question if($org.size = Small) true=viewque(org.internal_soc, False) false=SETANS(org.internal_soc, some value)

"""

def empty_list():
    return []


def empty_dict():
    return {}


@dataclass
class Feature:

    feature_descriptor: str = ''
    cmd: str = ''
    text: str = ''
    props: list = field(default_factory=empty_list)
    id: str = ''


def skeleton_feature():
    return Feature()


CMD_PATTERN = '(?P<cmd>[A-Z:]+|[a-zA-Z]+:)'
PROP_PATTERN = '[a-zA-Z_\-.0-9]*\(.*?\)'
TEST_PATTERN = '(IF:\(.*?\)|if:\(.*?\))'
TRUE_FUNC_PATTERN = '([+][a-zA-Z_\-.0-9]*:\(.*?\))'

def get_cmd(feature_descriptor):
    """Return parsed command from feature descriptor."""

    try:
        regex = fr'^{CMD_PATTERN} (?P<cmd_content>.*)$'
        m = re.match(regex, feature_descriptor)
        cmd = m.group('cmd').strip(':')
        msg = f"[DEBUG] line: '{feature_descriptor}'"
        print(msg)
        return cmd
    except Exception as e:
        msg = f"[ERROR] command line malformed '{e}' received '{feature_descriptor}'"
        print(msg)
        logging.exception(msg)
        return None


@dataclass
class FeatureFactory:
    """
    Factory for producing flow feature objects.
    The factory doesn't maintain any of the instances it creates.
    """

    feature_descriptor: str
    cmd: str = ''
    text: str = ''
    props: list = field(default_factory=empty_list)
    actions: list = field(default_factory=empty_list)
    id: str = ''
    feature: Feature = field(default_factory=skeleton_feature)
    cmd_pattern: str = CMD_PATTERN
    prop_pattern: str = PROP_PATTERN
    test_pattern: str = TEST_PATTERN
    true_func_pattern = TRUE_FUNC_PATTERN

    def __post_init__(self):
        self._set_cmd()
        self._set_props()
        self._set_test()
        self._set_true_action()
        self._set_text()
        self._set_id()

    def _set_cmd(self):
        """Parse out command from feature descriptor."""

        self.feature.cmd = get_cmd(self.feature_descriptor)
        return None

    def _set_props(self):
        """Parse out props from feature descriptor."""

        # parse out props
        try:
            regex = fr'{self.prop_pattern}'
            match_list = re.findall(regex, self.feature_descriptor)
            for m_str in match_list:
                m = re.match(r'(\w+)\((.*)\)', m_str)
                if m:
                    self.props.append({m.group(1): m.group(2)})
        except Exception as e:
            msg = f"[ERROR] failure '{e}' parsing props '{self.feature_descriptor}'"
            print(msg)
            logging.exception(msg)
        self.feature.props = self.props
        return None

    def _set_test(self):
        """Parse out rule test from feature descriptor."""

        try:
            regex = fr'{self.test_pattern}'
            match_list = re.findall(regex, self.feature_descriptor)
            if match_list:
                self.feature.test_pattern = match_list[0]
        except:
            msg = f"[ERROR] failure '{e}' parsing test_pattern '{self.feature_descriptor}'"
            print(msg)
            logging.exception(msg)
        return None

    def _set_true_action(self):
        """Parse out true action function from feature descriptor."""

        try:
            regex = fr'{self.true_func_pattern}'
            match_list = re.findall(regex, self.feature_descriptor)
            if match_list:
                self.feature.true_action = match_list[0].lstrip('+')
        except Exception as e:
            msg = f"[ERROR] failure '{e}' parsing true_func_pattern '{self.feature_descriptor}'"
            print(msg)
            logging.exception(msg)
        return None

    def _set_text(self):
        """Parse out feature content after removing cmd, props from feature descriptor."""

        self.text = self.feature_descriptor
        regex_rm_cmd = fr'^{self.cmd_pattern} '
        regex_rm_test = fr'{self.test_pattern}'
        regex_rm_true_func = fr'{self.true_func_pattern}'
        regex_rm_props = fr'{self.prop_pattern}'
        for regex in [regex_rm_cmd, regex_rm_test, regex_rm_true_func, regex_rm_props]:
            self.text = re.sub(regex, '', self.text).strip()
        self.feature.text = self.text
        return None

    def _set_id(self):
        """Set feature id via defined prop or hash of text."""

        id_prop = next((item for item in self.props if 'id' in item.keys()), None)
        if id_prop is not None:
            self.id = id_prop['id']
        else:
            h = blake2b(digest_size=4)
            h.update(str.encode(self.text))
            self.id = h.hexdigest()
        self.feature.id = self.id


@dataclass
class FlowImage:

    flow_image: dict = field(default_factory=empty_dict)

    def loads(self, flow_image_str):
        """Load flow image from string"""
        self.flow_image = json.loads(flow_image_str)
        return self.flow_image

    def load(self, file_obj):
        """Retrieve flow image from file."""
        self.flow_image = json.load(file_obj)
        return self.flow_image

    def save(self):
        """Save flow image to file."""
        data_dir = os.path.join(f"{os.getcwd()}", 'data')
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        json_data = json.dumps(self.flow_image, default=lambda o: o.__dict__)
        # print(json.dumps(json.loads(json_data), indent=4))
        filename = f"{self.flow_image['name']}__{self.flow_image['uuid']}.fim"
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(json.dumps(json.loads(json_data), indent=4))
            return True
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            return False
        except:  # handle other exceptions such as attribute errors
            print(f"Unexpected error: {sys.exc_info()[0]}")
            return False

@dataclass
class FlowImageFactory:
    """Returns a flow image object from a feature set to be serialized and persisted."""

    name: str
    uuid: str = str(uuid.uuid4())
    description: str = ''
    feature_descriptor_text: str = ''
    feature_descriptor_list: list = field(default_factory=empty_list)
    features: list = field(default_factory=empty_list)
    flow_image: dict = field(default_factory=empty_dict)

    def split_feature_descriptor_text(self):
        """Split multiline text containing multiple feature descriptors into individual feature descriptors."""

        feature_descriptors = [fd.strip() for fd in self.feature_descriptor_text.split("\n") if fd.strip() != '']
        self.feature_descriptor_list += feature_descriptors
        # todo: should self.feature_descriptor_text be reset to ''?
        return None

    def prepare_features(self):
        """Iterate through feature descriptor list to create features and append them to list of features."""

        for fd in self.feature_descriptor_list:
            msg = f'[INFO] making feature or rule from {fd}'
            print(msg)
            feature_fac = FeatureFactory(fd)
            feature = feature_fac.feature
            # ensure feature id unique
            fid = feature.id
            if fid in [f.id for f in self.features]:
                while fid in [f.id for f in self.features]:
                    fid = fid + "0"
                feature.id = fid
            self.features.append(feature)
        return None

    def create_flow_image(self):
        """Create the flow image object that can be serialized and persisted"""

        fi_dict = {'name': self.name,
              'uuid': self.uuid,
              'type': 'flow_image',
              'features': self.features}
        self.flow_image = FlowImage(flow_image=fi_dict)
        self.flow_image.save()
        return self.flow_image

    def update_or_create_workflowimage(self, workflowimage_record=None):
        """Create the workflow image object that can be serialized and persisted"""
        
        fi_uuid=str(uuid.uuid4())
        # express features list and feature_order
        features_list = {}
        feature_order = []
        rules_list = {}
        rule_order = []
        rules = {}
        for feature in self.features:
            if feature.cmd in ['rule', 'RULE']:
                # create rule
                feature_obj = {
                    'cmd': feature.cmd,
                    'props': feature.props,
                    'test': feature.test_pattern,
                    'true_action': feature.true_action,
                    'text': feature.text,
                    'id': feature.id,
                    'complete': False,
                    'status': 'not-started'
                }
                rules_list[feature_obj['id']] = feature_obj
                rule_order.append(feature_obj['id'])
            else:
                feature_obj = {
                    'cmd': feature.cmd,
                    'props': feature.props,
                    'text': feature.text,
                    'id': feature.id,
                    'complete': False,
                    'status': 'not-started'
                }
                features_list[feature_obj['id']] = feature_obj
                feature_order.append(feature_obj['id'])
        # build workflow dict
        wf_dict = {'name': self.name,
                  'uuid': fi_uuid,
                  'description': self.description,
                  'type': 'flow_image',
                  'status': 'red',
                  "complete": False,
                  'features': features_list,
                  "curr_feature": feature_order[0],
                  "feature_order": feature_order
              }
        rules = {'features': rules_list,
                'rule_order': rule_order
            }

        if workflowimage_record and WorkflowImage.objects.filter(pk=workflowimage_record.pk).exists():
            recs_updated = WorkflowImage.objects.filter(pk=workflowimage_record.pk).update(name=wf_dict['name'], uuid=wf_dict['uuid'], workflow=wf_dict, rules=rules)
            if recs_updated:
                workflowimage = WorkflowImage.objects.filter(pk=workflowimage_record.pk)[0]
            else:
                workflowimage = None
        else:
            workflowimage = WorkflowImage.objects.create(name=wf_dict['name'], uuid=wf_dict['uuid'], workflow=wf_dict, rules=rules)
        return workflowimage

    def update_or_create_workflowimage_from_flowtext(self, flowtext, workflowimage_record=None):
        """Update or create the workflow image object from input flow feature text descriptions"""

        self.feature_descriptor_text = flowtext
        self.split_feature_descriptor_text()
        self.prepare_features()
        wfi = self.update_or_create_workflowimage(workflowimage_record)
        return wfi

    def create_workflowimage_from_workflowrecipe(self, workflowrecipe):
        """Create the workflow image object from workflowrecipe object"""

        flowtext = workflowrecipe.recipe
        self.description = workflowrecipe.description
        self.name = workflowrecipe.name
        # TODO: should we get a new uuid if content of a workflow changes?
        if WorkflowImage.objects.filter(workflowrecipe=workflowrecipe).exists():
            wfi = WorkflowImage.objects.filter(workflowrecipe=workflowrecipe)[0]
            wfi = self.update_or_create_workflowimage_from_flowtext(flowtext, wfi)
        else:
            wfi = self.update_or_create_workflowimage_from_flowtext(flowtext)
            # relate new workflowimage to workflowrecipe
            wfi.workflowrecipe = workflowrecipe
        wfi.name = self.name
        wfi.workflow['name'] = self.name
        wfi.workflow['description'] = self.description
        wfi.save()
        return wfi

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

