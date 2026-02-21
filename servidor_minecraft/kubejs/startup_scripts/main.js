// Registro de items
StartupEvents.registry('item', e => {

    // Geração dos items de transição
    const incomplete_items = [
        'logic_processor_press',
        'calculation_processor_press',
        'engineering_processor_press',
        'silicon_press',

        'printed_calculation_processor',
        'printed_logic_processor',
        'printed_engineering_processor',
        'printed_silicon',

        'calculation_processor',
        'engineering_processor',
        'logic_processor'
    ]
    incomplete_items.forEach(item => {
        e.create(`incomplete_${item}`)
            .unstackable()
            .translationKey(`item.kubejs.incomplete_${item}`)
    })
})