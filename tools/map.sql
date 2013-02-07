-- schema for the map

create table map (
    nid integer primary key,
    terrain blob,
    ground blob,
    walk blob,
    sail blob,
    fly blob
);

create table doors (
    src integer references map(nid),
    dest integer references map(nid),
    offx int,
    offy int,
    verts blob,
    primary key(src, dest)
);
