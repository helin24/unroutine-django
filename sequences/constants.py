from enum import Enum

CATEGORY_CHOICES = [
    ('J', 'Jump'),
    ('S', 'Spin'),
    ('M', 'Move'),
]

class LevelAbbreviation(Enum):
    ADULT_BRONZE = 'AB'
    ADULT_SILVER = 'AS'
    ADULT_GOLD = 'AG'

LEVEL_CHOICES = [
    (LevelAbbreviation.ADULT_BRONZE.value, 'Adult Bronze'),
    (LevelAbbreviation.ADULT_SILVER.value, 'Adult Silver'),
    (LevelAbbreviation.ADULT_GOLD.value, 'Adult Gold'),
]

CSV_TO_LEVEL_MAP = {
    'bronze': LevelAbbreviation.ADULT_BRONZE.value,
    'silver': LevelAbbreviation.ADULT_SILVER.value,
    'gold': LevelAbbreviation.ADULT_GOLD.value,
}

RATINGS_COUNT_REQUIREMENT = 5
RATINGS_AVERAGE_REQUIREMENT = 3

