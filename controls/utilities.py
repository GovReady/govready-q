# Utility functions

def replace_line_breaks(text, break_src="\n", break_trg="<br />"):
    """ replace one type of line break with another in text block """
    if text is None:
    	return ""
    if break_src in text:
        return break_trg.join(text.split(break_src))
    else:
        return text

def replace_unicodes(text):
	""" replace various unicodes characters """
	text = text.replace(u'\ufffd', "'")
	return text

def use_org_name(text, org_name):
    """ replace 'The organization' with org_name """
    if org_name is not None:
        text = text.replace(u'The organization', "The organization %s" % org_name)
        return text
    else:
        return text

def replace_assignments(text, project):
    """ if assigments are defined replace them with value from system-security-plan.yaml """
    # for now do something hacking to prove it works
    text = text.replace(u'[Assignment: organization-defined audit record storage requirements]', project['assignments']['organization-defined-audit-record-storage-requirements'] )
    return text

def replace_colons(text, project):
    """ replace colons with &colon; """
    # for now do something hacking to prove it works
    text = text.replace(u':', "&colon;")
    return text