// Custom recipes
function createMixing(e, ingredients, results) {
    e.custom({
        'type': cr('mixing'),
        'ingredients': ingredients,
        'results': results
    })
} /* Exemplo: createMixing(e, [
    {'item': mc('dirt')}, {'item': mc('gravel')}
], [{'id': mc('coarse_dirt')}]) */

// Mods
const cr = v => `create:${v}`
const mc = v => `minecraft:${v}`
const ss = v => `sophisticatedstorage:${v}`

ServerEvents.recipes(e => {
    // Reposição
    e.replaceInput(
        {output: cr('andesite_alloy'), input: mc('andesite')},
        mc('iron_nugget'),
        mc('iron_ingot')
    )
    e.replaceInput(
        {output: cr('andesite_alloy'), input: mc('andesite')},
        cr('zinc_nugget'),
        cr('zinc_ingot')
    )

    // Remoção
    e.remove({id: cr('mixing/andesite_alloy')})
    e.remove({id: cr('mixing/andesite_alloy_from_zinc')})

    e.remove({output: ss('stack_upgrade_tier_1_plus')})
    e.remove({input: ss('stack_upgrade_tier_1_plus')})
    e.remove({output: ss('stack_upgrade_tier_2')})
    e.remove({input: ss('stack_upgrade_tier_2')})
    e.remove({output: ss('stack_upgrade_tier_2')})
    e.remove({input: ss('stack_upgrade_tier_2')})
    e.remove({output: ss('stack_upgrade_tier_3')})
    e.remove({input: ss('stack_upgrade_tier_3')})
    e.remove({output: ss('stack_upgrade_tier_4')})
    e.remove({input: ss('stack_upgrade_tier_4')})
    e.remove({output: ss('stack_upgrade_tier_5')})
    e.remove({input: ss('stack_upgrade_tier_5')})
    e.remove({output: ss('stack_upgrade_omega_tier')})
    e.remove({input: ss('stack_upgrade_omega_tier')})

    // Create: Mixing
    createMixing(e, [
        {'item': mc('andesite')},
        {'item': mc('iron_ingot')}
    ], [
        {'id': cr('andesite_alloy')}
    ])
    createMixing(e, [
        {'item': mc('andesite')},
        {'item': cr('zinc_ingot')}
    ], [
        {'id': cr('andesite_alloy')}
    ])

    // All arround
    function all_arround(center, arround, result) {
        e.shaped(
            result,
            [
                'AAA',
                'ACA',
                'AAA'
            ],
            {
                A: arround,
                C: center
            }
        )
    }
    all_arround(ss('stack_upgrade_tier_1'), mc('copper_block'), ss('stack_upgrade_tier_1_plus'))
    all_arround(ss('stack_upgrade_tier_1'), mc('iron_block'), ss('stack_upgrade_tier_2'))
    all_arround(ss('stack_upgrade_tier_2'), mc('gold_block'), ss('stack_upgrade_tier_3'))
    all_arround(ss('stack_upgrade_tier_3'), mc('diamond_block'), ss('stack_upgrade_tier_4'))
    all_arround(ss('stack_upgrade_tier_4'), mc('netherite_block'), ss('stack_upgrade_tier_5'))

    e.shaped(
        ss('stack_upgrade_omega_tier'),
        ['AAA', 'AAA', 'AAA'],
        {
            A: ss('stack_upgrade_tier_5')
        }
    )
    e.shaped(
        ss('stack_upgrade_tier_2'),
        [' I ', 'IUI', ' I '],
        {
            I: mc('iron_block'),
            U: ss('stack_upgrade_tier_1_plus')
        }
    )
})