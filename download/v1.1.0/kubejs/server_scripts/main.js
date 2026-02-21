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
function removeAndArround(e, input, material, output) {
    e.remove({output: output})
    e.shaped(
        output,
        [
            'MMM',
            'MIM',
            'MMM'
        ],
        {
            M: material,
            I: input
        }
    )
}


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

    // sophisticatedStorage stacks
    removeAndArround(e, ss('upgrade_base'), cr('zinc_block'), ss('stack_upgrade_tier_1'))
    removeAndArround(e, ss('stack_upgrade_tier_1'), mc('copper_block'), ss('stack_upgrade_tier_1_plus'))
    removeAndArround(e, ss('stack_upgrade_tier_1'), mc('iron_block'), ss('stack_upgrade_tier_2'))
    removeAndArround(e, ss('stack_upgrade_tier_2'), mc('gold_block'), ss('stack_upgrade_tier_3'))
    removeAndArround(e, ss('stack_upgrade_tier_3'), mc('diamond_block'), ss('stack_upgrade_tier_4'))
    removeAndArround(e, ss('stack_upgrade_tier_4'), mc('netherite_block'), ss('stack_upgrade_tier_5'))
    e.shaped(ss('stack_upgrade_tier_2'), 
        [
            ' M ',
            'MIM',
            ' M '
        ], {
            M: mc('iron_block'),
            I: ss('stack_upgrade_tier_1_plus')
        })

})