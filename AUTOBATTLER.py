import random
import time
import json
import os


class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


WEAPONS = [
    {"name": "Меч", "damage": 3, "type": "Рубящий"},
    {"name": "Дубина", "damage": 3, "type": "Дробящий"},
    {"name": "Кинжал", "damage": 2, "type": "Колющий"},
    {"name": "Топор", "damage": 4, "type": "Рубящий"},
    {"name": "Копьё", "damage": 3, "type": "Колющий"},
    {"name": "Легендарный Меч", "damage": 10, "type": "Рубящий"}
]

MONSTERS = [
    {
        "name": "Гоблин",
        "health": 5,
        "weapon_damage": 2,
        "strength": 1,
        "agility": 1,
        "stamina": 1,
        "special": "",
        "reward": "Кинжал"
    },
    {
        "name": "Скелет",
        "health": 10,
        "weapon_damage": 2,
        "strength": 2,
        "agility": 2,
        "stamina": 1,
        "special": "Получает вдвое больше урона, если его бьют дробящим оружием",
        "reward": "Дубина"
    },
    {
        "name": "Слайм",
        "health": 8,
        "weapon_damage": 1,
        "strength": 3,
        "agility": 1,
        "stamina": 2,
        "special": "Рубящее оружие не наносит ему урона (но урон от силы и прочих особенностей работает)",
        "reward": "Копьё"
    },
    {
        "name": "Призрак",
        "health": 6,
        "weapon_damage": 3,
        "strength": 3,
        "agility": 1,
        "stamina": 3,
        "special": "Есть способность 'скрытая атака', как у разбойника 1-го уровня",
        "reward": "Меч"
    },
    {
        "name": "Голем",
        "health": 10,
        "weapon_damage": 1,
        "strength": 1,
        "agility": 3,
        "stamina": 1,
        "special": "Есть способность 'каменная кожа', как у Варвара 2-го уровня",
        "reward": "Топор"
    },
    {
        "name": "Дракон",
        "health": 20,
        "weapon_damage": 4,
        "strength": 4,
        "agility": 3,
        "stamina": 3,
        "special": "Каждый 3-й ход дышит огнём, нанося дополнительно 3 урона",
        "reward": "Легендарный Меч"
    }
]


class Character:
    def __init__(self, char_class):
        self.strength = random.randint(1, 3)
        self.agility = random.randint(1, 3)
        self.stamina = random.randint(1, 3)
        self.classes = {char_class: 1}
        self.weapon = self.get_starting_weapon(char_class)
        self.max_health = self.get_base_health() + self.stamina
        self.health = self.max_health

    def get_starting_weapon(self, char_class):
        weapon_map = {
            "Разбойник": "Кинжал",
            "Воин": "Меч",
            "Варвар": "Дубина"
        }
        name = weapon_map[char_class]
        for w in WEAPONS:
            if w["name"] == name:
                return w
        return WEAPONS[0]

    def get_base_health(self):
        return {
            "Разбойник": 4,
            "Воин": 5,
            "Варвар": 6
        }[list(self.classes.keys())[0]]

    def get_total_level(self):
        return sum(self.classes.values())

    def get_base_damage(self):
        return self.weapon["damage"] + self.strength

    def calculate_total_damage(self, target, is_first_turn=False, move_count=1):
        base = self.get_base_damage()
        bonus = 0
        reasons = []

        for cls, lvl in self.classes.items():
            if cls == "Разбойник":
                if lvl >= 1 and self.agility > target.agility:
                    bonus += 1
                    reasons.append(f"Разбойник L{lvl}: +1 урон (скрытая атака)")
                if lvl >= 3:
                    bonus += lvl - 2
                    reasons.append(f"Разбойник L{lvl}: Яд (+{lvl - 2} урона)")

            elif cls == "Воин":
                if lvl >= 1 and is_first_turn:
                    bonus += self.weapon["damage"]
                    reasons.append(f"Воин L{lvl}: Порыв к действию (+{self.weapon['damage']} урона)")
                if lvl >= 3:
                    bonus += 1
                    reasons.append(f"Воин L{lvl}: Сила +1")

            elif cls == "Варвар":
                if lvl >= 1:
                    bonus += 2
                    reasons.append(f"Варвар L{lvl}: Ярость (+2 урона)")

        total_damage = base + bonus
        return total_damage, base, bonus, reasons

    def get_class_display(self):
        return ", ".join([f"{cls} {lvl}" for cls, lvl in self.classes.items()])

    def __str__(self):
        return (
            f"\n=== Персонаж ===\n"
            f"Классы: {self.get_class_display()}\n"
            f"Здоровье: {self.health}/{self.max_health}\n"
            f"Сила: {self.strength} | Ловкость: {self.agility} | Выносливость: {self.stamina}\n"
            f"Оружие: {self.weapon['name']} ({self.weapon['type']}) (урон: {self.weapon['damage']})\n"
            f"Базовый урон: {self.get_base_damage()}\n"
        )


class Monster:
    def __init__(self, template):
        self.name = template["name"]
        self.max_health = template["health"]
        self.health = self.max_health
        self.weapon_damage = template["weapon_damage"]
        self.strength = template["strength"]
        self.agility = template["agility"]
        self.stamina = template["stamina"]
        self.special = template["special"]
        self.reward = template["reward"]
        self.weapon = next(w for w in WEAPONS if w["name"] == self.reward)

    def get_base_damage(self):
        return self.weapon_damage + self.strength

    def __str__(self):
        special_text = self.special if self.special else "Нет"
        return (
            f"\n👹 {self.name}\n"
            f"Здоровье: {self.health}/{self.max_health}\n"
            f"Сила: {self.strength} | Ловкость: {self.agility} | Выносливость: {self.stamina}\n"
            f"Оружие: {self.weapon['name']} ({self.weapon['type']}) (урон: {self.weapon['damage']})\n"
            f"Особенность: {special_text}\n"
        )


def random_monster():
    return Monster(random.choice(MONSTERS))


def combat(player, monster):
    print(f"\n{Color.CYAN}⚔️  === БОЙ: {list(player.classes.keys())[0]} vs {monster.name} ==={Color.RESET}")
    turn = "player" if player.agility >= monster.agility else "monster"
    print(f"{Color.YELLOW}🏃 Первым ходит: {'Игрок' if turn == 'player' else monster.name}{Color.RESET}")
    time.sleep(0.7)

    move_count = 0

    while player.health > 0 and monster.health > 0:
        move_count += 1
        is_first_turn = (move_count == 1)

        print(f"\n{Color.GREEN}--- Ход {move_count} ---{Color.RESET}")
        print(f"Игрок: {player.health}/{player.max_health} ❤️")
        print(f"{monster.name}: {monster.health}/{monster.max_health} ❤️")
        time.sleep(0.4)

        attacker, target = (player, monster) if turn == "player" else (monster, player)
        attacker_name = "Игрок" if turn == "player" else monster.name
        print(f"\n{Color.MAGENTA}👉 {attacker_name} атакует!{Color.RESET}")
        time.sleep(0.3)

        roll = random.randint(1, attacker.agility + target.agility)
        print(f"{Color.BLUE}🎲 Бросок: {roll} (успех, если > {target.agility}){Color.RESET}")

        if roll <= target.agility:
            print(f"{Color.GRAY}❌ Промах!{Color.RESET}")
            damage = attacker.get_base_damage()
            print(f"{Color.RED}💥 Но нанесён базовый урон: {damage}{Color.RESET}")
        else:
            if isinstance(attacker, Character):
                total, base, bonus, reasons = attacker.calculate_total_damage(target, is_first_turn=is_first_turn,
                                                                              move_count=move_count)
                print(f"{Color.RED}💥 Попадание! Базовый урон: {base}{Color.RESET}")
                for r in reasons:
                    print(f"   {Color.YELLOW}➕ {r}{Color.RESET}")
                damage = total
            else:
                damage = attacker.get_base_damage()
                print(f"{Color.RED}💥 Попадание! Нанесено {damage} урона{Color.RESET}")

            if isinstance(target, Monster):
                if target.name == "Слайм" and attacker.weapon["type"] == "Рубящий":
                    print(f"{Color.BLUE}🛡️  Слайм игнорирует рубящий урон!{Color.RESET}")
                    damage = 0
                elif target.name == "Скелет" and attacker.weapon["type"] == "Дробящий":
                    damage *= 2
                    print(f"{Color.RED}💥 Скелет получает удвоенный урон от дробящего оружия!{Color.RESET}")
                elif target.name == "Призрак" and attacker.agility > target.agility:
                    damage += 1
                    print(f"{Color.YELLOW}➕ Призрак: +1 урон (скрытая атака){Color.RESET}")
                elif target.name == "Голем" and attacker.strength > target.strength:
                    reduction = target.stamina
                    damage = max(0, damage - reduction)
                    print(f"{Color.BLUE}🛡️  Голем: снижает урон на {reduction} (каменная кожа){Color.RESET}")

            print(f"{Color.RED}→ Итого: {damage} урона{Color.RESET}")

        target.health -= damage
        print(
            f"{Color.GREEN}❤️  У {target.name if hasattr(target, 'name') else 'Игрока'} осталось {max(0, target.health)} HP{Color.RESET}")

        if isinstance(attacker, Monster) and attacker.name == "Дракон" and move_count % 3 == 0:
            fire_damage = 3
            print(f"{Color.RED}🔥 Дракон дышит огнём! Наносит дополнительно {fire_damage} урона!{Color.RESET}")
            target.health -= fire_damage
            print(f"{Color.GREEN}❤️  У {target.name} осталось {max(0, target.health)} HP{Color.RESET}")

        time.sleep(0.8)
        turn = "monster" if turn == "player" else "player"

    return player.health > 0


def show_tutorial():
    print(f"\n{Color.BOLD}🎓 ОБУЧЕНИЕ: Как играть?{Color.RESET}")
    print("\n1. Выберите класс: Разбойник, Воин или Варвар.")
    print("   • Разбойник: +1 урон, если ловкость выше цели. На 3 уровне — яд.")
    print("   • Воин: В первый ход наносит двойной урон. На 3 уровне — +1 сила.")
    print("   • Варвар: +2 урона всегда. На 3 уровне — +1 выносливость.")
    time.sleep(1)

    print("\n2. Оружие имеет тип: Рубящий, Колющий, Дробящий.")
    print("   • Некоторые монстры слабы или устойчивы к определённым типам.")

    print("\n3. Бои идут автоматически по ходам.")
    print("   • Даже при промахе наносится базовый урон.")

    print("\n4. После победы:")
    print("   • Здоровье восстанавливается.")
    print("   • Можно повысить уровень в ЛЮБОМ классе (мультикласс!).")
    print("   • Максимум — 3 уровня суммарно.")
    print("   • Вам предложат заменить оружие на дроп с монстра.")

    print("\n5. Победите 5 монстров подряд — и вы выиграли!")
    input(f"\n{Color.YELLOW}> Нажмите Enter, чтобы начать игру...{Color.RESET}")


def choose_class():
    print("Выберите класс персонажа:")
    print("1. Разбойник")
    print("2. Воин")
    print("3. Варвар")
    while True:
        c = input("> Введите номер (1-3): ").strip()
        if c == "1":
            return "Разбойник"
        elif c == "2":
            return "Воин"
        elif c == "3":
            return "Варвар"
        else:
            print("❌ Неверный ввод.")


def choose_upgrade_class(current_classes):
    classes = ["Разбойник", "Воин", "Варвар"]
    print("\n📈 Выберите класс для повышения уровня:")
    for i, cls in enumerate(classes, 1):
        lvl = current_classes.get(cls, 0)
        print(f"{i}. {cls} (уровень: {lvl})")
    while True:
        c = input("> Номер: ").strip()
        if c in ["1", "2", "3"]:
            cls = classes[int(c) - 1]
            if sum(current_classes.values()) >= 3:
                print("❌ Макс. уровень 3 достигнут.")
                return None
            return cls
        else:
            print("❌ Введите 1, 2 или 3.")


def offer_weapon_change(player, weapon):
    print(f"\n🎁 Выпало: {weapon['name']} ({weapon['type']}) (урон: {weapon['damage']})")
    print(f"Текущее: {player.weapon['name']} ({player.weapon['type']}) (урон: {player.weapon['damage']})")
    while True:
        c = input("> Заменить? (д/н): ").strip().lower()
        if c in ["д", "да", "y", "yes"]:
            player.weapon = weapon
            print("✅ Оружие заменено!")
            break
        elif c in ["н", "нет", "n", "no"]:
            print("❌ Оставляем старое.")
            break
        else:
            print("❌ Введите 'д' или 'н'.")


def load_stats():
    if os.path.exists("game_stats.json"):
        with open("game_stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"best_run": 0}


def save_stats(stats):
    with open("game_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def main():
    print(f"{Color.CYAN}{Color.BOLD}🎮 ДОБРО ПОЖАЛОВАТЬ В АВТОБАТТЛЕР!{Color.RESET}")

    if input("\nХотите пройти обучение? (д/н): ").strip().lower() in ['д', 'да', 'y', 'yes']:
        show_tutorial()

    stats = load_stats()
    print(f"\n📊 Лучший результат: {stats['best_run']} побед подряд")

    while True:
        char_class = choose_class()
        player = Character(char_class)
        victories = 0

        print(f"\n🎉 Создан персонаж:")
        print(player)
        input("\n> Нажмите Enter...")

        while player.health > 0 and victories < 5:
            print(f"\n🔥 Бой #{victories + 1}")
            monster = random_monster()
            print(f"\n👹 {monster.name}")
            print(monster)
            input("\n> Нажмите Enter для начала боя...")

            if combat(player, monster):
                victories += 1
                player.health = player.max_health
                print(f"\n{Color.GREEN}❤️  Здоровье восстановлено.{Color.RESET}")

                if player.get_total_level() < 3:
                    cls = choose_upgrade_class(player.classes)
                    if cls:
                        player.classes[cls] = player.classes.get(cls, 0) + 1
                        print(f"📈 Уровень {cls} повышен!")

                offer_weapon_change(player, monster.weapon)
                input("\n> Нажмите Enter...")
            else:
                break

        if victories >= 5:
            print(f"\n{Color.YELLOW}{Color.BOLD}🏆 ПОБЕДА! Вы прошли игру!{Color.RESET}")
            if victories > stats["best_run"]:
                stats["best_run"] = victories
                save_stats(stats)
                print("🎉 Новый рекорд!")
            break
        else:
            print(f"\n💀 Поражение после {victories} побед.")
            if victories > stats["best_run"]:
                stats["best_run"] = victories
                save_stats(stats)
                print("Но это ваш новый рекорд!")

            if input("\n🔄 Новый герой? (д/н): ").strip().lower() not in ['д', 'да', 'y', 'yes']:
                break

    print(f"\n{Color.CYAN}👋 Спасибо за игру!{Color.RESET}")


if __name__ == "__main__":
    main()