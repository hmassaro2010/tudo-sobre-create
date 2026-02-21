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
})