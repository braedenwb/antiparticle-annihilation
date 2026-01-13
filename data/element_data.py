ELEMENT_DATA = {
    "hydrogen": {
        "buy_cost": 20,
        "upgrade_cost": 10,
        "state": "Gas",
        "desc": "Fires projectiles at a steady rate.",
        "damage_element": True,
        "healing_element": False,
        "energy_element": False,
        "radioactive_element": False,

        "hp": 50,
        "damage": 10,
        "cooldown": 400,
        "range": 150
    },

    "oxygen": {
        "level": 1,
        "buy_cost": 100,
        "upgrade_cost": 50,
        "state": "Gas",
        "desc": "Heals nearby elements & compounds.",
        "damage_element": False,
        "healing_element": True,
        "energy_element": False,
        "radioactive_element": False,

        "hp": 50,
        "healing": 15,
        "cooldown": 5000,
        "range": 75
    },
    
    "silicon": {
        "level": 1,
        "buy_cost": 100,
        "upgrade_cost": 50,
        "state": "Solid",
        "desc": "Can be placed on energy tiles to gain energy.",
        "damage_element": False,
        "healing_element": False,
        "energy_element": True,
        "radioactive_element": False,
        
        "hp": 50,
        "energy_generation": 1,
        "cooldown": 1000,
        "range": 0
    }
}