function build_townhall(me, x, y)
    print('building townhall')
    ent = create_entity(0, 'townhall')
    place_entity(ent, x, y)
end
