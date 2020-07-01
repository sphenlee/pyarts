function start_building(me)
    log('started building something')
end

function build_townhall(me, x, y)
    log('building townhall')
    construct(me, 'townhall', function(townhall)
    	create_town(townhall, 'human')
    	display('Completed constructing Town Hall')
    end)
end


function killme(me)
    log('killing {}', me)
    destroy(me)
end
