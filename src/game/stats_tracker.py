# Условия достижений
ACHIEVEMENTS = {
    "first_step": {"cond": lambda s: s["given"] >= 1, "title": "🥉 Первый шаг"},
    "smile_master": {"cond": lambda s: s["smiles"] >= 5, "title": "😎 Мастер улыбки"},
    "relentless": {"cond": lambda s: s["given"] >= 20, "title": "📦 Неутомимый курьер"},
    "survivor": {"cond": lambda s: s["interactions"] >= 30 and s["fatigue"] > 80, "title": "🔥 Выживший"}
}


def update_stats(stats, action, success=True):
    if action == "flyer" and success: stats["given"] += 1
    if action == "refusal": stats["refusals"] += 1
    if action == "smile": stats["smiles"] += 1
    if action == "push":
        stats["pushes"] = stats.get("pushes", 0) + 1  # Счётчик надавливаний
    stats["interactions"] += 1
    stats["fatigue"] = min(100, stats["fatigue"] + 5)
    return stats


def get_daily_summary(stats):
    """Генерирует итоговую сводку"""
    unlocked = [a["title"] for a in ACHIEVEMENTS.values() if a["cond"](stats)]
    ach_text = "\n🏆 " + ", ".join(unlocked) if unlocked else "\n🏆 Достижений пока нет"

    return (f"📊 Итоги дня:\n"
            f"📄 Раздано: {stats['given']} | ❌ Отказов: {stats['refusals']}\n"
            f"😊 Улыбок: {stats['smiles']} | 😴 Усталость: {stats['fatigue']}%{ach_text}")