"""
compound_data.py

Data registry for compound recipes and combat stats.
Add new compounds here instead of hardcoding them in the bonding logic.
"""

COMPOUND_DATA = {
    "water": {
        "display_name": "Water",
        "formula": "H2O",
        "components": {
            "hydrogen": 1,
            "oxygen": 1,
        },
        "min_levels": {
            "hydrogen": 2,
            "oxygen": 1,
        },
        "state": "Liquid",
        "description": "Rapidly fires droplets of water, dealing chip damage and knocking back enemies.",
        "damage_element": True,
        "healing_element": False,
        "energy_element": False,
        "health": 160,
        "damage": 4,
        "range": 175,
        "cooldown": 325,
        "upgrade_cost": 45,
        "knockback": 16,
    },
    "hydrogen_peroxide": {
        "display_name": "Hydrogen Peroxide",
        "formula": "H2O2",
        "components": {
            "hydrogen": 1,
            "oxygen": 1,
        },
        "min_levels": {
            "hydrogen": 2,
            "oxygen": 2,
        },
        "state": "Liquid",
        "description": "Rapidly fires droplets, which can heal molecules from a long distance. Better for healing singular, distant molecules.",
        "damage_element": False,
        "healing_element": True,
        "energy_element": False,
        "health": 200,
        "healing": 18,
        "range": 275,
        "cooldown": 240,
        "upgrade_cost": 70,
    },
    "ozone": {
        "display_name": "Ozone",
        "formula": "O3",
        "components": {
            "oxygen": 1
        },
        "min_levels": {
            "oxygen": 3
        },
        "state": "Gas",
        "description": "Creates an ozone shield, which protects elements & compounds in range.",
        "damage_element": False,
        "healing_element": False,
        "energy_element": False,
        "health": 150,
        "range": 250,
        "cooldown": 0,
        "upgrade_cost": 30,
        "damage_reduction": 0.35,
    },
    "rust": {
        "display_name": "Rust",
        "formula": "Fe2O3",
        "components": {
            "iron": 1,
            "oxygen": 1,
        },
        "min_levels": {
            "iron": 2,
            "oxygen": 3,
        },
        "state": "Solid",
        "description": "A dud compound with no useful stats.",
        "damage_element": False,
        "healing_element": False,
        "energy_element": False,
        "health": 1,
        "range": 0,
        "cooldown": 0,
        "upgrade_cost": 9999,
    },
    "black_hole": {
        "display_name": "Black Hole",
        "formula": "Fe30",
        "hide_component_sprites": True,
        "components": {
            "iron": 1,
        },
        "min_levels": {
            "iron": 30,
        },
        "state": "Unknown",
        "description": "Sucks up nearby antiparticles and passively generates energy. Higher health antiparticles take longer to consume.",
        "damage_element": False,
        "healing_element": False,
        "energy_element": True,
        "health": 3000,
        "range": 260,
        "cooldown": 1000,
        "upgrade_cost": 5000,
        "energy_generation": 4,
        "gravity_well": True,
        "suction_base_time": 700,
        "suction_time_per_health": 1.2,
        "suction_pull_speed": 150,
    }
}


def get_compound_definitions():
    return COMPOUND_DATA
