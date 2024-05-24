import re
from typing import Union, Iterator, Iterable

from lxml import etree
from lxml.etree import _Element

from sqlalchemy import create_engine, text

DATABASES = {
    "p51vms": {
        "engine": "mysql+mysqldb",
        "user": "dbuser",
        "password": "dbpassword",
        "host": "p51vms",
        "port": 3306,
        "database": "s11",
        "charset": "utf8",
        "IEMK_ORG_ID": 3196,
        "B15_MODE": False,
    }
}

DATABASE_CONFIG = DATABASES["p51vms"]
engine_url = (
    "{engine}://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(
        **DATABASE_CONFIG
    )
)

engine = create_engine(engine_url)


# Определение пространства имен XML
namespaces = {
    "ns": "urn:hl7-org:v3",
    "identity": "urn:hl7-ru:identity",
    "address": "urn:hl7-ru:address",
    "fias": "urn:hl7-ru:fias",
}

xpath_comment = "/preceding-sibling::comment()[1]"

# Определение базовых значений заголовков с регулярными выражениями для валидации
headers_base_value = {
    "/ns:ClinicalDocument/ns:id": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.51$",
        },
        "extension": {"@type": r"\d+"},
    },
    "/ns:ClinicalDocument/ns:setId": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.50$",
        },
        "extension": {"@type": r"\d+"},
    },
    "/ns:ClinicalDocument/ns:versionNumber": {"value": {"@type": r"\d+"}},
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[1]": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.10$",
            # {org_oid}.100.{mis_number}.10.{system}
        },
        "extension": {"@type": r"\d+"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[2]": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.10$",
        },
        "extension": {"@type": r"\d+"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IdentityCardType": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystem": {"@type": "^.+$"},
        "codeSystemName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Series": {
        "text": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Number": {
        "text": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgName": {
        "text": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgCode": {
        "text": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueDate": {
        "value": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:InsurancePolicyType": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystem": {"@type": "^.+$"},
        "codeSystemName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:Number": {
        "text": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:Type": {
        "code": {
            "@type": "^.+$",
        },
        "displayName": {"@type": "^.+$"},
        "codeSystem": {"@type": "^.+$"},
        "codeSystemName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:streetAddressLine": {
        "text": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:stateCode": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystem": {"@type": "^.+$"},
        "codeSystemName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:residentCode": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystem": {"@type": "^.+$"},
        "codeSystemName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:postalCode": {
        "text": {"@type": "^.+$"}
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:AOGUID": {
        "text": {"@type": "^.+$"},
    },
    "/ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:HOUSEGUID": {
        "text": {"@type": "^.+$"},
    },
}

# Пути к SEMD для различных OID
semd_paths = {"147": r"Эпикриз в стационаре выписной.xml"}


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
        self.type = Type(re.compile(kwargs.get("@type", r"^.+$")))

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
            el: Union[_Element, None] = self._get_first_or_none(
                root.xpath(header_key, namespaces=namespaces),
            )
            if el is not None:
                comment = self._get_first_or_none(
                    root.xpath(header_key + xpath_comment, namespaces=namespaces),
                )
                if comment is not None:
                    header_value = {
                        key: {
                            **value,
                            "@req": (
                                re.search(r"\[\d+\.\.\d+\]", comment.text).group(0)
                                if re.search(r"\[\d+\.\.\d+\]", comment.text)
                                else "[0..0]"
                            ),
                        }
                        for key, value in header_value.items()
                    }
                    header_value = {
                        key: {
                            **value,
                            "@alias": (
                                re.search(r"\[\d+\.\.\d+\] (.*)", comment.text).group(1)
                                if re.search(r"\[\d+\.\.\d+\]", comment.text)
                                else "Not alias"
                            ),
                        }
                        for key, value in header_value.items()
                    }
                for attr_name, attr_value in header_value.items():
                    attr_value["@value"] = self._encode_name(
                        "{" + header_key + "@" + attr_name + "}"
                    )
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
            f.write(
                etree.tostring(
                    self.xml_doc,
                    pretty_print=True,
                    xml_declaration=True,
                    encoding="utf-8",
                )
            )

    @classmethod
    def _encode_name(cls, name: str) -> str:
        # Кодируем символы в их hex-обозначения
        return name.replace("/", "_x2F_").replace(":", "_x3A_").replace("@", "_x40_")

    @classmethod
    def _decode_name(cls, encoded_name: str) -> str:
        # Декодируем обратно в исходные символы
        return (
            encoded_name.replace("_x2F_", "/")
            .replace("_x3A_", ":")
            .replace("_x40_", "@")
        )

    @staticmethod
    def _get_first_or_none(target: Iterable):
        return next(iter(target), None)

    def __call__(self) -> _Element:
        """
        Обработать поля SEMD и заполнить их значениями из базы данных.

        :return: Измененный XML документ.
        :raises: ValueError, если валидация одного из полей не удалась.
        """
        for field in self._semd_fields:
            result = OTHER_DATABASE_TEMPLATE.get(
                find_by_name(self._decode_name(field.value)), ""
            )

            if not field.type(result) and (
                field.req.startswith("[0..0]") or field.req.startswith("[0..*]")
            ):
                el = self._get_first_or_none(
                    self.xml_doc.xpath(
                        self._get_first_or_none(
                            self._decode_name(field.value).split("@"),
                        ),
                        namespaces=namespaces,
                    ),
                )
                if el is not None:
                    el.getparent().remove(el)

                continue

            if not field.type(result):
                break

            field.__setattr__("in_xml", result)
        else:
            temp_xml_doc = etree.tostring(self.xml_doc, encoding="unicode")
            temp_xml_doc = temp_xml_doc.format(
                **{filed.value: filed.in_xml for filed in self._semd_fields}
            )
            self.xml_doc = etree.fromstring(temp_xml_doc)
            return self.xml_doc

        raise ValueError("Валидация не прошла для одного из полей")

    def create_fields_in_database(self) -> None:

        for field in self._semd_fields:
            result = OTHER_DATABASE_TEMPLATE.get(
                find_by_name(self._decode_name(field.value)), ""
            )

            if not field.type(result) and (
                field.req.startswith("[0..0]") or field.req.startswith("[0..*]")
            ):
                el = self._get_first_or_none(
                    self.xml_doc.xpath(
                        self._get_first_or_none(
                            self._decode_name(field.value).split("@"),
                        ),
                        namespaces=namespaces,
                    ),
                )
                if el is not None:
                    el.getparent().remove(el)

                continue

            if not field.type(result):
                break

            field.__setattr__("in_xml", result)
        else:
            temp_xml_doc = etree.tostring(self.xml_doc, encoding="unicode")
            temp_xml_doc = temp_xml_doc.format(
                **{filed.value: filed.in_xml for filed in self._semd_fields}
            )
            self.xml_doc = etree.fromstring(temp_xml_doc)
            return self.xml_doc

        raise ValueError("Валидация не прошла для одного из полей")


# Создание и обработка объекта SEMD
a = SEMD("147")
# a()
a.save()
