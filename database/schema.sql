CREATE TABLE restaurant_tables (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    number INTEGER NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL
);

CREATE TABLE reservations (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guest_name VARCHAR(100) NOT NULL,
    guest_count INTEGER NOT NULL CHECK (guest_count > 0),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT valid_reservation_time CHECK (ends_at > starts_at)
);

CREATE TABLE reservation_tables (
    reservation_id INTEGER NOT NULL
        REFERENCES reservations(id) ON DELETE CASCADE,
    table_id INTEGER NOT NULL
        REFERENCES restaurant_tables(id),
    PRIMARY KEY (reservation_id, table_id)
);