Users, Organizations, Projects, Folders, and Invitations
========================================================

The diagram below provides a summary representation of GovReady-Q’s
Django ``siteapp`` data model, which handles users, organizations,
projects and folders, and invitations.

.. figure:: assets/govready-q-siteapp-erd.png
   :alt: Siteapp data model (not all tables represented)

   Siteapp data model (not all tables represented)

The siteapp data model represents users who have membership in different
projects. Users must be invited to projects. Projects belong to
organizations.

Access control is based on organization and projects. Information cannot
be shared across organizations and only limited information can be
shared across projects within an organization.
