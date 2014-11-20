-- database schema for pyarts state files

-- metadata about the database itself (schema version etc...)
create table metadata (
    key text,
    value text
);

-- info about the scenario (num players, description etc).
create table scenarioinfo (
    key text,
    value text
);


-- The next section contains the static parts of a state,
-- the map itself and the unit set

-- a team is an owner of entities, is can be controlled
-- by 1 or more players
create table teams (
    id integer primary key,
    name text,
    data text
);

-- entitiy prototypes and templates used for creating
-- entities, these are shared by all teams but can be overriden
-- by the teamprotos table in the dynamic part
create table entityprotos (
    id integer primary key,
    name text,
    data text
);

