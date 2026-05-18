import random

QUESTS = [
    {"text": "Раздай 5 листовок у метро", "base_reward": 10},
    {"text": "Улыбнись каждому 3-му прохожему", "base_reward": 5},
    {"text": "Избегай полиции в парке", "base_reward": 15},
    {"text": "Поговори с незнакомцем о погоде", "base_reward": 8}
]

MODIFIERS = [
    {"condition": "🌧 Дождь", "text": "Листовки мокнут, эффективность −30%", "mult": 0.7},
    {"condition": "☀️ Солнечно", "text": "Люди в настроении, +20% к успеху", "mult": 1.2},
    {"condition": "🌆 Вечер пятницы", "text": "Все спешат, но открыты к общению", "mult": 1.0}
]

def generate_daily_quest():
    quest = random.choice(QUESTS)
    mod = random.choice(MODIFIERS)
    reward = int(quest["base_reward"] * mod["mult"])
    return f"📋 Задание: {quest['text']}\n{mod['condition']} — {mod['text']}\n💰 Награда: {reward} очков"