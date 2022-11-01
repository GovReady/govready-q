# generated by datamodel-codegen:
#   filename:  AssessmentPlanOSCALSchema.json
#   timestamp: 2022-10-17T20:39:55+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Extra, Field, constr


class Url(BaseModel):
    __root__: AnyUrl = Field(
        ...,
        description='The uniform resource locator (URL) for a web site or Internet presence associated with the location.',
        title='Location URL',
    )


class OscalApOscalMetadataLocationUuid(BaseModel):
    __root__: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented identifier reference to a location defined in the metadata section of this or another OSCAL instance. The UUID of the location in the source OSCAL instance is sufficient to reference the data item locally or globally (e.g., in an imported OSCAL instance).',
        title='Location Reference',
    )


class Type(Enum):
    person = 'person'
    organization = 'organization'


class ExternalId(BaseModel):
    class Config:
        extra = Extra.forbid

    scheme: AnyUrl = Field(
        ...,
        description='Indicates the type of external identifier.',
        title='External Identifier Schema',
    )
    id: str


class MemberOfOrganization(BaseModel):
    __root__: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented identifier reference to another party (person or organization) that this subject is associated with. The UUID of the party in the source OSCAL instance is sufficient to reference the data item locally or globally (e.g., in an imported OSCAL instance).',
        title='Organizational Affiliation',
    )


class OscalApOscalMetadataPartyUuid(BaseModel):
    __root__: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented identifier reference to another party defined in metadata. The UUID of the party in the source OSCAL instance is sufficient to reference the data item locally or globally (e.g., in an imported OSCAL instance).',
        title='Party Reference',
    )


class OscalApOscalMetadataRoleId(BaseModel):
    __root__: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        description='A human-oriented identifier reference to roles served by the user.',
        title='Role Identifier Reference',
    )


class Base64(BaseModel):
    class Config:
        extra = Extra.forbid

    filename: Optional[str] = Field(
        None,
        description='Name of the file before it was encoded as Base64 to be embedded in a resource. This is the name that will be assigned to the file when the file is decoded.',
        title='File Name',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description='Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    value: str


class OscalApOscalMetadataLink(BaseModel):
    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URL reference to a resource.',
        title='Hypertext Reference',
    )
    rel: Optional[constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$')] = Field(
        None,
        description="Describes the type of relationship provided by the link. This can be an indicator of the link's purpose.",
        title='Relation',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description='Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    text: Optional[str] = Field(
        None,
        description='A textual label to associate with the link, which may be used for presentation in a tool.',
        title='Link Text',
    )


class OscalApOscalMetadataHash(BaseModel):
    class Config:
        extra = Extra.forbid

    algorithm: constr(regex=r'^\S(.*\S)?$') = Field(
        ..., description='Method by which a hash is derived', title='Hash algorithm'
    )
    value: str


class OscalApOscalMetadataRemarks(BaseModel):
    __root__: str = Field(
        ...,
        description='Additional commentary on the containing object.',
        title='Remarks',
    )


class OscalApOscalMetadataPublished(BaseModel):
    __root__: datetime = Field(
        ...,
        description='The date and time the document was published. The date-time value must be formatted according to RFC 3339 with full time and time zone included.',
        title='Publication Timestamp',
    )


class OscalApOscalMetadataLastModified(BaseModel):
    __root__: datetime = Field(
        ...,
        description='The date and time the document was last modified. The date-time value must be formatted according to RFC 3339 with full time and time zone included.',
        title='Last Modified Timestamp',
    )


class OscalApOscalMetadataVersion(BaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='A string used to distinguish the current version of the document from other previous (and future) versions.',
        title='Document Version',
    )


class OscalApOscalMetadataOscalVersion(BaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='The OSCAL model version the document was authored against.',
        title='OSCAL version',
    )


class OscalApOscalMetadataEmailAddress(BaseModel):
    __root__: EmailStr = Field(
        ...,
        description='An email address as defined by RFC 5322 Section 3.4.1.',
        title='Email Address',
    )


class OscalApOscalMetadataTelephoneNumber(BaseModel):
    class Config:
        extra = Extra.forbid

    type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None, description='Indicates the type of phone number.', title='type flag'
    )
    number: str


class OscalApOscalMetadataAddrLine(BaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ..., description='A single line of an address.', title='Address line'
    )


class OscalApOscalMetadataDocumentId(BaseModel):
    class Config:
        extra = Extra.forbid

    scheme: Optional[AnyUrl] = Field(
        None,
        description='Qualifies the kind of document identifier using a URI. If the scheme is not provided the value of the element will be interpreted as a string of characters.',
        title='Document Identification Scheme',
    )
    identifier: str


class StatementId(BaseModel):
    __root__: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        description='Used to constrain the selection to only specificity identified statements.',
        title='Include Specific Statements',
    )


class OscalApOscalAssessmentCommonSelectControlById(BaseModel):
    class Config:
        extra = Extra.forbid

    control_id: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        alias='control-id',
        description='A human-oriented identifier reference to a control with a corresponding id value. When referencing an externally defined control, the Control Identifier Reference must be used in the context of the external / imported OSCAL instance (e.g., uri-reference).',
        title='Control Identifier Reference',
    )
    statement_ids: Optional[List[StatementId]] = Field(
        None, alias='statement-ids', min_items=1
    )


class OscalApOscalAssessmentCommonSelectObjectiveById(BaseModel):
    class Config:
        extra = Extra.forbid

    objective_id: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        alias='objective-id',
        description='Points to an assessment objective.',
        title='Objective ID',
    )


class OscalApOscalCatalogCommonIncludeAll(BaseModel):
    pass

    class Config:
        extra = Extra.forbid


class OscalApOscalAssessmentCommonImportSsp(BaseModel):
    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URL reference to the system security plan for the system being assessed.',
        title='System Security Plan Reference',
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class Rlink(BaseModel):
    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URI reference to a resource.',
        title='Hypertext Reference',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description='Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    hashes: Optional[List[OscalApOscalMetadataHash]] = Field(None, min_items=1)


class OscalApOscalMetadataProperty(BaseModel):
    class Config:
        extra = Extra.forbid

    name: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        description="A textual label that uniquely identifies a specific attribute, characteristic, or quality of the property's containing object.",
        title='Property Name',
    )
    uuid: Optional[
        constr(
            regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
        )
    ] = Field(
        None,
        description='A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this defined property elsewhere in this or other OSCAL instances. This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Property Universally Unique Identifier',
    )
    ns: Optional[AnyUrl] = Field(
        None,
        description="A namespace qualifying the property's name. This allows different organizations to associate distinct semantics with the same name.",
        title='Property Namespace',
    )
    value: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='Indicates the value of the attribute, characteristic, or quality.',
        title='Property Value',
    )
    class_: Optional[constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$')] = Field(
        None,
        alias='class',
        description="A textual label that provides a sub-type or characterization of the property's name. This can be used to further distinguish or discriminate between the semantics of multiple properties of the same object with the same name and ns.",
        title='Property Class',
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataResponsibleParty(BaseModel):
    class Config:
        extra = Extra.forbid

    role_id: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        alias='role-id',
        description='A human-oriented identifier reference to roles served by the user.',
        title='Responsible Role',
    )
    party_uuids: List[OscalApOscalMetadataPartyUuid] = Field(
        ..., alias='party-uuids', min_items=1
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataResponsibleRole(BaseModel):
    class Config:
        extra = Extra.forbid

    role_id: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        alias='role-id',
        description='A human-oriented identifier reference to roles responsible for the business function.',
        title='Responsible Role ID',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    party_uuids: Optional[List[OscalApOscalMetadataPartyUuid]] = Field(
        None, alias='party-uuids', min_items=1
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataAddress(BaseModel):
    class Config:
        extra = Extra.forbid

    type: Optional[constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$')] = Field(
        None, description='Indicates the type of address.', title='Address Type'
    )
    addr_lines: Optional[List[OscalApOscalMetadataAddrLine]] = Field(
        None, alias='addr-lines', min_items=1
    )
    city: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='City, town or geographical region for the mailing address.',
        title='City',
    )
    state: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='State, province or analogous geographical region for mailing address',
        title='State',
    )
    postal_code: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='postal-code',
        description='Postal or ZIP code for mailing address',
        title='Postal Code',
    )
    country: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='The ISO 3166-1 alpha-2 country code for the mailing address.',
        title='Country Code',
    )


class ControlSelection(BaseModel):
    class Config:
        extra = Extra.forbid

    description: Optional[str] = Field(
        None,
        description='A human-readable description of in-scope controls specified for assessment.',
        title='Assessed Controls Description',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    include_all: Optional[OscalApOscalCatalogCommonIncludeAll] = Field(
        None, alias='include-all'
    )
    include_controls: Optional[
        List[OscalApOscalAssessmentCommonSelectControlById]
    ] = Field(None, alias='include-controls', min_items=1)
    exclude_controls: Optional[
        List[OscalApOscalAssessmentCommonSelectControlById]
    ] = Field(None, alias='exclude-controls', min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class ControlObjectiveSelection(BaseModel):
    class Config:
        extra = Extra.forbid

    description: Optional[str] = Field(
        None,
        description='A human-readable description of this collection of control objectives.',
        title='Control Objectives Description',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    include_all: Optional[OscalApOscalCatalogCommonIncludeAll] = Field(
        None, alias='include-all'
    )
    include_objectives: Optional[
        List[OscalApOscalAssessmentCommonSelectObjectiveById]
    ] = Field(None, alias='include-objectives', min_items=1)
    exclude_objectives: Optional[
        List[OscalApOscalAssessmentCommonSelectObjectiveById]
    ] = Field(None, alias='exclude-objectives', min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalAssessmentCommonReviewedControls(BaseModel):
    class Config:
        extra = Extra.forbid

    description: Optional[str] = Field(
        None,
        description='A human-readable description of control objectives.',
        title='Control Objective Description',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    control_selections: List[ControlSelection] = Field(
        ..., alias='control-selections', min_items=1
    )
    control_objective_selections: Optional[List[ControlObjectiveSelection]] = Field(
        None, alias='control-objective-selections', min_items=1
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataRevision(BaseModel):
    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(
        None,
        description='A name given to the document revision, which may be used by a tool for display and navigation.',
        title='Document Title',
    )
    published: Optional[OscalApOscalMetadataPublished] = None
    last_modified: Optional[OscalApOscalMetadataLastModified] = Field(
        None, alias='last-modified'
    )
    version: OscalApOscalMetadataVersion
    oscal_version: Optional[OscalApOscalMetadataOscalVersion] = Field(
        None, alias='oscal-version'
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataLocation(BaseModel):
    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this defined location elsewhere in this or other OSCAL instances. The locally defined UUID of the location can be used to reference the data item locally or globally (e.g., from an importing OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Location Universally Unique Identifier',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the location, which may be used by a tool for display and navigation.',
        title='Location Title',
    )
    address: OscalApOscalMetadataAddress
    email_addresses: Optional[List[OscalApOscalMetadataEmailAddress]] = Field(
        None, alias='email-addresses', min_items=1
    )
    telephone_numbers: Optional[List[OscalApOscalMetadataTelephoneNumber]] = Field(
        None, alias='telephone-numbers', min_items=1
    )
    urls: Optional[List[Url]] = Field(None, min_items=1)
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataParty(BaseModel):
    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this defined party elsewhere in this or other OSCAL instances. The locally defined UUID of the party can be used to reference the data item locally or globally (e.g., from an importing OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Party Universally Unique Identifier',
    )
    type: Type = Field(
        ...,
        description='A category describing the kind of party the object describes.',
        title='Party Type',
    )
    name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='The full name of the party. This is typically the legal name associated with the party.',
        title='Party Name',
    )
    short_name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='short-name',
        description='A short common name, abbreviation, or acronym for the party.',
        title='Party Short Name',
    )
    external_ids: Optional[List[ExternalId]] = Field(
        None, alias='external-ids', min_items=1
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    email_addresses: Optional[List[OscalApOscalMetadataEmailAddress]] = Field(
        None, alias='email-addresses', min_items=1
    )
    telephone_numbers: Optional[List[OscalApOscalMetadataTelephoneNumber]] = Field(
        None, alias='telephone-numbers', min_items=1
    )
    addresses: Optional[List[OscalApOscalMetadataAddress]] = Field(None, min_items=1)
    location_uuids: Optional[List[OscalApOscalMetadataLocationUuid]] = Field(
        None, alias='location-uuids', min_items=1
    )
    member_of_organizations: Optional[List[MemberOfOrganization]] = Field(
        None, alias='member-of-organizations', min_items=1
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataRole(BaseModel):
    class Config:
        extra = Extra.forbid

    id: constr(regex=r'^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$') = Field(
        ...,
        description='A human-oriented, locally unique identifier with cross-instance scope that can be used to reference this defined role elsewhere in this or other OSCAL instances. When referenced from another OSCAL instance, the locally defined ID of the Role from the imported OSCAL instance must be referenced in the context of the containing resource (e.g., import, import-component-definition, import-profile, import-ssp or import-ap). This ID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Role Identifier',
    )
    title: str = Field(
        ...,
        description='A name given to the role, which may be used by a tool for display and navigation.',
        title='Role Title',
    )
    short_name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='short-name',
        description='A short common name, abbreviation, or acronym for the role.',
        title='Role Short Name',
    )
    description: Optional[str] = Field(
        None,
        description="A summary of the role's purpose and associated responsibilities.",
        title='Role Description',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class Citation(BaseModel):
    class Config:
        extra = Extra.forbid

    text: str = Field(
        ..., description='A line of citation text.', title='Citation Text'
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)


class Resource(BaseModel):
    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this defined resource elsewhere in this or other OSCAL instances. This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Resource Universally Unique Identifier',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the resource, which may be used by a tool for display and navigation.',
        title='Resource Title',
    )
    description: Optional[str] = Field(
        None,
        description='A short summary of the resource used to indicate the purpose of the resource.',
        title='Resource Description',
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    document_ids: Optional[List[OscalApOscalMetadataDocumentId]] = Field(
        None, alias='document-ids', min_items=1
    )
    citation: Optional[Citation] = Field(
        None,
        description='A citation consisting of end note text and optional structured bibliographic data.',
        title='Citation',
    )
    rlinks: Optional[List[Rlink]] = Field(None, min_items=1)
    base64: Optional[Base64] = Field(
        None,
        description='The Base64 alphabet in RFC 2045 - aligned with XSD.',
        title='Base64',
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalMetadataBackMatter(BaseModel):
    class Config:
        extra = Extra.forbid

    resources: Optional[List[Resource]] = Field(None, min_items=1)


class OscalApOscalMetadataMetadata(BaseModel):
    class Config:
        extra = Extra.forbid

    title: str = Field(
        ...,
        description='A name given to the document, which may be used by a tool for display and navigation.',
        title='Document Title',
    )
    published: Optional[OscalApOscalMetadataPublished] = None
    last_modified: OscalApOscalMetadataLastModified = Field(..., alias='last-modified')
    version: OscalApOscalMetadataVersion
    oscal_version: OscalApOscalMetadataOscalVersion = Field(..., alias='oscal-version')
    revisions: Optional[List[OscalApOscalMetadataRevision]] = Field(None, min_items=1)
    document_ids: Optional[List[OscalApOscalMetadataDocumentId]] = Field(
        None, alias='document-ids', min_items=1
    )
    props: Optional[List[OscalApOscalMetadataProperty]] = Field(None, min_items=1)
    links: Optional[List[OscalApOscalMetadataLink]] = Field(None, min_items=1)
    roles: Optional[List[OscalApOscalMetadataRole]] = Field(None, min_items=1)
    locations: Optional[List[OscalApOscalMetadataLocation]] = Field(None, min_items=1)
    parties: Optional[List[OscalApOscalMetadataParty]] = Field(None, min_items=1)
    responsible_parties: Optional[List[OscalApOscalMetadataResponsibleParty]] = Field(
        None, alias='responsible-parties', min_items=1
    )
    remarks: Optional[OscalApOscalMetadataRemarks] = None


class OscalApOscalApAssessmentPlan(BaseModel):
    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[45][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description='A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this assessment plan in this or other OSCAL instances. The locally defined UUID of the assessment plan can be used to reference the data item locally or globally (e.g., in an imported OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',
        title='Assessment Plan Universally Unique Identifier',
    )
    metadata: OscalApOscalMetadataMetadata


class Model(BaseModel):
    class Config:
        extra = Extra.forbid

    assessment_plan: OscalApOscalApAssessmentPlan = Field(..., alias='assessment-plan')