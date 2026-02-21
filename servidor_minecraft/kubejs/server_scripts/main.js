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
const sb = v => `sophisticatedbackpacks:${v}`
const ae = v => `ae2:${v}`
const nf = v => `neoforge:${v}`
const ca = v => `createaddition:${v}`
const kj = v => `kubejs:${v}`
const rs = v => `refinedstorage:${v}`
const bg = v => `buildinggadgets2:${v}`

const tag = v => `#${v}`

function no_modid(v) {
    let match = v.match(/:(.*)/)

    if (match === null) return v

    return match[1]
}

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

    e.remove({output: ae('inscriber')})
    e.remove({type: ae('inscriber')})
    e.remove({type: ae('charger')})

    e.remove({output: rs('basic_processor')})
    e.remove({output: rs('improved_processor')})
    e.remove({output: rs('advanced_processor')})
    e.remove({output: rs('raw_basic_processor')})
    e.remove({output: rs('raw_improved_processor')})
    e.remove({output: rs('raw_advanced_processor')})
    e.remove({output: rs('construction_core')})
    e.remove({output: rs('destruction_core')})
    e.remove({output: rs('silicon')})

    e.remove({mod: 'buildinggadgets2'})

    e.replaceInput({mod: 'refinedstorage', input: rs('basic_processor')},
        rs('basic_processor'),
        ae('calculation_processor'))
    e.replaceInput({mod: 'refinedstorage', input: rs('improved_processor')},
        rs('improved_processor'),
        ae('logic_processor'))
    e.replaceInput({mod: 'refinedstorage', input: rs('advanced_processor')},
        rs('advanced_processor'),
        ae('engineering_processor'))
    e.replaceInput({mod: 'refinedstorage', input: rs('construction_core')},
        rs('construction_core'),
        ae('formation_core'))
    e.replaceInput({mod: 'refinedstorage', input: rs('destruction_core')},
        rs('destruction_core'),
        ae('annihilation_core'))
    e.replaceInput({output: rs('quartz_eriched_iron')},
        mc('quartz'),
        ae('certus_quartz_crystal'))
    e.replaceInput({output: rs('quartz_eriched_copper')},
        mc('quartz'),
        ae('certus_quartz_crystal'))

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

    // Sophisticated Storage/Backpack convert
    function sophisticated_convert(sb_upgrade, ss_upgrade) {
        /*e.remove({
            input: ss_upgrade,
            output: sb_upgrade
        })
        e.remove({
            input: sb_upgrade,
            output: ss_upgrade
        }) */
        e.shaped(
            sb_upgrade,
            ['SUS', ' L ', 'S S'],
            {
                S: mc('string'),
                U: ss_upgrade,
                L: mc('leather')
            }
        )
        e.shaped(
            ss_upgrade,
            [' P ', 'PUP'],
            {
                P: tag(mc('planks')),
                U: sb_upgrade
            }
        )
    }

    sophisticated_convert(sb('stack_upgrade_starter_tier'), ss('stack_upgrade_tier_1_plus'))
    sophisticated_convert(sb('stack_upgrade_tier_1'), ss('stack_upgrade_tier_2'))
    sophisticated_convert(sb('stack_upgrade_tier_2'), ss('stack_upgrade_tier_3'))
    sophisticated_convert(sb('stack_upgrade_tier_3'), ss('stack_upgrade_tier_4'))
    sophisticated_convert(sb('stack_upgrade_tier_4'), ss('stack_upgrade_tier_5'))
    sophisticated_convert(sb('stack_upgrade_omega_tier'), ss('stack_upgrade_omega_tier'))

    // Inscriber -> create
    const ae2_presses = [
        ae('logic_processor_press'),
        ae('calculation_processor_press'),
        ae('engineering_processor_press'),
        ae('silicon_press')
    ]
    ae2_presses.forEach(press => {
        let transitional = kj(`incomplete_${no_modid(press)}`)

        e.custom({
            type: cr('sequenced_assembly'),
            ingredient: { item: mc('iron_block') },
            results: [{ id: press }],
            transitional_item: { id: transitional },
            sequence: [
                {
                    type: cr('deploying'),
                    ingredients: [
                        { item: transitional },
                        { item: press }
                    ],
                    results: [{ id: transitional }],
                    keep_held_item: true
                },
                {
                    type: cr('pressing'),
                    ingredients: [{ item: transitional }],
                    results: [{ id: transitional }]
                }
            ]
        })
    })

    const ae2_circuits = [
        [
            ae('calculation_processor_press'),
            ae('certus_quartz_crystal'),
            ae('printed_calculation_processor')
        ], 
        [
            ae('logic_processor_press'),
            mc('gold_ingot'),
            ae('printed_logic_processor')
        ],
        [
            ae('silicon_press'),
            ae('silicon'),
            ae('printed_silicon')
        ],
        [
            ae('engineering_processor_press'),
            mc('diamond'),
            ae('printed_engineering_processor')
        ]
    ]
    ae2_circuits.forEach(v => {
        let [press, ingredient, result] = v
        let transitional = kj(`incomplete_${no_modid(result)}`)

        e.custom({
            type: cr('sequenced_assembly'),
            ingredient: { item: ingredient },
            results: [{ id: result }],
            transitional_item: { id: transitional },
            sequence: [
                {
                    type: cr('deploying'),
                    ingredients: [
                        { item: transitional },
                        { item: press }
                    ],
                    results: [{ id: transitional }]
                },
                {
                    type: cr('filling'),
                    ingredients: [
                        { item: transitional },
                        { type: nf('single'), fluid: mc('lava'), amount: 200 }
                    ],
                    results: [{ id: transitional }]
                },
                {
                    type: cr('pressing'),
                    ingredients: [{ item: transitional }],
                    results: [{ id: transitional }]
                }
            ]
        })
    })

    const ae2_mount_processors = [
        [
            ae('printed_calculation_processor'),
            ae('calculation_processor')
        ],
        [
            ae('printed_engineering_processor'),
            ae('engineering_processor')
        ],
        [
            ae('printed_logic_processor'),
            ae('logic_processor')
        ]
    ]
    ae2_mount_processors.forEach(v => {
        let [ingredient, result] = v
        let transitional = kj(`incomplete_${no_modid(result)}`)

        e.custom({
            type: cr('sequenced_assembly'),
            ingredient: { item: ae('printed_silicon') },
            results: [{ id: result }],
            transitional_item: { id: transitional },
            sequence: [
                {
                    type: cr('deploying'),
                    ingredients: [
                        { item: transitional },
                        { item: ingredient }
                    ],
                    results: [{ id: transitional }],
                    keep_held_item: true
                },
                {
                    type: cr('deploying'),
                    ingredients: [
                        { item: transitional },
                        { item: mc('redstone') }
                    ],
                    results: [{ id: transitional }]
                },
                {
                    type: cr('pressing'),
                    ingredients: [{ item: transitional }],
                    results: [{ id: transitional }]
                }
            ]
        })
    })

    e.custom({
        type: ca('charging'),
        energy: 10000,
        max_charge_rate: 100,
        ingredients: [{ item: mc('compass') }],
        results: [{ id: ae('meteorite_compass') }]
    })

    // Building gadgets nerf
    e.shaped(bg('template_manager'),
        ['IAI', 'PLP', 'IRI'],
        {
            I: rs('quartz_enriched_iron'),
            A: mc('lapis_lazuli'),
            P: mc('paper'),
            L: ae('logic_processor'),
            R: mc('redstone')
        })
    e.shaped(bg('gadget_building'),
        ['IDI', 'QCQ', 'IDI'],
        {
            I: rs('quartz_enriched_iron'),
            D: mc('diamond'),
            Q: ae('charged_certus_quartz_crystal'),
            C: ae('formation_core')
        })
    e.shaped(bg('gadget_exchanging'),
        ['IDI', 'FCF', 'IDI'],
        {
            I: rs('quartz_enriched_iron'),
            D: mc('diamond'),
            F: ae('fluix_crystal'),
            C: ae('formation_core')
        })
    e.shaped(bg('gadget_copy_paste'),
        ['IEI', 'PCP', 'IEI'],
        {
            I: rs('quartz_enriched_iron'),
            E: mc('emerald'),
            P: ae('engineering_processor'),
            C: ae('formation_core')
        })
    e.shaped(bg('gadget_cut_paste'),
        ['IEI', 'PCP', 'IEI'],
        {
            I: rs('quartz_enriched_iron'),
            E: mc('emerald'),
            P: ae('engineering_processor'),
            C: ae('annihilation_core')
        })
    e.shaped(bg('gadget_destruction'),
        ['IDI', 'QCQ', 'IDI'],
        {
            I: rs('quartz_enriched_iron'),
            D: mc('diamond'),
            Q: ae('charged_certus_quartz_crystal'),
            C: ae('annihilation_core')
        })
})