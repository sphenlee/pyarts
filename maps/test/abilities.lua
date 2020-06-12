function start_building(me)
    print('started building something')
end

function build_townhall(me, x, y)
    print('building townhall')
    construct(me, 'townhall')
end


function killme(me)
    print('killing', me)
    destroy(me)
end
