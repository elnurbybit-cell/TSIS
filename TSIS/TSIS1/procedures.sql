CREATE OR REPLACE PROCEDURE add_phone(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_email VARCHAR,
    p_birthday DATE,
    p_group_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
    v_contact_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
    VALUES (p_first_name, p_last_name, p_email, p_birthday, v_group_id)
    RETURNING id INTO v_contact_id;

    INSERT INTO phones(contact_id, phone)
    VALUES (v_contact_id, p_phone);
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_id INTEGER,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = p_contact_id;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_pattern VARCHAR)
RETURNS TABLE(
    contact_id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name,
        p.phone
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_pattern || '%'
        OR c.last_name ILIKE '%' || p_pattern || '%'
        OR c.email ILIKE '%' || p_pattern || '%'
        OR p.phone ILIKE '%' || p_pattern || '%'
        OR g.name ILIKE '%' || p_pattern || '%';
END;
$$;