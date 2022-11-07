import os
import json
import tempfile
import shutil
import pathlib
from datetime import datetime
from pathlib import PurePath
from django.db.models import Q
from django.http import HttpResponse, FileResponse
from django.utils.text import slugify
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from wsgiref.util import FileWrapper

from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet, ReadWriteViewSet
from api.controls.serializers.element import DetailedElementSerializer, SimpleElementSerializer, SimpleWriteElementSerializer, \
    WriteElementTagsSerializer, ElementPermissionSerializer, UpdateElementPermissionSerializer, RemoveUserPermissionFromElementSerializer, \
    WriteElementAppointPartySerializer, ElementPartySerializer, DeletePartyAppointmentsFromElementSerializer, CreateMultipleAppointmentsFromRoleIds, \
    ElementRequestsSerializer, ElementSetRequestsSerializer, ElementCreateAndSetRequestSerializer, \
    WriteElementOscalSerializer, ReadElementOscalSerializer, SimpleGetElementByNameSerializer
from controls.models import Element, System
from siteapp.models import Appointment, Party, Proposal, Role, Request, User
from controls.views import ComponentImporter, OSCALComponentSerializer

class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class ElementViewSet(ReadWriteViewSet):
    queryset = Element.objects.all()
    serializer_classes = SerializerClasses(retrieve=DetailedElementSerializer,
                                           list=SimpleElementSerializer,
                                           create=SimpleWriteElementSerializer,
                                           update=SimpleWriteElementSerializer,
                                           destroy=SimpleWriteElementSerializer,
                                           tags=WriteElementTagsSerializer,
                                           getElementsByName=SimpleGetElementByNameSerializer,
                                           retrieveParties=ElementPartySerializer,
                                           appointments=WriteElementAppointPartySerializer,
                                           removeAppointments=WriteElementAppointPartySerializer,
                                           removeAppointmentsByParty=DeletePartyAppointmentsFromElementSerializer,
                                           CreateAndSet=CreateMultipleAppointmentsFromRoleIds,
                                           retrieveRequests=ElementRequestsSerializer,
                                           setRequest=ElementSetRequestsSerializer,
                                           CreateAndSetRequest=ElementCreateAndSetRequestSerializer,
                                           createOSCAL=WriteElementOscalSerializer,
                                           getOSCAL=ReadElementOscalSerializer,
                                           downloadOSCAL=ReadElementOscalSerializer)

    @action(detail=False, url_path="createOSCAL", methods=["POST"])
    def createOSCAL(self, request, **kwargs):
        # Create component
        title = 'none'
        if "metadata" in request.data["oscal"]["component-definition"]:
            title = request.data["oscal"]["component-definition"]["metadata"]["title"]
        date_string = datetime.now().strftime("%Y-%m-%d-%H-%M")
        
        import_record_name = title + "_api-import_" + date_string
        oscal_component_json = json.dumps(request.data["oscal"])
        
        import_record_result = ComponentImporter().import_components_as_json(import_record_name, oscal_component_json, request)
        element = Element.objects.filter(import_record=import_record_result).first()
        
        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)
    
    # TODO: update component with new OSCAL file - add revision, new uuid, etc
    # @action(detail=True, url_path="updateOSCAL", methods=["PUT"])
    # def updateOSCAL(self, request, **kwargs):
    #     element, validated_data = self.validate_serializer_and_get_object(request)
    #     print("UPDATING COMPONENT USING OSCAL-JSON")
    #     
    #     element.save()

    #     serializer_class = self.get_serializer_class('retrieve')
    #     serializer = self.get_serializer(serializer_class, element)
    #     return Response(serializer.data)

    @action(detail=True, url_path="getOSCAL", methods=["GET"])
    def getOSCAL(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        impl_smts = element.statements_produced.filter(consumer_element=element)
        oscal_string = OSCALComponentSerializer(element, impl_smts).as_json()

        # serializer_class = self.get_serializer_class('retrieve')
        # serializer = self.get_serializer(serializer_class, element)
        oscal = json.loads(oscal_string)
        return Response(oscal)

    @action(detail=True, url_path="downloadOSCAL", methods=["GET"])
    def downloadOSCAL(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        impl_smts = element.statements_produced.filter(consumer_element=element)
        oscal_string = OSCALComponentSerializer(element, impl_smts).as_json()
        oscal = json.loads(oscal_string)

        # Creating oscal json file name
        title = 'none'
        if "metadata" in oscal["component-definition"]:
            title = oscal["component-definition"]["metadata"]["title"]
        else:
            if element.full_name:
                title = element.full_name
            else:
                title = element.name

        date_string = datetime.now().strftime("%Y-%m-%d-%H-%M")
        oscal_json_filename = title + "_oscal_" + date_string + ".json"

        # Download link TODO: Figure out how to download immediately from Execution
        response = HttpResponse(oscal_string, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="%s"' % oscal_json_filename
        return response

    @action(detail=True, url_path="tags", methods=["PUT"])
    def tags(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        element.tags.clear()
        element.tags.add(*validated_data['tags'])
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=False, url_path="getElementsByName", methods=["POST"])
    def getElementsByName(self, request, **kwargs):
        nameSearch = request.data['nameSearch']
        elements = Element.objects.filter(Q(name__icontains=nameSearch) | Q(full_name__icontains=nameSearch))

        serialized_queryset = []
        serializer_class = self.get_serializer_class('list')
        for element in elements:
            serializer = self.get_serializer(serializer_class, element)
            serialized_queryset.append(serializer.data)

        return Response(serialized_queryset)

    @action(detail=True, url_path="retrieveParties", methods=["GET"])
    def retrieveParties(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        element.save()
        
        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)
    
    @action(detail=True, url_path="appointments", methods=["PUT"])
    def appointments(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        for key, value in validated_data.items():
            element.add_appointments(value)
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=True, url_path="removeAppointments", methods=["PUT"])
    def removeAppointments(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        for key, value in validated_data.items():
            element.remove_appointments(value)
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=True, url_path="removeAppointmentsByParty", methods=["PUT"])
    def removeAppointmentsByParty(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        for key, value in validated_data.items():
            for party in element.appointments.filter(party_id=value):
                element.remove_appointments([party.id])
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=True, url_path="CreateAndSet", methods=["POST"])
    def CreateAndSet(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        createdAppointments = []

        # expects this object type:
        # {
        #   "role_ids": {
        #    "party_id": 3,
        #    "roles": [1,2]
        #    }
        # }
        
        for key, value in validated_data.items():
            for val in value['roles']: 
                createExample = Appointment.objects.create(
                    party=Party.objects.get(id=value['party_id']), 
                    role=Role.objects.get(id=val), 
                    model_name="element", 
                    comment="Assigning new role")
                createExample.save()
                createdAppointments.append(createExample.id)
            
        element.add_appointments(createdAppointments)
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)
    
    @action(detail=True, url_path="retrieveRequests", methods=["GET"])
    def retrieveRequests(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        element.save()

        serializer_class = self.get_serializer_class('retrieveRequests')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)
    
    @action(detail=True, url_path="setRequest", methods=["PUT"])
    def setRequest(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        for key, value in validated_data.items():
            element.add_requests(value)
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=True, url_path="CreateAndSetRequest", methods=["POST"])
    def CreateAndSetRequest(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        prop = Proposal.objects.get(id=validated_data['proposalId'])
        newRequest = Request.objects.create(
            user=User.objects.get(id=validated_data['userId']),
            system=System.objects.get(id=validated_data['systemId']),
            requested_element=element,
            criteria_comment=validated_data['criteria_comment'],
            criteria_reject_comment=validated_data['criteria_reject_comment'],
            status=validated_data['status'],
        )
        newRequest.save()
        prop.req = newRequest
        prop.save()
        element.add_requests([newRequest.id])
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)


class ElementWithPermissionsViewSet(ReadWriteViewSet):
    # NESTED_ROUTER_PKS = [{'pk': 'modules_pk', 'model_field': 'module', 'model': Module}]
    queryset = Element.objects.all()
    # ordering = ('definition_order',)
    serializer_classes = SerializerClasses(retrieve=ElementPermissionSerializer,
                                           list=ElementPermissionSerializer,
                                           create=UpdateElementPermissionSerializer,
                                           update=UpdateElementPermissionSerializer,
                                           destroy=UpdateElementPermissionSerializer,
                                           assign_role=UpdateElementPermissionSerializer,
                                           remove_user=RemoveUserPermissionFromElementSerializer)

    @action(detail=True, url_path="assign_role", methods=["PUT"])
    def assign_role(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)

        # assign permissions to user on element
        user_permissions = []
        perm_user = {}

        for key, value in validated_data.items():
            perm_user = value['user']
            if(value['add']):
                user_permissions.append('add_element')
            if(value['change']):
                user_permissions.append('change_element')
            if(value['delete']):
                user_permissions.append('delete_element')
            if(value['view']):
                user_permissions.append('view_element')

        user = User.objects.get(id=perm_user['id'])
        element.assign_user_permissions(user, user_permissions)
        element.save()

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)

    @action(detail=True, url_path="remove_user", methods=["PUT"])
    def remove_user(self, request, **kwargs):
        element, validated_data = self.validate_serializer_and_get_object(request)
        userId = None
        for key, value in validated_data.items():
            userId = value['id']

        user = User.objects.get(id=userId)
        element.remove_all_permissions_from_user(user)

        serializer_class = self.get_serializer_class('retrieve')
        serializer = self.get_serializer(serializer_class, element)
        return Response(serializer.data)