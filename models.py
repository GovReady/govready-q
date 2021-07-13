INFO: ALLOWED_HOSTS ['localhost', 'http://127.0.0.1:8000', 'http://127.0.0.1', '*']
INFO: Connection scheme is 'http'.
INFO: 'SITE_ROOT_URL' set to http://localhost:8000 
INFO: GR_PDF_GENERATOR set to wkhtmltopdf
INFO: GR_IMG_GENERATOR set to wkhtmltopdf
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountEmailaddress(models.Model):
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    email = models.CharField(max_length=254)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'),)


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class ControlsCommoncontrol(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=255)
    oscal_ctl_id = models.CharField(max_length=20, blank=True, null=True)
    legacy_imp_smt = models.TextField(blank=True, null=True)
    common_control_provider = models.ForeignKey('ControlsCommoncontrolprovider', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_commoncontrol'


class ControlsCommoncontrolprovider(models.Model):
    description = models.CharField(max_length=255)
    name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'controls_commoncontrolprovider'


class ControlsDeployment(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=255)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    inventory_items = models.TextField(blank=True, null=True)
    system = models.ForeignKey('ControlsSystem', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_deployment'


class ControlsElement(models.Model):
    name = models.CharField(unique=True, max_length=250)
    full_name = models.CharField(max_length=250, blank=True, null=True)
    element_type = models.CharField(max_length=150, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    import_record = models.ForeignKey('ControlsImportrecord', models.DO_NOTHING, blank=True, null=True)
    component_state = models.CharField(max_length=50, blank=True, null=True)
    component_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'controls_element'


class ControlsElementRoles(models.Model):
    element = models.ForeignKey(ControlsElement, models.DO_NOTHING)
    elementrole = models.ForeignKey('ControlsElementrole', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_element_roles'
        unique_together = (('element', 'elementrole'),)


class ControlsElementTags(models.Model):
    element = models.ForeignKey(ControlsElement, models.DO_NOTHING)
    tag = models.ForeignKey('SiteappTag', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_element_tags'
        unique_together = (('element', 'tag'),)


class ControlsElementcommoncontrol(models.Model):
    oscal_ctl_id = models.CharField(max_length=20, blank=True, null=True)
    oscal_catalog_key = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    common_control = models.ForeignKey(ControlsCommoncontrol, models.DO_NOTHING)
    element = models.ForeignKey(ControlsElement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_elementcommoncontrol'
        unique_together = (('element', 'common_control', 'oscal_ctl_id', 'oscal_catalog_key'),)


class ControlsElementcontrol(models.Model):
    oscal_ctl_id = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    oscal_catalog_key = models.CharField(max_length=100, blank=True, null=True)
    smts_updated = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(max_length=32)
    element = models.ForeignKey(ControlsElement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_elementcontrol'
        unique_together = (('element', 'oscal_ctl_id', 'oscal_catalog_key'),)


class ControlsElementrole(models.Model):
    role = models.CharField(unique=True, max_length=250)
    description = models.CharField(max_length=255)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'controls_elementrole'


class ControlsHistoricaldeployment(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=255)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    inventory_items = models.TextField(blank=True, null=True)
    history_id = models.AutoField(primary_key=True)
    history_date = models.DateTimeField()
    history_change_reason = models.CharField(max_length=100, blank=True, null=True)
    history_type = models.CharField(max_length=1)
    history_user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)
    system_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_historicaldeployment'


class ControlsHistoricalstatement(models.Model):
    id = models.IntegerField()
    sid = models.CharField(max_length=100, blank=True, null=True)
    sid_class = models.CharField(max_length=200, blank=True, null=True)
    pid = models.CharField(max_length=20, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    history_id = models.AutoField(primary_key=True)
    history_date = models.DateTimeField()
    history_change_reason = models.CharField(max_length=100, blank=True, null=True)
    history_type = models.CharField(max_length=1)
    consumer_element_id = models.IntegerField(blank=True, null=True)
    history_user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)
    import_record_id = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    producer_element_id = models.IntegerField(blank=True, null=True)
    prototype_id = models.IntegerField(blank=True, null=True)
    statement_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_historicalstatement'


class ControlsHistoricalsystemassessmentresult(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=250)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    assessment_results = models.TextField(blank=True, null=True)
    history_id = models.AutoField(primary_key=True)
    history_date = models.DateTimeField()
    history_change_reason = models.CharField(max_length=100, blank=True, null=True)
    history_type = models.CharField(max_length=1)
    deployment_id = models.IntegerField(blank=True, null=True)
    history_user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    system_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_historicalsystemassessmentresult'


class ControlsImportrecord(models.Model):
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_importrecord'


class ControlsPoam(models.Model):
    statement = models.OneToOneField('ControlsStatement', models.DO_NOTHING, blank=True, null=True)
    controls = models.CharField(max_length=254, blank=True, null=True)
    milestone_changes = models.TextField(blank=True, null=True)
    milestones = models.TextField(blank=True, null=True)
    poam_id = models.IntegerField(blank=True, null=True)
    remediation_plan = models.TextField(blank=True, null=True)
    risk_rating_adjusted = models.CharField(max_length=50, blank=True, null=True)
    risk_rating_original = models.CharField(max_length=50, blank=True, null=True)
    scheduled_completion_date = models.DateTimeField(blank=True, null=True)
    weakness_detection_source = models.CharField(max_length=180, blank=True, null=True)
    weakness_name = models.CharField(max_length=254, blank=True, null=True)
    weakness_source_identifier = models.CharField(max_length=180, blank=True, null=True)
    poam_group = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_poam'


class ControlsStatement(models.Model):
    sid = models.CharField(max_length=100, blank=True, null=True)
    sid_class = models.CharField(max_length=200, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    consumer_element = models.ForeignKey(ControlsElement, models.DO_NOTHING, blank=True, null=True)
    producer_element = models.ForeignKey(ControlsElement, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    pid = models.CharField(max_length=20, blank=True, null=True)
    uuid = models.CharField(max_length=32)
    import_record = models.ForeignKey(ControlsImportrecord, models.DO_NOTHING, blank=True, null=True)
    statement_type = models.CharField(max_length=150, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    prototype = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_statement'


class ControlsStatementMentionedElements(models.Model):
    statement = models.ForeignKey(ControlsStatement, models.DO_NOTHING)
    element = models.ForeignKey(ControlsElement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_statement_mentioned_elements'
        unique_together = (('statement', 'element'),)


class ControlsSystem(models.Model):
    fisma_id = models.CharField(max_length=40, blank=True, null=True)
    root_element = models.ForeignKey(ControlsElement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'controls_system'


class ControlsSystemassessmentresult(models.Model):
    name = models.CharField(max_length=250)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=32)
    assessment_results = models.TextField(blank=True, null=True)
    deployment = models.ForeignKey(ControlsDeployment, models.DO_NOTHING, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    system = models.ForeignKey(ControlsSystem, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'controls_systemassessmentresult'


class CookieConsentCookie(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    path = models.TextField()
    domain = models.CharField(max_length=250)
    created = models.DateTimeField()
    cookiegroup = models.ForeignKey('CookieConsentCookiegroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cookie_consent_cookie'


class CookieConsentCookiegroup(models.Model):
    varname = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_required = models.BooleanField()
    is_deletable = models.BooleanField()
    ordering = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cookie_consent_cookiegroup'


class CookieConsentLogitem(models.Model):
    action = models.IntegerField()
    version = models.CharField(max_length=32)
    created = models.DateTimeField()
    cookiegroup = models.ForeignKey(CookieConsentCookiegroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cookie_consent_logitem'


class DbstorageStoredfile(models.Model):
    mime_type = models.CharField(max_length=128, blank=True, null=True)
    value = models.TextField()
    size = models.IntegerField()
    encoded_size = models.IntegerField()
    encoding = models.IntegerField()
    gzipped = models.BooleanField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    trusted = models.BooleanField()
    path = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'dbstorage_storedfile'


class DiscussionAttachment(models.Model):
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    comment = models.ForeignKey('DiscussionComment', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    file = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'discussion_attachment'


class DiscussionComment(models.Model):
    emojis = models.CharField(max_length=256, blank=True, null=True)
    text = models.TextField()
    proposed_answer = models.TextField(blank=True, null=True)
    deleted = models.BooleanField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    discussion = models.ForeignKey('DiscussionDiscussion', models.DO_NOTHING)
    draft = models.BooleanField()
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    replies_to = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discussion_comment'


class DiscussionDiscussion(models.Model):
    attached_to_object_id = models.PositiveIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    attached_to_content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    organization = models.ForeignKey('SiteappOrganization', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'discussion_discussion'
        unique_together = (('attached_to_content_type', 'attached_to_object_id'),)


class DiscussionDiscussionGuests(models.Model):
    discussion = models.ForeignKey(DiscussionDiscussion, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'discussion_discussion_guests'
        unique_together = (('discussion', 'user'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    action_flag = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    name = models.CharField(max_length=50)
    domain = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'django_site'


class GuardianGroupobjectpermission(models.Model):
    object_pk = models.CharField(max_length=255)
    content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guardian_groupobjectpermission'
        unique_together = (('group', 'permission', 'object_pk'),)


class GuardianUserobjectpermission(models.Model):
    object_pk = models.CharField(max_length=255)
    content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guardian_userobjectpermission'
        unique_together = (('user', 'permission', 'object_pk'),)


class GuidedmodulesAppinput(models.Model):
    input_name = models.CharField(max_length=200)
    content_hash = models.CharField(max_length=64)
    file = models.CharField(max_length=100)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    app = models.ForeignKey('GuidedmodulesAppversion', models.DO_NOTHING, blank=True, null=True)
    source = models.ForeignKey('GuidedmodulesAppsource', models.DO_NOTHING)
    input_type = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appinput'
        unique_together = (('source', 'content_hash'),)


class GuidedmodulesAppsource(models.Model):
    slug = models.CharField(unique=True, max_length=200)
    spec = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    trust_assets = models.BooleanField()
    available_to_all = models.BooleanField()
    is_system_source = models.BooleanField()
    available_to_all_individuals = models.BooleanField()
    available_to_role = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'guidedmodules_appsource'


class GuidedmodulesAppsourceAvailableToIndividual(models.Model):
    appsource = models.ForeignKey(GuidedmodulesAppsource, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appsource_available_to_individual'
        unique_together = (('appsource', 'user'),)


class GuidedmodulesAppsourceAvailableToOrgs(models.Model):
    appsource = models.ForeignKey(GuidedmodulesAppsource, models.DO_NOTHING)
    organization = models.ForeignKey('SiteappOrganization', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appsource_available_to_orgs'
        unique_together = (('appsource', 'organization'),)


class GuidedmodulesAppversion(models.Model):
    appname = models.CharField(max_length=200)
    source = models.ForeignKey(GuidedmodulesAppsource, models.DO_NOTHING)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    catalog_metadata = models.TextField()
    version_name = models.CharField(max_length=128, blank=True, null=True)
    version_number = models.CharField(max_length=128, blank=True, null=True)
    asset_paths = models.TextField()
    trust_assets = models.BooleanField()
    show_in_catalog = models.BooleanField()
    input_paths = models.TextField(blank=True, null=True)
    trust_inputs = models.BooleanField(blank=True, null=True)
    system_app = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appversion'
        unique_together = (('source', 'appname', 'system_app'),)


class GuidedmodulesAppversionAssetFiles(models.Model):
    appversion = models.ForeignKey(GuidedmodulesAppversion, models.DO_NOTHING)
    moduleasset = models.ForeignKey('GuidedmodulesModuleasset', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appversion_asset_files'
        unique_together = (('appversion', 'moduleasset'),)


class GuidedmodulesAppversionInputArtifacts(models.Model):
    appversion = models.ForeignKey(GuidedmodulesAppversion, models.DO_NOTHING)
    importrecord = models.ForeignKey(ControlsImportrecord, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appversion_input_artifacts'
        unique_together = (('appversion', 'importrecord'),)


class GuidedmodulesAppversionInputFiles(models.Model):
    appversion = models.ForeignKey(GuidedmodulesAppversion, models.DO_NOTHING)
    appinput = models.ForeignKey(GuidedmodulesAppinput, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_appversion_input_files'
        unique_together = (('appversion', 'appinput'),)


class GuidedmodulesInstrumentationevent(models.Model):
    event_time = models.DateTimeField()
    event_type = models.CharField(max_length=32)
    event_value = models.FloatField(blank=True, null=True)
    extra = models.TextField()
    answer = models.ForeignKey('GuidedmodulesTaskanswer', models.DO_NOTHING, blank=True, null=True)
    module = models.ForeignKey('GuidedmodulesModule', models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey('SiteappProject', models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey('GuidedmodulesModulequestion', models.DO_NOTHING, blank=True, null=True)
    task = models.ForeignKey('GuidedmodulesTask', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guidedmodules_instrumentationevent'


class GuidedmodulesModule(models.Model):
    module_name = models.CharField(max_length=200)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    source = models.ForeignKey(GuidedmodulesAppsource, models.DO_NOTHING)
    app = models.ForeignKey(GuidedmodulesAppversion, models.DO_NOTHING, blank=True, null=True)
    spec = models.TextField()
    superseded_by = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guidedmodules_module'
        unique_together = (('app', 'module_name'),)


class GuidedmodulesModuleasset(models.Model):
    content_hash = models.CharField(max_length=64)
    file = models.CharField(max_length=100)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    source = models.ForeignKey(GuidedmodulesAppsource, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_moduleasset'
        unique_together = (('source', 'content_hash'),)


class GuidedmodulesModulequestion(models.Model):
    key = models.CharField(max_length=100)
    definition_order = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    module = models.ForeignKey(GuidedmodulesModule, models.DO_NOTHING)
    answer_type_module = models.ForeignKey(GuidedmodulesModule, models.DO_NOTHING, blank=True, null=True)
    spec = models.TextField()

    class Meta:
        managed = False
        db_table = 'guidedmodules_modulequestion'
        unique_together = (('module', 'key'),)


class GuidedmodulesTask(models.Model):
    title_override = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.TextField()
    editor = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    module = models.ForeignKey(GuidedmodulesModule, models.DO_NOTHING)
    project = models.ForeignKey('SiteappProject', models.DO_NOTHING)
    uuid = models.CharField(max_length=32)
    cached_state = models.TextField()

    class Meta:
        managed = False
        db_table = 'guidedmodules_task'


class GuidedmodulesTaskInvitationHistory(models.Model):
    task = models.ForeignKey(GuidedmodulesTask, models.DO_NOTHING)
    invitation = models.ForeignKey('SiteappInvitation', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_task_invitation_history'
        unique_together = (('task', 'invitation'),)


class GuidedmodulesTaskanswer(models.Model):
    notes = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    question = models.ForeignKey(GuidedmodulesModulequestion, models.DO_NOTHING)
    task = models.ForeignKey(GuidedmodulesTask, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_taskanswer'
        unique_together = (('task', 'question'),)


class GuidedmodulesTaskanswerhistory(models.Model):
    stored_value = models.TextField()
    notes = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    answered_by = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    cleared = models.BooleanField()
    answered_by_file = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.CharField(max_length=100, blank=True, null=True)
    stored_encoding = models.TextField(blank=True, null=True)
    answered_by_method = models.CharField(max_length=3)
    reviewed = models.IntegerField()
    skipped_reason = models.CharField(max_length=24, blank=True, null=True)
    unsure = models.BooleanField()
    taskanswer = models.ForeignKey(GuidedmodulesTaskanswer, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_taskanswerhistory'


class GuidedmodulesTaskanswerhistoryAnsweredByTask(models.Model):
    taskanswerhistory = models.ForeignKey(GuidedmodulesTaskanswerhistory, models.DO_NOTHING)
    task = models.ForeignKey(GuidedmodulesTask, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guidedmodules_taskanswerhistory_answered_by_task'
        unique_together = (('taskanswerhistory', 'task'),)


class NotificationsNotification(models.Model):
    level = models.CharField(max_length=20)
    unread = models.BooleanField()
    actor_object_id = models.CharField(max_length=255)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    public = models.BooleanField()
    action_object_content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING, blank=True, null=True)
    actor_content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING)
    recipient = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    target_content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING, blank=True, null=True)
    deleted = models.BooleanField()
    emailed = models.BooleanField()
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notifications_notification'


class SiteappFolder(models.Model):
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    organization = models.ForeignKey('SiteappOrganization', models.DO_NOTHING)
    description = models.CharField(max_length=512)
    title = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'siteapp_folder'


class SiteappFolderAdminUsers(models.Model):
    folder = models.ForeignKey(SiteappFolder, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_folder_admin_users'
        unique_together = (('folder', 'user'),)


class SiteappFolderProjects(models.Model):
    folder = models.ForeignKey(SiteappFolder, models.DO_NOTHING)
    project = models.ForeignKey('SiteappProject', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_folder_projects'
        unique_together = (('folder', 'project'),)


class SiteappInvitation(models.Model):
    into_project = models.BooleanField()
    target_object_id = models.PositiveIntegerField()
    target_info = models.TextField()
    text = models.TextField()
    sent_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    revoked_at = models.DateTimeField(blank=True, null=True)
    email_invitation_code = models.CharField(max_length=64)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    accepted_user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)
    from_project = models.ForeignKey('SiteappProject', models.DO_NOTHING, blank=True, null=True)
    from_user = models.ForeignKey('SiteappUser', models.DO_NOTHING)
    target_content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING)
    to_user = models.ForeignKey('SiteappUser', models.DO_NOTHING, blank=True, null=True)
    from_portfolio = models.ForeignKey('SiteappPortfolio', models.DO_NOTHING, blank=True, null=True)
    to_email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteapp_invitation'


class SiteappOrganization(models.Model):
    slug = models.CharField(unique=True, max_length=32)
    created = models.DateTimeField()
    extra = models.TextField()
    updated = models.DateTimeField()
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'siteapp_organization'


class SiteappOrganizationHelpSquad(models.Model):
    organization = models.ForeignKey(SiteappOrganization, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_organization_help_squad'
        unique_together = (('organization', 'user'),)


class SiteappOrganizationReviewers(models.Model):
    organization = models.ForeignKey(SiteappOrganization, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_organization_reviewers'
        unique_together = (('organization', 'user'),)


class SiteappOrganizationalsetting(models.Model):
    catalog_key = models.CharField(max_length=255)
    parameter_key = models.CharField(max_length=255)
    organization = models.ForeignKey(SiteappOrganization, models.DO_NOTHING)
    value = models.TextField()

    class Meta:
        managed = False
        db_table = 'siteapp_organizationalsetting'
        unique_together = (('organization', 'catalog_key', 'parameter_key'),)


class SiteappPortfolio(models.Model):
    description = models.CharField(max_length=512)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    title = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'siteapp_portfolio'


class SiteappProject(models.Model):
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    is_account_project = models.BooleanField()
    root_task = models.ForeignKey(GuidedmodulesTask, models.DO_NOTHING, blank=True, null=True)
    is_organization_project = models.BooleanField(blank=True, null=True)
    organization = models.ForeignKey(SiteappOrganization, models.DO_NOTHING, blank=True, null=True)
    portfolio = models.ForeignKey(SiteappPortfolio, models.DO_NOTHING, blank=True, null=True)
    system = models.ForeignKey(ControlsSystem, models.DO_NOTHING, blank=True, null=True)
    version = models.CharField(max_length=32, blank=True, null=True)
    version_comment = models.TextField(blank=True, null=True)
    import_record = models.ForeignKey(ControlsImportrecord, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteapp_project'
        unique_together = (('organization', 'is_organization_project'),)


class SiteappProjectTags(models.Model):
    project = models.ForeignKey(SiteappProject, models.DO_NOTHING)
    tag = models.ForeignKey('SiteappTag', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_project_tags'
        unique_together = (('project', 'tag'),)


class SiteappProjectasset(models.Model):
    title = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=255)
    file = models.CharField(max_length=100)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    extra = models.TextField()
    uuid = models.CharField(max_length=32)
    default = models.BooleanField()
    project = models.ForeignKey(SiteappProject, models.DO_NOTHING)
    content_hash = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'siteapp_projectasset'
        unique_together = (('title', 'project'),)


class SiteappProjectmembership(models.Model):
    is_admin = models.BooleanField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    project = models.ForeignKey(SiteappProject, models.DO_NOTHING)
    user = models.ForeignKey('SiteappUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_projectmembership'
        unique_together = (('project', 'user'),)


class SiteappSupport(models.Model):
    email = models.CharField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteapp_support'


class SiteappTag(models.Model):
    label = models.CharField(unique=True, max_length=100)
    system_created = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'siteapp_tag'


class SiteappUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(unique=True, max_length=150)
    notifemails_enabled = models.IntegerField()
    notifemails_last_at = models.DateTimeField(blank=True, null=True)
    notifemails_last_notif_id = models.PositiveIntegerField()
    api_key_ro = models.CharField(unique=True, max_length=32, blank=True, null=True)
    api_key_rw = models.CharField(unique=True, max_length=32, blank=True, null=True)
    api_key_wo = models.CharField(unique=True, max_length=32, blank=True, null=True)
    default_portfolio = models.ForeignKey(SiteappPortfolio, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteapp_user'


class SiteappUserGroups(models.Model):
    user = models.ForeignKey(SiteappUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_user_groups'
        unique_together = (('user', 'group'),)


class SiteappUserUserPermissions(models.Model):
    user = models.ForeignKey(SiteappUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'siteapp_user_user_permissions'
        unique_together = (('user', 'permission'),)


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=30)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    user = models.ForeignKey(SiteappUser, models.DO_NOTHING)
    extra_data = models.TextField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


class SystemSettingsClassification(models.Model):
    status = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'system_settings_classification'


class SystemSettingsSitename(models.Model):
    sitename = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'system_settings_sitename'


class SystemSettingsSystemsettings(models.Model):
    setting = models.CharField(unique=True, max_length=200)
    active = models.BooleanField()
    time_out = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'system_settings_systemsettings'
