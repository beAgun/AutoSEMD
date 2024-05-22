import re
from typing import Union, Iterator
from lxml import etree
from lxml.etree import _Element




# Определение пространства имен XML
namespaces = {
    "ns": "urn:hl7-org:v3",
    "identity": "urn:hl7-ru:identity",
    "address": "urn:hl7-ru:address",
    "fias": "urn:hl7-ru:fias"
}
# Определение базовых значений заголовков с регулярными выражениями для валидации
headers_base_value = {
    "/ns:ClinicalDocument/ns:id": {
        "root": {
            "@value": "{ns_ClinicalDocument_ns_id_root}", # {org_oid}.100.{mis_number}.51.{system}
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.51$",
        },
        "extension": {
            "@value": "{parent_id}",
            "type": r"\d+"
        }
    },
    "/ns:ClinicalDocument/ns:setId": {
        "root": {
            "@value": "ns_ClinicalDocument_ns_setId_root" # {org_oid}.100.{mis_number}.50.{system}
        },
        "extension": {
            "@value": "{parent_id}"
        }
    },
    "/ns:ClinicalDocument/ns:versionNumber": {
            "value": {
                "@value": "{parent_version}"
            }
        },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[1]": {
        "root": {
            "@value": "ns_ClinicalDocument_ns_recordTarget_ns_patientRole_ns_id1_root" # {org_oid}.100.{mis_number}.10.{system}
        },
        "extension": {
            "@value": "{client_id}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[2]": {
        "root": {
            "@value": "{org_oid}.100.{mis_number}.10.{system}"
        },
        "extension": {
            "@value": "{client_id}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IdentityCardType": {
        "code": {
            "@value": "{recordTarget_IdentityCardType_code}"
        },
        "displayName": {
            "@value": "{recordTarget_IdentityCardType_displayName}"
        },
        "codeSystem": {
            "@value": "{recordTarget_IdentityCardType_codeSystem}"
        },
        "codeSystemName": {
            "@value": "{recordTarget_IdentityCardType_codeSystemName}"
        },
        "codeSystemVersion": {
            "@value": "{recordTarget_IdentityCardType_codeSystemVersion}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Series":
    {
       "text": {
           "@value": "{recordTarget_Series}"
       }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Number":
    {
        "text": {
            "@value": "{recordTarget_Number}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgName":
    {
        "text": {
            "@value": "{recordTarget_IssueOrgName}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgCode":
    {
        "text": {
            "@value": "{recordTarget_IssueOrgCode}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueDate":
    {
        "@value": "{recordTarget_IssueDate}"
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:InsurancePolicyType":
    {
        "code": {
            "@value": "{recordTarget_InsurancePolicy_code}"
        },
        "displayName": {
            "@value": "{recordTarget_InsurancePolicy_displayName}"
        },
        "codeSystem": {
            "@value": "{recordTarget_InsurancePolicy_codeSystem}"
        },
        "codeSystemName": {
            "@value": "{recordTarget_InsurancePolicy_codeSystemName}"
        },
        "codeSystemVersion": {
            "@value": "{recordTarget_InsurancePolicy_codeSystemVersion}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:Number":
    {
        "text": {
            "@value": "{recordTarget_Number}"
        },

    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:Type":
    {
        "code": {
            "@value": "{recordTarget_addr1_Type_code}"
        },
        "displayName": {
            "@value": "{recordTarget_addr1_Type_displayName}"
        },
        "codeSystem": {
            "@value": "{recordTarget_addr1_Type_codeSystem}"
        },
        "codeSystemName": {
            "@value": "{recordTarget_addr1_Type_codeSystemName}"
        },
        "codeSystemVersion": {
            "@value": "{recordTarget_addr1_Type_codeSystemVersion}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:streetAddressLine":
    {
        "text": {
            "@value": "{recordTarget_addr1_streetAddressLine}"
        },
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:stateCode":
    {
        "code": {
            "@value": "{recordTarget_addr1_stateCode_code}"
        },
        "displayName": {
            "@value": "{recordTarget_addr1_stateCode_displayName}"
        },
        "codeSystem": {
            "@value": "{recordTarget_addr1_stateCode_codeSystem}"
        },
        "codeSystemName": {
            "@value": "{recordTarget_addr1_stateCode_codeSystemName}"
        },
        "codeSystemVersion": {
            "@value": "{recordTarget_addr1_stateCode_codeSystemVersion}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:residentCode":
    {
        "code": {
            "@value": "{recordTarget_addr1_residentCode_code}"
        },
        "displayName": {
            "@value": "{recordTarget_addr1_residentCode_displayName}"
        },
        "codeSystem": {
            "@value": "{recordTarget_addr1_residentCode_codeSystem}"
        },
        "codeSystemName": {
            "@value": "{recordTarget_addr1_residentCode_codeSystemName}"
        },
        "codeSystemVersion": {
            "@value": "{recordTarget_addr1_residentCode_codeSystemVersion}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:postalCode":
    {
        "text": {
            "@value": "{recordTarget_addr1_postalCode}"
        }
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:AOGUID":
    {
        "text": {
            "@value": "{recordTarget_addr1_fias_Address_fias_AOGUID}"
        },
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:HOUSEGUID":
    {
        "text": {
            "@value": "{recordTarget_addr1_fias_Address_fias_HOUSEGUID}"
        },
    },
}

# для теста
headers_base_value = {
    "/ns:ClinicalDocument/ns:id": {
        "root": {
            "@value": "{ns_ClinicalDocument_ns_id_root}",  # {org_oid}.100.{mis_number}.51.{system}
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.51$"
        },
        "extension": {
            "@value": "{parent_id}",
            "@type": r"\d+"
        }
    }
}

# Пути к SEMD для различных OID
semd_paths = {
    "147": r"V:\ProjectPython\AutoSemd\Эпикриз в стационаре выписной.xml"
}

# TODO: Временное решение
# Шаблоны базы данных для SQL-запросов и комментариев
DATABASE_TEMPLATE = {
    "1": {
        "name": "ns_ClinicalDocument_ns_id_root",
        "alias": "doc_id",
        "sql": "SELECT doc_id",
        "comment": "Уникальный идентификатор документа"
    },
    "2": {
        "name": "parent_id",
        "alias": "extention",
        "sql": "SELECT extention",
        "comment": "Уникальный идентификатор документа"
    }
}

# TODO: Временное решение
# Шаблон с предопределенными результатами запросов к базе данных
OTHER_DATABASE_TEMPLATE = {
    "SELECT doc_id": "1.2.643.5.1.13.13.12.2.66.6770.100.1.1.51",
    "SELECT extention": ""
}

# TODO: Временное решение
def find_by_name(name: str) -> Union[str, None]:
    """
    Найти SQL-запрос по имени поля.

    :param name: Имя поля в шаблоне базы данных.
    :return: SQL-запрос или None, если имя не найдено.
    """
    for _, sql in DATABASE_TEMPLATE.items():
        if sql["name"] == name:
            return sql["sql"]
    return None


class Type:
    """
    Класс для обработки валидации типа с использованием регулярных выражений.
    """

    def __init__(self, regexp: re.Pattern):
        """
        Инициализация объекта Type.

        :param regexp: Регулярное выражение для валидации.
        """
        self.regexp = regexp

    def __call__(self, target: str) -> bool:
        """
        Проверить, соответствует ли целевая строка регулярному выражению.

        :param target: Целевая строка для проверки.
        :return: True, если строка соответствует регулярному выражению, иначе False.
        """
        return self.regexp.search(target) is not None


class SEMDField:
    """
    Класс, представляющий одно поле внутри SEMD.
    """

    def __init__(self, **kwargs):
        """
        Инициализация объекта SEMDField.

        :param kwargs: Аргументы, определяющие атрибуты и значения поля.
        """
        for k, v in kwargs.items():
            setattr(self, k.replace("@", ""), v)
        self.value = kwargs.get("@value", "").replace("{", "").replace("}", "")
        self.type = Type(re.compile(kwargs.get("@type", r'^.+$')))

    def __call__(self, *args, **kwargs) -> bool:
        """
        Валидировать значение поля.

        :return: True, если значение поля соответствует типу, иначе False.
        """
        return self.type(self.value)


class SEMDFields:
    """
    Класс, представляющий коллекцию полей SEMD.
    """

    def __init__(self):
        """
        Инициализация объекта SEMDFields.
        """
        self.semd_fields: list[SEMDField] = []

    def append(self, field: dict):
        """
        Добавить новое поле SEMD в коллекцию.

        :param field: Словарь, содержащий атрибуты и значения поля.
        """
        self.semd_fields.append(SEMDField(**field))

    def __iter__(self) -> Iterator[SEMDField]:
        """
        Итерация по коллекции полей SEMD.

        :return: Итератор полей SEMD.
        """
        return iter(self.semd_fields)


class SEMD:
    """
    Класс для обработки SEMD XML документа.
    """

    def __init__(self, oid: str):
        """
        Инициализация объекта SEMD.

        :param oid: Идентификатор объекта (OID).
        """
        self.oid = str(oid)
        self.xml_path: str = semd_paths.get(self.oid, None)
        self.xml_doc = self._create_header_xml() if self.xml_path else None

    def _create_header_xml(self) -> _Element:
        """
        Создать XML заголовок на основе предопределенных headers_base_value.

        :return: Корневой элемент XML.
        """
        root = etree.parse(self.xml_path)
        self._semd_fields: SEMDFields = SEMDFields()

        # Проход по заголовкам для заполнения полей SEMD и обновления XML
        for header_key, header_value in headers_base_value.items():
            el: Union[_Element, None] = next(iter(root.xpath(header_key, namespaces=namespaces)), None)

            if el is not None:
                for attr_name, attr_value in header_value.items():
                    self._semd_fields.append(attr_value)
                    if attr_name in el.attrib:
                        el.set(attr_name, attr_value["@value"])
                    elif attr_name == "text":
                        el.text = attr_value["@value"]

        return root

    def save(self):
        """
        Сохранить измененный XML документ в файл.
        """
        with open("target.xml", "wb") as f:
            f.write(etree.tostring(self.xml_doc, pretty_print=True, xml_declaration=True, encoding="utf-8"))

    def __call__(self, *args, **kwargs) -> _Element:
        """
        Обработать поля SEMD и заполнить их значениями из базы данных.

        :return: Измененный XML документ.
        :raises: ValueError, если валидация одного из полей не удалась.
        """
        for field in self._semd_fields:
            result = OTHER_DATABASE_TEMPLATE.get(find_by_name(field.value), "")

            if not field.type(result):
                break

            field.__setattr__("in_xml", result)
        else:
            temp_xml_doc = etree.tostring(self.xml_doc, encoding="unicode")
            temp_xml_doc = temp_xml_doc.format(**{filed.value: filed.in_xml for filed in self._semd_fields})
            self.xml_doc = etree.fromstring(temp_xml_doc)
            return self.xml_doc

        raise ValueError("Валидация не прошла для одного из полей")


# Создание и обработка объекта SEMD
a = SEMD("147")
a()
a.save()
