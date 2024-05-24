from sqlalchemy import create_engine, text

DATABASES = {
    "p51vms": {
        "engine": "mysql+mysqldb",
        "user": "dbuser",
        "password": "dbpassword",
        "host": "p51vms",
        "port": 3306,
        "database": "s12",
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


# Настройка подключения к базе данных
engine = create_engine(engine_url)

# Данные для добавления
oid = "147"
code = 1
xpath_name = "/ns:ClinicalDocument/ns:id@root"

# Запросы для вставки данных и создания связей
with engine.connect() as connection:
    # Начало транзакции
    with connection.begin():
        # Добавление записи в таблицу Semd
        semd_insert_query = """
        INSERT INTO Semd (oid, code)
        SELECT :oid, :code
        WHERE NOT EXISTS (
            SELECT oid FROM Semd WHERE oid = :oid
        ) LIMIT 1;
        """
        connection.execute(text(semd_insert_query), {"oid": oid, "code": code})

        # Добавление записи в таблицу SemdPropertyType с пустыми значениями
        semd_property_type_insert_query = """
        INSERT INTO SemdPropertyType (db_name, sql_query, alias, comment)
        SELECT NULL, NULL, NULL, NULL
        WHERE NOT EXISTS (
            SELECT id FROM SemdPropertyType WHERE db_name IS NULL AND sql_query IS NULL AND alias IS NULL AND comment IS NULL
        ) LIMIT 1;
        """
        connection.execute(text(semd_property_type_insert_query))

        # Получение id добавленного/существующего SemdPropertyType
        semd_property_type_id_query = """
        SELECT id FROM SemdPropertyType 
        WHERE db_name IS NULL AND sql_query IS NULL AND alias IS NULL AND comment IS NULL
        LIMIT 1;
        """
        semd_property_type_id = connection.execute(
            text(semd_property_type_id_query)
        ).scalar()

        # Добавление записи в таблицу SemdProperty
        semd_property_insert_query = """
        INSERT INTO SemdProperty (oid, xpath_name, semdPropertyType_id)
        SELECT :oid, :xpath_name, :semdPropertyType_id
        WHERE NOT EXISTS (
            SELECT oid FROM SemdProperty WHERE oid = :oid AND xpath_name = :xpath_name
        ) LIMIT 1;
        """
        connection.execute(
            text(semd_property_insert_query),
            {
                "oid": oid,
                "xpath_name": xpath_name,
                "semdPropertyType_id": semd_property_type_id,
            },
        )

        # Получение id добавленного/существующего Semd
        semd_id_query = "SELECT id FROM Semd WHERE oid = :oid"
        semd_id = connection.execute(text(semd_id_query), {"oid": oid}).scalar()

        # Получение id добавленного/существующего SemdProperty
        semd_property_id_query = (
            "SELECT id FROM SemdProperty WHERE oid = :oid AND xpath_name = :xpath_name"
        )
        semd_property_id = connection.execute(
            text(semd_property_id_query), {"oid": oid, "xpath_name": xpath_name}
        ).scalar()

        # Добавление записи в таблицу Semd_SemdProperty
        semd_semdproperty_insert_query = """
        INSERT INTO Semd_SemdProperty (semd_id, semdProperty_id)
        SELECT :semd_id, :semdProperty_id
        WHERE NOT EXISTS (
            SELECT * FROM Semd_SemdProperty WHERE semd_id = :semd_id AND semdProperty_id = :semdProperty_id
        ) LIMIT 1;
        """
        connection.execute(
            text(semd_semdproperty_insert_query),
            {"semd_id": semd_id, "semdProperty_id": semd_property_id},
        )
