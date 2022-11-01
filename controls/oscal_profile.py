class ProfileSerializer(object):
    def __init__(self, system, impl_smts):
        self.system = system
        self.impl_smts = impl_smts

class OSCALProfileSerializer(ProfileSerializer):
    # The OSCAL assessment plan model represents the information contained within an assessment plan, 
    # and is typically used by anyone planning to perform an assessment or continuous monitoring activities 
    # on an information system to determine the degree to which that system complies with a given control baseline
    # used by the system.

    # It was designed to use identical syntax to the assessment results model, 
    # for overlapping assemblies (Objectives, Assessment Subject, Assets, and Assessment Activities).
    @staticmethod
    def generate_metadata(self):
        project = self.system.projects.first()
        orgs = list(Organization.objects.all())

        list_of_parties = []
        list_of_roles = []
        list_of_resp_parties = []
        list_of_resp_roles = []
        list_of_locations = []
        list_of_revisions = []
        list_of_document_ids = []
        list_of_props = []
        list_of_links = []
        remarks = '' # markup-line data type are also supported by the markup-multiline data type,
        published = '' #datetime with timezone

        if self.system.root_element.tags.exists():
            list_of_props.extend([{"name": "tag", "ns": "https://govready.com/ns/oscal", "value": tag.label} for tag in self.element.tags.all()])

        for appointment in self.system.root_element.appointments.all():
            party = {
                "uuid": str(appointment.party.uuid),
                "type": appointment.party.party_type,
                "name": appointment.party.name,
                "short-name": appointment.party.short_name,
                "email-addresses": [appointment.party.email],
                "telephone-numbers": [
                    {
                        "type": "home", "number": appointment.party.phone_number
                    },
                    {
                        "type": "mobile", "number": appointment.party.mobile_phone,
                    }
                ]
            }
            role = {
                "id": appointment.role.role_id,
                "title": appointment.role.title,
                "short-name": appointment.role.short_name,
                "description": appointment.role.description,
                # props
                # links
                # remarks
            }
            respParty = {
                'role-id': role["id"],
                'party-uuids': [party["uuid"]]
            }
            respRole = respParty

            if len(list_of_resp_parties) == 0:
                list_of_resp_parties.append(respParty)
            
            if len(list_of_resp_roles) == 0:
                list_of_resp_roles.append(respRole)

            # Adding resp party to its respective index
            if role["id"] in [x['role-id'] for x in list_of_resp_parties]:
                for x in list_of_resp_parties:
                    if x['role-id'] == role["id"] and party['uuid'] not in x['party-uuids']:
                        x['party-uuids'].append(party["uuid"])
            else:
                list_of_resp_parties.append(respParty)

            if role["id"] in [x['role-id'] for x in list_of_resp_roles]:
                for x in list_of_resp_roles:
                    if x['role-id'] == role["id"] and party['uuid'] not in x['party-uuids']:
                        x['party-uuids'].append(party["uuid"])
            else:
                list_of_resp_roles.append(respRole)

            if party not in list_of_parties:
                list_of_parties.append(party)

            if role not in list_of_roles:
                list_of_roles.append(role)

        parties = [
            {
                "uuid": str(uuid.uuid4()), 
                "type": "organization", 
                "name": org.name
            } for org in orgs]
        parties.extend(list_of_parties)
        

        metadata = {
            "title": "{} System Security Plan".format(self.system.root_element.name),
            "last-modified": self.system.root_element.updated.replace(microsecond=0).isoformat(),
            "version": project.version,
            "oscal-version": self.system.root_element.oscal_version
        }
        
        if published:
            metadata['published'] = published
        # Addition of Optional Metadata 
        if len(list_of_revisions) != 0:
            metadata['revisions'] = list_of_revisions

        if len(list_of_document_ids) != 0:
            metadata['document-ids'] = list_of_document_ids

        if len(list_of_props) != 0:
            metadata['props'] = list_of_props
        
        if len(list_of_links) != 0:
            metadata['links'] = list_of_links

        if len(list_of_roles) != 0:
            metadata['roles'] = list_of_roles

        if len(list_of_locations) != 0:
            metadata['locations'] = list_of_locations

        if len(parties) != 0:
            metadata['parties'] = parties

        if len(list_of_resp_parties) != 0:
            metadata['responsible-parties'] = list_of_resp_parties

        if remarks:
            metadata['remarks'] = remarks

        return metadata
    
    def generate_imports(self):
        #  Identifies the OSCAL-based SSP of the system being assessed. 
        # Several pieces of information about a system that normally appear in an assessment plan are now 
        # referenced via this import statement, eliminating the need to duplicate and maintain the same 
        # information in multiple places.

        # href: A resolvable URL reference to the system security plan for the system being assessed
        # The value of the href can be an internet resource, or a local reference using a fragment e.g. #fragment that points to a back-matter resource in the same document.

        import_ssp = {
            'href': 'https://systemsecurityplan_link',
            'remarks': 'additional commentary on the containing object in markup-multiline'
        }
        return import_ssp

   
    def generate_merge(self):
        # Identifies the rules of engagement, disclosures, limitation of liability statements, assumption statements, 
        # methodology, and other explanatory content as needed.

        merge = {}
        return merge

   
    def generate_modify(self):
        # Identifies the elements of the system that are in scope for the assessment, 
        # including locations, components, inventory items, and users.

        modify = {}
        return modify

    def generate_back_matter(self):
        # Back matter syntax is identical in all OSCAL models. 
        # It is used for attachments, citations, and embedded content such as graphics.

        back_matter = {}
        return back_matter

    def generate_profile(self):
        # Generate OSCAL Assessment Plan as JSON
        # Generate base of Assessment Plan

        metadata = self.generate_metadata(self)
        imports = self.generate_imports()
        merge = self.generate_merge()
        modify = self.generate_modify()
        back_matter = self.generate_back_matter()

        profile = {
            "assessment-plan": {
                "uuid": str(uuid4()),
                "metadata": metadata,
                "imports": imports
            }
        }
        
        # Addition of optional Assessment Plan properties
        if merge:
            profile["profile"]["merge"] = merge
        
        if modify:
            profile["profile"]["modify"] = modify
        
        if back_matter:
            profile["profile"]["back-matter"] = back_matter
        
        return profile

    def validate(self, profile):
        validated = False

        # try:
        #     # validate that this object is valid by the component definition
        #     trestlecomponent.ComponentDefinition.validate(assessment_plan)
        #     validated = True
        # except:
        #     validated = False

        return validated
    
    def as_json(self):
        # Build OSCAL
        # Example: https://github.com/usnistgov/OSCAL/blob/master/src/content/ssp-example/json/example-component.json
        #open the file
        # with open('controls/data/oscal_shemas/1.0.0/oscal_component_schema.json') as f:
        #     component_schema = json.load(f)
        profile = self.generate_profile()
        # validate_assessment_plan = self.validate(assessment_plan['assessment-plan'])

        profile_oscal_json = json.dumps(profile, sort_keys=False, indent=2)
        return profile_oscal_json
