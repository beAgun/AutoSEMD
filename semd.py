from typing import \
    Union

from lxml import \
    etree
from lxml.etree import \
    _Element

namespaces = {
    "ns": "urn:hl7-org:v3",
    "identity": "urn:hl7-ru:identity",
    "address": "urn:hl7-ru:address",
    "fias": "urn:hl7-ru:fias"
}

headers_base_value = {
    "/ns:ClinicalDocument/ns:id": {
        "root": "{org_oid}.100.{mis_number}.51.{system}",
        "extension": "{parent_id}"
    },
    "/ns:ClinicalDocument/ns:setId": {
        "root": "{org_oid}.100.{mis_number}.50.{system}",
        "extension": "{parent_id}"
    },
    "/ns:ClinicalDocument/ns:versionNumber": {
            "value": "{parent_version}"
        },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[1]": {
        "root": "{org_oid}.100.{mis_number}.10.{system}",
        "extension": "{client_id}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[2]": {
        "root": "{org_oid}.100.{mis_number}.10.{system}",
        "extension": "{client_id}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IdentityCardType": {
        "code": "{recordTarget_IdentityCardType_code}",
        "displayName": "{recordTarget_IdentityCardType_displayName}",
        "codeSystem": "{recordTarget_IdentityCardType_codeSystem}",
        "codeSystemName": "{recordTarget_IdentityCardType_codeSystemName}",
        "codeSystemVersion": "{recordTarget_IdentityCardType_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Series":
    {
       "text": "{recordTarget_Series}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Number":
    {
        "text": "{recordTarget_Number}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgName":
    {
        "text": "{recordTarget_IssueOrgName}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgCode":
    {
        "text": "{recordTarget_IssueOrgCode}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueDate":
    {
        "value": "{recordTarget_IssueDate}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:InsurancePolicyType":
    {
        "code": "{recordTarget_InsurancePolicy_code}",
        "displayName": "{recordTarget_InsurancePolicy_displayName}",
        "codeSystem": "{recordTarget_InsurancePolicy_codeSystem}",
        "codeSystemName": "{recordTarget_InsurancePolicy_codeSystemName}",
        "codeSystemVersion": "{recordTarget_InsurancePolicy_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:Number":
    {
        "text": "{recordTarget_Number}",

    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:Type":
    {
        "code": "{recordTarget__addr1_Type_code}",
        "displayName": "{recordTarget__addr1_Type_displayName}",
        "codeSystem": "{recordTarget__addr1_Type_codeSystem}",
        "codeSystemName": "{recordTarget__addr1_Type_codeSystemName}",
        "codeSystemVersion": "{recordTarget__addr1_Type_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:streetAddressLine":
    {
        "text": "{recordTarget__addr1_streetAddressLine}",
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:stateCode":
    {
        "code": "{recordTarget__addr1_stateCode_code}",
        "displayName": "{recordTarget__addr1_stateCode_displayName}",
        "codeSystem": "{recordTarget__addr1_stateCode_codeSystem}",
        "codeSystemName": "{recordTarget__addr1_stateCode_codeSystemName}",
        "codeSystemVersion": "{recordTarget__addr1_stateCode_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:residentCode":
    {
        "code": "{recordTarget__addr1_residentCode_code}",
        "displayName": "{recordTarget__addr1_residentCode_displayName}",
        "codeSystem": "{recordTarget__addr1_residentCode_codeSystem}",
        "codeSystemName": "{recordTarget__addr1_residentCode_codeSystemName}",
        "codeSystemVersion": "{recordTarget__addr1_residentCode_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:postalCode":
    {
        "code": "{recordTarget__addr1_residentCode_code}",
        "displayName": "{recordTarget__addr1_residentCode_displayName}",
        "codeSystem": "{recordTarget__addr1_residentCode_codeSystem}",
        "codeSystemName": "{recordTarget__addr1_residentCode_codeSystemName}",
        "codeSystemVersion": "{recordTarget__addr1_residentCode_codeSystemVersion}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:AOGUID":
    {
        "text": "{recordTarget__addr1_fias_Address_fias_AOGUID}",
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:HOUSEGUID":
    {
        "text": "{recordTarget__addr1_fias_Address_fias_HOUSEGUID}",
    },





}


root = etree.parse('Эпикриз в стационаре выписной.xml')

for header_key, header_value in headers_base_value.items():
    el: Union[_Element, None] = next(iter(root.xpath(header_key, namespaces=namespaces)), None)
    if el is not None:
        if type(header_value) == dict :
            for attr_name, attr_value in header_value.items():
                if attr_name in el.attrib:
                    el.set(attr_name, attr_value)
                elif attr_name == "text":
                    el.text = attr_value


root.write('Измененный_Эпикриз.xml', pretty_print=True, xml_declaration=True, encoding="UTF-8")


# org_oid = sql(ORG_ID_STMT, compos=1)
# mis_number = "SELECT * FROM ..."
# id_org_number = "SELECT * FROM ..."
# system = "SELECT * FROM ..."
# parent_id = "SELECT * FROM ..."
#
# count_res =