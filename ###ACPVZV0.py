import tkinter as tk
import random
import time
import math
import os
import ctypes

# ============================================================
#  AC HOLDINGS — PVZ ENGINE v0 (1920x1080 60FPS + BUILT‑IN SOUND)
#  Full HD • Perfect 60 FPS • Windows 10 Optimized
#  No external files – tones generated with winsound.Beep
# ============================================================

FPS = 60
TICK_MS = 1000 // FPS
COLS = 9
ROWS = 5
CELL_W = 100
CELL_H = 100
GRID_X0 = 500
GRID_Y0 = 150
CANVAS_W = 1920
CANVAS_H = 1080
SUN_INTERVAL = 600
SUN_VALUE = 25
SPEED_SCALE = CELL_W / 64.0

# ---- Color Palette ----
C_GRASS_A = "#4a8c3f"
C_GRASS_B = "#5a9c4f"
C_SKY = "#87ceeb"
C_NIGHT = "#1a1a3a"
C_MENU_BG = "#2d5a1e"
C_BTN = "#4a8c3f"
C_BTN_HI = "#6ab85f"
C_TEXT = "#ffffff"
C_GOLD = "#ffd700"
C_RED = "#ff3333"
C_DIM = "#888888"
C_DARK = "#1a1a1a"
C_WHITE = "#ffffff"

# ============================================================
#  BUILT‑IN SOUND MANAGER (uses winsound.Beep, no files)
# ============================================================

class SoundManager:
    def __init__(self):
        # Try to import winsound (Windows only)
        self.winsound = None
        if os.name == 'nt':
            try:
                import winsound
                self.winsound = winsound
            except ImportError:
                pass
        # Map event names to (frequency, duration_ms) tuples
        self.sound_map = {
            # Zombie
            "zombie_spawn": (440, 100),    # A4, short
            "zombie_hit":   (330, 80),      # E4, short
            "zombie_death": (220, 200),     # A3, longer
            "zombie_eat":   (110, 150),     # A2, low
            # Plants
            "plant_peashooter": (523, 50),  # C5, quick
            "plant_snowpea":    (587, 50),  # D5
            "plant_repeater":   (659, 50),  # E5
            "plant_cactus":     (698, 50),  # F5
            "plant_puffshroom": (392, 60),  # G4
            "plant_sunflower":  (784, 80),  # G5
            "plant_cherrybomb": (220, 400), # A3, long explosion
            "plant_jalapeno":   (330, 300), # E4, whoosh
            "plant_potatomine": (146, 150), # D3, low
            "plant_chomper":    (130, 200), # C3, chomp
            "plant_squash":     (164, 100), # E3, squash
            # Other
            "lawnmower":   (523, 300),      # C5, rev
            "sun_collect": (784, 50),       # G5, ping
            "button_click": (440, 30),      # A4, tiny click
        }

    def play_sound(self, key, volume=0.5):
        if not self.winsound:
            return
        if key in self.sound_map:
            freq, dur = self.sound_map[key]
            # Volume is ignored in winsound.Beep (uses system volume)
            self.winsound.Beep(freq, dur)

    def play_music(self, key, loop=True):
        # No music with beeps
        pass

    def stop_music(self):
        pass

    def set_music_volume(self, volume):
        pass

    def set_sound_volume(self, volume):
        pass

sound_mgr = SoundManager()

# ============================================================
#  DATA: Plants, Zombies, Levels, Minigames
# ============================================================

PLANT_DATA = {
    "Peashooter":    {"hp": 300, "cost": 100, "damage": 20, "rate": 90,  "color": "#22aa22", "char": "P", "desc": "Shoots peas at zombies."},
    "Sunflower":     {"hp": 300, "cost": 50,  "damage": 0,  "rate": 150, "color": "#ffdd00", "char": "S", "desc": "Produces sun over time."},
    "Wall-nut":      {"hp": 4000,"cost": 50,  "damage": 0,  "rate": 0,   "color": "#c8a050", "char": "W", "desc": "Blocks zombies with high HP."},
    "Snow Pea":      {"hp": 300, "cost": 175, "damage": 20, "rate": 90,  "color": "#88ccff", "char": "I", "desc": "Shoots frozen peas that slow."},
    "Cherry Bomb":   {"hp": 1,   "cost": 150, "damage": 1800,"rate": 1,  "color": "#ff2200", "char": "B", "desc": "Explodes in a 3x3 area."},
    "Repeater":      {"hp": 300, "cost": 200, "damage": 20, "rate": 90,  "color": "#118811", "char": "R", "desc": "Shoots two peas at a time."},
    "Chomper":       {"hp": 300, "cost": 150, "damage": 1800,"rate": 240, "color": "#8822cc", "char": "C", "desc": "Devours a zombie whole."},
    "Potato Mine":   {"hp": 300, "cost": 25,  "damage": 1800,"rate": 0,  "color": "#aa6633", "char": "M", "desc": "Explodes on contact after arming."},
    "Jalapeno":      {"hp": 1,   "cost": 125, "damage": 1800,"rate": 1,  "color": "#ff4400", "char": "J", "desc": "Burns an entire lane."},
    "Squash":        {"hp": 300, "cost": 50,  "damage": 1800,"rate": 0,  "color": "#336633", "char": "Q", "desc": "Jumps on and squashes a zombie."},
    "Torchwood":     {"hp": 300, "cost": 175, "damage": 0,  "rate": 0,   "color": "#ff8800", "char": "T", "desc": "Turns peas into fireballs (2x)."},
    "Tall-nut":      {"hp": 8000,"cost": 125, "damage": 0,  "rate": 0,   "color": "#8a6030", "char": "N", "desc": "Taller wall. Blocks vaulters."},
    "Puff-shroom":   {"hp": 300, "cost": 0,   "damage": 20, "rate": 90,  "color": "#cc88ff", "char": "p", "desc": "Free short-range shooter."},
    "Lily Pad":      {"hp": 300, "cost": 25,  "damage": 0,  "rate": 0,   "color": "#44bb44", "char": "L", "desc": "Platform for pool plants."},
    "Cactus":        {"hp": 300, "cost": 125, "damage": 20, "rate": 90,  "color": "#228822", "char": "X", "desc": "Shoots spikes. Pops balloons."},
}

ZOMBIE_DATA = {
    "Basic":         {"hp": 200,  "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#667744", "char": "Z", "desc": "Your basic zombie."},
    "Flag":          {"hp": 200,  "speed": 0.5 * SPEED_SCALE, "damage": 100, "color": "#887744", "char": "F", "desc": "Signals a huge wave."},
    "Conehead":      {"hp": 560,  "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#cc7722", "char": "c", "desc": "Cone adds durability."},
    "Buckethead":    {"hp": 1300, "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#888888", "char": "b", "desc": "Bucket = very tough."},
    "Pole Vaulter":  {"hp": 340,  "speed": 0.8 * SPEED_SCALE, "damage": 100, "color": "#556633", "char": "v", "desc": "Jumps over the first plant."},
    "Newspaper":     {"hp": 340,  "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#aaaaaa", "char": "n", "desc": "Gets angry when paper lost."},
    "Screen Door":   {"hp": 1200, "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#999999", "char": "d", "desc": "Screen door as shield."},
    "Football":      {"hp": 1600, "speed": 0.7 * SPEED_SCALE, "damage": 100, "color": "#334433", "char": "f", "desc": "Fast and armored."},
    "Dancing":       {"hp": 500,  "speed": 0.5 * SPEED_SCALE, "damage": 100, "color": "#cc44cc", "char": "D", "desc": "Summons backup dancers."},
    "Gargantuar":    {"hp": 3000, "speed": 0.3 * SPEED_SCALE, "damage": 1800,"color": "#444444", "char": "G", "desc": "Giant. Crushes plants."},
    "Imp":           {"hp": 80,   "speed": 1.0 * SPEED_SCALE, "damage": 100, "color": "#668866", "char": "i", "desc": "Thrown by Gargantuar."},
    "Zombie Yeti":   {"hp": 1400, "speed": 0.4 * SPEED_SCALE, "damage": 100, "color": "#aabbcc", "char": "Y", "desc": "Rare. Drops diamonds."},
}

def make_wave(zombie_list, delay_frames=300):
    return {"zombies": zombie_list, "delay": delay_frames}

LEVELS = [
    {"name": "1-1 Day", "night": False, "pool": False, "waves": [
        make_wave([("Basic", r) for r in random.sample(range(ROWS), 2)], 300),
        make_wave([("Basic", r) for r in random.sample(range(ROWS), 3)], 400),
        make_wave([("Basic", r) for r in range(ROWS)] + [("Flag", 2)], 500),
    ], "plants": ["Peashooter", "Sunflower"]},
    {"name": "1-2 Day", "night": False, "pool": False, "waves": [
        make_wave([("Basic", r) for r in random.sample(range(ROWS), 3)], 300),
        make_wave([("Conehead", r) for r in random.sample(range(ROWS), 2)], 400),
        make_wave([("Basic", r) for r in range(ROWS)] + [("Conehead", 1), ("Flag", 2)], 500),
    ], "plants": ["Peashooter", "Sunflower", "Cherry Bomb"]},
    {"name": "1-3 Day", "night": False, "pool": False, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 250),
        make_wave([("Conehead", r) for r in random.sample(range(ROWS), 3)], 350),
        make_wave([("Conehead", r) for r in range(ROWS)] + [("Buckethead", 2), ("Flag", 0)], 400),
    ], "plants": ["Peashooter", "Sunflower", "Cherry Bomb", "Wall-nut"]},
    {"name": "1-4 Day", "night": False, "pool": False, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 200),
        make_wave([("Conehead", r) for r in range(ROWS)], 300),
        make_wave([("Buckethead", r) for r in random.sample(range(ROWS), 3)] + [("Flag", 2)], 350),
        make_wave([("Conehead", r) for r in range(ROWS)] + [("Buckethead", r) for r in range(ROWS)], 400),
    ], "plants": ["Peashooter", "Sunflower", "Cherry Bomb", "Wall-nut", "Snow Pea"]},
    {"name": "1-5 Day", "night": False, "pool": False, "waves": [
        make_wave([("Conehead", r) for r in range(ROWS)], 200),
        make_wave([("Buckethead", r) for r in range(ROWS)], 300),
        make_wave([("Pole Vaulter", r) for r in random.sample(range(ROWS), 3)] + [("Flag", 2)], 300),
        make_wave([("Buckethead", r) for r in range(ROWS)] + [("Conehead", r) for r in range(ROWS)] + [("Flag", 0)], 350),
    ], "plants": ["Peashooter", "Sunflower", "Cherry Bomb", "Wall-nut", "Snow Pea", "Repeater"]},
    {"name": "2-1 Night", "night": True, "pool": False, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 300),
        make_wave([("Newspaper", r) for r in random.sample(range(ROWS), 3)], 350),
        make_wave([("Conehead", r) for r in range(ROWS)] + [("Newspaper", 1), ("Flag", 2)], 400),
    ], "plants": ["Puff-shroom", "Sunflower", "Peashooter", "Cherry Bomb", "Wall-nut"]},
    {"name": "2-2 Night", "night": True, "pool": False, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 250),
        make_wave([("Newspaper", r) for r in range(ROWS)], 300),
        make_wave([("Screen Door", r) for r in random.sample(range(ROWS), 3)] + [("Flag", 2)], 350),
        make_wave([("Conehead", r) for r in range(ROWS)] + [("Screen Door", r) for r in range(ROWS)], 400),
    ], "plants": ["Puff-shroom", "Sunflower", "Peashooter", "Cherry Bomb", "Wall-nut", "Chomper"]},
    {"name": "3-1 Pool", "night": False, "pool": True, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 300),
        make_wave([("Conehead", r) for r in range(ROWS)], 350),
        make_wave([("Buckethead", r) for r in random.sample(range(ROWS), 3)] + [("Flag", 2)], 400),
    ], "plants": ["Peashooter", "Sunflower", "Wall-nut", "Lily Pad", "Snow Pea", "Repeater"]},
    {"name": "4-1 Fog", "night": True, "pool": False, "waves": [
        make_wave([("Basic", r) for r in range(ROWS)], 250),
        make_wave([("Football", r) for r in random.sample(range(ROWS), 2)], 350),
        make_wave([("Football", r) for r in range(ROWS)] + [("Flag", 2)], 400),
        make_wave([("Buckethead", r) for r in range(ROWS)] + [("Football", r) for r in range(ROWS)], 400),
    ], "plants": ["Peashooter", "Sunflower", "Wall-nut", "Snow Pea", "Repeater", "Torchwood"]},
    {"name": "5-1 Roof", "night": False, "pool": False, "waves": [
        make_wave([("Conehead", r) for r in range(ROWS)], 250),
        make_wave([("Buckethead", r) for r in range(ROWS)], 300),
        make_wave([("Football", r) for r in range(ROWS)] + [("Flag", 2)], 350),
        make_wave([("Gargantuar", 2), ("Gargantuar", 4)], 400),
        make_wave([("Gargantuar", r) for r in range(ROWS)] + [("Imp", r) for r in range(ROWS)] + [("Flag", 0)], 500),
    ], "plants": ["Peashooter", "Sunflower", "Wall-nut", "Snow Pea", "Repeater", "Cherry Bomb", "Jalapeno", "Tall-nut"]},
]

MINIGAMES = [
    {"name": "Wall-nut Bowling", "desc": "Bowl wall-nuts to crush zombies!", "type": "bowling"},
    {"name": "Slot Machine", "desc": "Spin slots for random plants!", "type": "slots"},
    {"name": "Zombie Blitz", "desc": "Survive endless fast waves!", "type": "blitz"},
    {"name": "Column Defense", "desc": "Pre-placed plants, survive 5 waves.", "type": "column"},
    {"name": "Last Stand", "desc": "5000 sun, set up, survive 5 flags.", "type": "laststand"},
]

# ============================================================
#  ENTITIES
# ============================================================

class Projectile:
    __slots__ = ("x", "y", "row", "damage", "speed", "color", "frozen", "fire", "is_pea")
    def __init__(self, x, y, row, damage, speed=6.25, color="#22cc22", frozen=False, fire=False, is_pea=True):
        self.x, self.y, self.row = x, y, row
        self.damage, self.speed, self.color = damage, speed, color
        self.frozen, self.fire = frozen, fire
        self.is_pea = is_pea

class Sun:
    __slots__ = ("x", "y", "target_y", "value", "lifetime", "falling")
    def __init__(self, x, y, target_y, value=SUN_VALUE, falling=True):
        self.x, self.y, self.target_y = x, y, target_y
        self.value, self.falling = value, falling
        self.lifetime = 600

class Plant:
    __slots__ = ("name", "row", "col", "hp", "max_hp", "damage", "rate", "color", "timer", "armed", "eaten")
    def __init__(self, name, row, col):
        d = PLANT_DATA[name]
        self.name, self.row, self.col = name, row, col
        self.hp = d["hp"]
        self.max_hp = d["hp"]
        self.damage, self.rate = d["damage"], d["rate"]
        self.color = d["color"]
        self.timer = 0
        self.armed = name != "Potato Mine"
        self.eaten = False

class Zombie:
    __slots__ = ("name", "row", "x", "hp", "max_hp", "speed", "base_speed", "damage", "color", "eating", "slow_timer", "vaulted")
    def __init__(self, name, row, x):
        d = ZOMBIE_DATA[name]
        self.name, self.row = name, row
        self.x = float(x)
        self.hp = d["hp"]
        self.max_hp = d["hp"]
        self.speed = d["speed"]
        self.base_speed = d["speed"]
        self.damage = d["damage"]
        self.color = d["color"]
        self.eating = False
        self.slow_timer = 0
        self.vaulted = False


# ============================================================
#  GAME ENGINE (with sound triggers)
# ============================================================

class PVZEngine:
    def __init__(self, canvas, level_data, on_win, on_lose, on_quit):
        self.cv = canvas
        self.level = level_data
        self.on_win, self.on_lose, self.on_quit = on_win, on_lose, on_quit
        self.running = True
        self.paused = False
        self.frame = 0

        self.sun = 50
        self.sun_timer = 0
        self.plants = []
        self.zombies = []
        self.projectiles = []
        self.suns = []
        self.grid = [[None]*COLS for _ in range(ROWS)]
        self.lawnmowers = [True]*ROWS

        self.wave_idx = 0
        self.wave_timer = 0
        self.all_waves_sent = False

        self.selected_plant = None
        avail = level_data.get("plants", list(PLANT_DATA.keys())[:6])
        self.available_plants = avail[:8]

        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<Button-3>", self.on_right_click)

    def on_click(self, event):
        x, y = event.x, event.y
        # Sun collection
        for s in self.suns[:]:
            if abs(s.x - x) < 30 and abs(s.y - y) < 30:
                self.sun += s.value
                self.suns.remove(s)
                sound_mgr.play_sound("sun_collect")
                return
        # Plant selector click
        for i, pname in enumerate(self.available_plants):
            bx = 8 + i * 90
            by = 8
            if bx <= x <= bx + 80 and by <= y <= by + 60:
                cost = PLANT_DATA[pname]["cost"]
                if self.sun >= cost:
                    self.selected_plant = pname
                    sound_mgr.play_sound("button_click")
                else:
                    self.selected_plant = None
                return
        # Grid placement
        if self.selected_plant:
            col = int((x - GRID_X0) / CELL_W)
            row = int((y - GRID_Y0) / CELL_H)
            if 0 <= row < ROWS and 0 <= col < COLS and self.grid[row][col] is None:
                cost = PLANT_DATA[self.selected_plant]["cost"]
                if self.sun >= cost:
                    self.sun -= cost
                    p = Plant(self.selected_plant, row, col)
                    self.plants.append(p)
                    self.grid[row][col] = p
                    if self.selected_plant == "Cherry Bomb":
                        self._cherry_bomb(row, col)
                        sound_mgr.play_sound("plant_cherrybomb")
                    elif self.selected_plant == "Jalapeno":
                        self._jalapeno(row)
                        sound_mgr.play_sound("plant_jalapeno")
                    elif self.selected_plant == "Potato Mine":
                        sound_mgr.play_sound("plant_potatomine")
                    elif self.selected_plant == "Squash":
                        sound_mgr.play_sound("plant_squash")
                    elif self.selected_plant == "Chomper":
                        sound_mgr.play_sound("plant_chomper")
                    # Other plants may have placement sounds if desired
                    self.selected_plant = None

    def on_right_click(self, event):
        self.selected_plant = None

    def _cherry_bomb(self, row, col):
        for z in self.zombies[:]:
            zc = int((z.x - GRID_X0) / CELL_W)
            if abs(z.row - row) <= 1 and abs(zc - col) <= 1:
                z.hp = 0
                sound_mgr.play_sound("zombie_death")
        p = self.grid[row][col]
        if p:
            self.plants.remove(p)
            self.grid[row][col] = None

    def _jalapeno(self, row):
        for z in self.zombies[:]:
            if z.row == row:
                z.hp = 0
                sound_mgr.play_sound("zombie_death")
        for p in self.plants[:]:
            if p.name == "Jalapeno" and p.row == row:
                self.grid[p.row][p.col] = None
                self.plants.remove(p)
                break

    def update(self):
        if not self.running or self.paused:
            return
        self.frame += 1

        # Sky sun
        self.sun_timer += 1
        if self.sun_timer >= SUN_INTERVAL and not self.level.get("night", False):
            self.sun_timer = 0
            sx = random.randint(GRID_X0, GRID_X0 + COLS * CELL_W - 40)
            ty = random.randint(GRID_Y0, GRID_Y0 + ROWS * CELL_H - 40)
            self.suns.append(Sun(sx, -20, ty))

        # Plant actions
        for p in self.plants[:]:
            if p.hp <= 0:
                self.grid[p.row][p.col] = None
                self.plants.remove(p)
                continue
            p.timer += 1
            if p.name == "Sunflower" and p.rate > 0 and p.timer >= p.rate:
                p.timer = 0
                px = GRID_X0 + p.col * CELL_W + CELL_W // 2
                py = GRID_Y0 + p.row * CELL_H + CELL_H // 2
                self.suns.append(Sun(px, py - 15, py + 30, SUN_VALUE, falling=True))
                sound_mgr.play_sound("plant_sunflower")
            elif p.name in ("Peashooter", "Repeater", "Snow Pea", "Cactus", "Puff-shroom") and p.rate > 0 and p.timer >= p.rate:
                has_zombie = any(z.row == p.row and z.x > GRID_X0 + p.col * CELL_W for z in self.zombies)
                if has_zombie:
                    p.timer = 0
                    px = GRID_X0 + p.col * CELL_W + CELL_W
                    py = GRID_Y0 + p.row * CELL_H + CELL_H // 2
                    frozen = p.name == "Snow Pea"
                    is_pea = p.name in ("Peashooter", "Repeater", "Snow Pea")
                    color = "#88ccff" if frozen else "#22cc22"
                    self.projectiles.append(Projectile(px, py, p.row, p.damage, 6.25, color, frozen=frozen, is_pea=is_pea))
                    if p.name == "Repeater":
                        self.projectiles.append(Projectile(px + 15, py, p.row, p.damage, 6.25, color, frozen=frozen, is_pea=is_pea))
                    # Play shoot sound
                    if p.name == "Peashooter":
                        sound_mgr.play_sound("plant_peashooter")
                    elif p.name == "Repeater":
                        sound_mgr.play_sound("plant_repeater")
                    elif p.name == "Snow Pea":
                        sound_mgr.play_sound("plant_snowpea")
                    elif p.name == "Cactus":
                        sound_mgr.play_sound("plant_cactus")
                    elif p.name == "Puff-shroom":
                        sound_mgr.play_sound("plant_puffshroom")
            elif p.name == "Chomper" and p.rate > 0 and p.timer >= p.rate:
                for z in self.zombies:
                    zc = int((z.x - GRID_X0) / CELL_W)
                    if z.row == p.row and (zc == p.col or zc == p.col + 1):
                        z.hp -= p.damage
                        p.timer = 0
                        sound_mgr.play_sound("plant_chomper")
                        if z.hp <= 0:
                            sound_mgr.play_sound("zombie_death")
                        break
            elif p.name == "Potato Mine" and not p.armed:
                if p.timer >= 180:
                    p.armed = True

        # Projectile movement
        for proj in self.projectiles[:]:
            proj.x += proj.speed
            if proj.x > CANVAS_W:
                self.projectiles.remove(proj)
                continue
            if proj.is_pea and not proj.fire:
                for p in self.plants:
                    if p.name == "Torchwood" and p.row == proj.row:
                        tw_x = GRID_X0 + p.col * CELL_W + CELL_W // 2
                        if abs(proj.x - tw_x) < 15:
                            proj.fire = True
                            proj.damage *= 2
                            proj.color = "#ff6600"
                            proj.frozen = False
                            break
            hit = False
            for z in self.zombies:
                if z.row == proj.row and abs(z.x - proj.x) < 20:
                    z.hp -= proj.damage
                    if proj.frozen:
                        z.slow_timer = 300
                        z.speed = z.base_speed * 0.5
                    hit = True
                    sound_mgr.play_sound("zombie_hit")
                    if z.hp <= 0:
                        sound_mgr.play_sound("zombie_death")
                    break
            if hit and proj in self.projectiles:
                self.projectiles.remove(proj)

        # Sun movement
        for s in self.suns[:]:
            s.lifetime -= 1
            if s.lifetime <= 0:
                self.suns.remove(s)
                continue
            if s.falling and s.y < s.target_y:
                s.y += 1.875

        # Zombie movement + eating
        for z in self.zombies[:]:
            if z.hp <= 0:
                self.zombies.remove(z)
                continue
            if z.slow_timer > 0:
                z.slow_timer -= 1
                if z.slow_timer <= 0:
                    z.speed = z.base_speed

            z.eating = False
            col = int((z.x - GRID_X0) / CELL_W)
            if 0 <= col < COLS:
                target = self.grid[z.row][col]
                if target and target.hp > 0:
                    z.eating = True
                    target.hp -= z.damage / FPS
                    # Play eating sound occasionally (every 30 frames)
                    if random.randint(1, 30) == 1:
                        sound_mgr.play_sound("zombie_eat")
                    if target.hp <= 0:
                        self.grid[target.row][target.col] = None
                        if target in self.plants:
                            self.plants.remove(target)
                    if target.name == "Potato Mine" and target.armed:
                        z.hp -= target.damage
                        sound_mgr.play_sound("plant_potatomine")
                        self.grid[target.row][target.col] = None
                        if target in self.plants:
                            self.plants.remove(target)

            if not z.eating:
                z.x -= z.speed

            if z.name == "Pole Vaulter" and not z.vaulted and 0 <= col < COLS:
                target = self.grid[z.row][col]
                if target and col > 0:
                    z.x = GRID_X0 + (col - 1) * CELL_W + CELL_W // 2
                    z.vaulted = True
                    z.speed = z.base_speed * 0.5

            if z.x <= GRID_X0 - 20:
                if self.lawnmowers[z.row]:
                    self.lawnmowers[z.row] = False
                    sound_mgr.play_sound("lawnmower")
                    for zz in self.zombies[:]:
                        if zz.row == z.row:
                            zz.hp = 0
                            sound_mgr.play_sound("zombie_death")
                else:
                    self.running = False
                    self.on_lose()
                    return

        # Wave spawning
        if not self.all_waves_sent:
            self.wave_timer += 1
            if self.wave_idx < len(self.level["waves"]):
                wave = self.level["waves"][self.wave_idx]
                if self.wave_timer >= wave["delay"]:
                    self.wave_timer = 0
                    for zname, zrow in wave["zombies"]:
                        zx = GRID_X0 + COLS * CELL_W + random.randint(30, 150)
                        self.zombies.append(Zombie(zname, zrow, zx))
                        sound_mgr.play_sound("zombie_spawn")
                    self.wave_idx += 1
            else:
                self.all_waves_sent = True

        if self.all_waves_sent and len(self.zombies) == 0:
            self.running = False
            self.on_win()

    def render(self):
        cv = self.cv
        cv.delete("all")
        is_night = self.level.get("night", False)

        cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_NIGHT if is_night else C_SKY, outline="")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = GRID_X0 + c * CELL_W
                y1 = GRID_Y0 + r * CELL_H
                clr = C_GRASS_A if (r + c) % 2 == 0 else C_GRASS_B
                cv.create_rectangle(x1, y1, x1 + CELL_W, y1 + CELL_H, fill=clr, outline="#3a7c2f", width=2)

        for r in range(ROWS):
            if self.lawnmowers[r]:
                lx = GRID_X0 - 40
                ly = GRID_Y0 + r * CELL_H + CELL_H // 2
                cv.create_rectangle(lx, ly - 15, lx + 30, ly + 15, fill="#555555", outline="#333333", width=2)
                cv.create_text(lx + 15, ly, text="LM", fill=C_RED, font=("Consolas", 10, "bold"))

        for p in self.plants:
            px = GRID_X0 + p.col * CELL_W + CELL_W // 2
            py = GRID_Y0 + p.row * CELL_H + CELL_H // 2
            sz = 32
            cv.create_oval(px - sz, py - sz, px + sz, py + sz, fill=p.color, outline="#000000", width=2)
            cv.create_text(px, py, text=PLANT_DATA[p.name]["char"], fill=C_TEXT, font=("Consolas", 20, "bold"))
            if p.hp < p.max_hp:
                bw = CELL_W - 12
                ratio = max(0, p.hp / p.max_hp)
                bx = px - bw // 2
                by = py - sz - 8
                cv.create_rectangle(bx, by, bx + bw, by + 6, fill="#333333", outline="")
                cv.create_rectangle(bx, by, bx + int(bw * ratio), by + 6, fill=C_GOLD, outline="")

        for z in self.zombies:
            zy = GRID_Y0 + z.row * CELL_H + CELL_H // 2
            sz = 30
            outline = "#88ccff" if z.slow_timer > 0 else "#000000"
            cv.create_rectangle(z.x - sz, zy - sz, z.x + sz, zy + sz, fill=z.color, outline=outline, width=3)
            cv.create_text(z.x, zy, text=ZOMBIE_DATA[z.name]["char"], fill=C_TEXT, font=("Consolas", 20, "bold"))
            bw = CELL_W - 16
            ratio = max(0, z.hp / z.max_hp)
            bx = z.x - bw // 2
            by = zy - sz - 8
            cv.create_rectangle(bx, by, bx + bw, by + 6, fill="#333333", outline="")
            cv.create_rectangle(bx, by, bx + int(bw * ratio), by + 6, fill=C_RED, outline="")

        for proj in self.projectiles:
            cv.create_oval(proj.x - 8, proj.y - 8, proj.x + 8, proj.y + 8, fill=proj.color, outline="")

        for s in self.suns:
            cv.create_oval(s.x - 20, s.y - 20, s.x + 20, s.y + 20, fill=C_GOLD, outline="#ffaa00", width=2)
            cv.create_text(s.x, s.y, text="☀", fill="#fff8e0", font=("Segoe UI", 16))

        cv.create_rectangle(0, 0, CANVAS_W, 80, fill=C_DARK, outline="")
        cv.create_text(CANVAS_W - 120, 45, text=f"☀ {self.sun}", fill=C_GOLD, font=("Consolas", 20, "bold"))
        for i, pname in enumerate(self.available_plants):
            bx = 8 + i * 90
            by = 8
            cost = PLANT_DATA[pname]["cost"]
            is_sel = self.selected_plant == pname
            fill = C_BTN_HI if is_sel else (C_BTN if self.sun >= cost else "#333333")
            cv.create_rectangle(bx, by, bx + 80, by + 64, fill=fill, outline="#222222", width=2)
            cv.create_text(bx + 40, by + 22, text=PLANT_DATA[pname]["char"], fill=C_TEXT, font=("Consolas", 20, "bold"))
            cv.create_text(bx + 40, by + 52, text=str(cost), fill=C_GOLD, font=("Consolas", 11))

        total = len(self.level["waves"])
        cv.create_text(CANVAS_W // 2, CANVAS_H - 18, text=f"WAVE {min(self.wave_idx + 1, total)}/{total}", fill=C_TEXT, font=("Consolas", 12, "bold"))
        cv.create_text(CANVAS_W - 120, CANVAS_H - 18, text="ESC = Menu", fill=C_DIM, font=("Consolas", 10))


# ============================================================
#  MINIGAME ENGINES (with sound)
# ============================================================

class WallnutBowling:
    def __init__(self, canvas, on_win, on_lose, on_quit):
        self.cv = canvas
        self.on_win, self.on_lose, self.on_quit = on_win, on_lose, on_quit
        self.running = True
        self.frame = 0
        self.nuts = []
        self.zombies = []
        self.cooldown = 0
        self.score = 0
        self.total_zombies = 30
        self.spawned = 0
        self.cv.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.cooldown <= 0:
            row = int((event.y - GRID_Y0) / CELL_H)
            if 0 <= row < ROWS:
                self.nuts.append({"x": float(GRID_X0), "y": GRID_Y0 + row * CELL_H + CELL_H // 2, "row": row})
                self.cooldown = 40
                sound_mgr.play_sound("plant_walnut")  # Use a generic sound if needed

    def update(self):
        if not self.running:
            return
        self.frame += 1
        self.cooldown = max(0, self.cooldown - 1)

        if self.frame % 120 == 0 and self.spawned < self.total_zombies:
            row = random.randint(0, ROWS - 1)
            self.zombies.append({"x": float(GRID_X0 + COLS * CELL_W + 30), "y": GRID_Y0 + row * CELL_H + CELL_H // 2, "row": row, "hp": 200})
            self.spawned += 1
            sound_mgr.play_sound("zombie_spawn")

        for n in self.nuts[:]:
            n["x"] += 7.5
            for z in self.zombies[:]:
                if z["row"] == n["row"] and abs(z["x"] - n["x"]) < 30:
                    z["hp"] -= 200
                    if z["hp"] <= 0:
                        self.zombies.remove(z)
                        self.score += 1
                        sound_mgr.play_sound("zombie_death")
                    if n in self.nuts:
                        self.nuts.remove(n)
                    sound_mgr.play_sound("zombie_hit")
                    break
            if n in self.nuts and n["x"] > CANVAS_W:
                self.nuts.remove(n)

        for z in self.zombies[:]:
            z["x"] -= 0.45
            if z["x"] < GRID_X0 - 40:
                self.running = False
                self.on_lose()
                return

        if self.spawned >= self.total_zombies and len(self.zombies) == 0:
            self.running = False
            self.on_win()

    def render(self):
        cv = self.cv
        cv.delete("all")
        cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_SKY, outline="")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = GRID_X0 + c * CELL_W
                y1 = GRID_Y0 + r * CELL_H
                cv.create_rectangle(x1, y1, x1 + CELL_W, y1 + CELL_H, fill=C_GRASS_A if (r+c) % 2 == 0 else C_GRASS_B, outline="#3a7c2f", width=2)
        for n in self.nuts:
            cv.create_oval(n["x"]-20, n["y"]-20, n["x"]+20, n["y"]+20, fill="#c8a050", outline="#8a6030", width=2)
        for z in self.zombies:
            cv.create_rectangle(z["x"]-20, z["y"]-24, z["x"]+20, z["y"]+24, fill="#667744", outline="#444444", width=2)
            cv.create_text(z["x"], z["y"], text="Z", fill=C_TEXT, font=("Consolas", 16, "bold"))
        cv.create_rectangle(0, 0, CANVAS_W, 60, fill=C_DARK, outline="")
        cv.create_text(CANVAS_W//2, 30, text=f"WALL-NUT BOWLING — Score: {self.score}/{self.total_zombies}", fill=C_GOLD, font=("Consolas", 16, "bold"))
        cv.create_text(CANVAS_W//2, CANVAS_H-18, text="Click a lane to bowl!", fill=C_TEXT, font=("Consolas", 12))
        cv.create_text(CANVAS_W - 120, CANVAS_H-18, text="ESC = Menu", fill=C_DIM, font=("Consolas", 10))


class ZombieBlitz:
    def __init__(self, canvas, on_win, on_lose, on_quit):
        self.cv = canvas
        self.on_win, self.on_lose, self.on_quit = on_win, on_lose, on_quit
        self.running = True
        self.frame = 0
        level = {"name": "Blitz", "night": False, "pool": False, "waves": [], "plants": list(PLANT_DATA.keys())[:8]}
        self.engine = PVZEngine(canvas, level, on_win, on_lose, on_quit)
        self.engine.sun = 5000
        self.spawn_rate = 180

    def update(self):
        if not self.running:
            return
        self.frame += 1
        if self.frame % self.spawn_rate == 0:
            types = ["Basic", "Conehead", "Buckethead", "Football"]
            for _ in range(random.randint(1, 3)):
                row = random.randint(0, ROWS - 1)
                zx = GRID_X0 + COLS * CELL_W + random.randint(30, 150)
                self.engine.zombies.append(Zombie(random.choice(types), row, zx))
                sound_mgr.play_sound("zombie_spawn")
            self.spawn_rate = max(60, self.spawn_rate - 5)
        self.engine.update()
        self.running = self.engine.running

    def render(self):
        self.engine.render()
        self.cv.create_text(CANVAS_W // 2, CANVAS_H - 18, text=f"ZOMBIE BLITZ — Frame: {self.frame}", fill=C_RED, font=("Consolas", 12, "bold"))


# ============================================================
#  CREDITS SCREEN (scrolling text)
# ============================================================

class CreditsScreen:
    def __init__(self, canvas, on_back):
        self.cv = canvas
        self.on_back = on_back
        self.running = True
        self.scroll_y = CANVAS_H
        self.credits = [
            "=== PLANTS vs ZOMBIES ===",
            "AC HOLDINGS ENGINE v0",
            "",
            "ORIGINAL GAME BY",
            "PopCap Games",
            "",
            "LEAD DESIGNER",
            "George Fan",
            "",
            "PROGRAMMING",
            "Tod Semple",
            "",
            "ART",
            "Rich Werner",
            "",
            "MUSIC & SOUND",
            "Laura Shigihara",
            "",
            "SPECIAL THANKS",
            "All the zombies who donated their brains",
            "",
            "",
            "PRESS ESC TO RETURN",
        ]
        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<Escape>", lambda e: self.on_back())

    def update(self):
        if not self.running:
            return
        self.scroll_y -= 1
        if self.scroll_y < -len(self.credits) * 40:
            self.scroll_y = CANVAS_H

    def render(self):
        self.cv.delete("all")
        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_DARK, outline="")
        y = self.scroll_y
        for line in self.credits:
            self.cv.create_text(CANVAS_W // 2, y, text=line, fill=C_GOLD if line.startswith("==") else C_TEXT,
                                font=("Consolas", 20, "bold" if line.startswith("==") else "normal"))
            y += 40
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 30, text="ESC = Back", fill=C_DIM, font=("Consolas", 12))

    def on_click(self, event):
        pass


# ============================================================
#  MAIN APPLICATION
# ============================================================

class PVZApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AC HOLDINGS — PVZ ENGINE v0 (1920x1080 60FPS + BUILT-IN SOUND)")
        self.root.configure(bg=C_DARK)
        self.root.resizable(False, False)

        self.cv = tk.Canvas(self.root, width=CANVAS_W, height=CANVAS_H, bg=C_DARK, highlightthickness=0)
        self.cv.pack()

        self.engine = None
        self.credits_screen = None
        self.unlocked_levels = list(range(len(LEVELS)))

        # TIMING ACCUMULATOR FIX
        self.last_time = time.perf_counter()
        self.target_dt = 1.0 / FPS
        self.accumulator = 0.0

        self.root.bind("<Escape>", self.on_escape)
        self.show_main_menu()
        self.game_loop()

    def game_loop(self):
        # Calculate Delta Time
        current_time = time.perf_counter()
        frame_time = current_time - self.last_time
        self.last_time = current_time

        # Prevent death-spiral if window freezes or moves
        if frame_time > 0.1:
            frame_time = 0.1

        self.accumulator += frame_time

        updated = False

        # Advance Game Logic exactly 60 times a second
        while self.accumulator >= self.target_dt:
            if self.engine:
                self.engine.update()
            elif self.credits_screen:
                self.credits_screen.update()
            self.accumulator -= self.target_dt
            updated = True

        # Render only if logic has updated
        if updated:
            if self.engine:
                self.engine.render()
            elif self.credits_screen:
                self.credits_screen.render()

        # Fast schedule next poll: 10ms wait ensures we capture our next 16.6ms window smoothly
        self.root.after(10, self.game_loop)

    def on_escape(self, event=None):
        if self.engine:
            self.engine.running = False
            self.engine = None
            self.show_main_menu()
        elif self.credits_screen:
            self.credits_screen = None
            self.show_main_menu()

    # ---- SCREENS ----

    def show_main_menu(self):
        self.engine = None
        self.credits_screen = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.unbind("<Button-3>")

        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_MENU_BG, outline="")

        self.cv.create_text(CANVAS_W // 2, 120, text="PLANTS vs ZOMBIES", fill=C_GOLD, font=("Segoe UI", 48, "bold"))
        self.cv.create_text(CANVAS_W // 2, 180, text="AC HOLDINGS ENGINE v0 • 60 FPS • FULL HD", fill=C_TEXT, font=("Consolas", 16))

        btns = [
            ("ADVENTURE", self.show_level_select),
            ("MINIGAMES", self.show_minigame_select),
            ("ALMANAC", self.show_almanac),
            ("CREDITS", self.show_credits),
            ("QUIT", self.root.destroy),
        ]
        self._menu_rects = []
        for i, (label, cmd) in enumerate(btns):
            bx = CANVAS_W // 2 - 200
            by = 280 + i * 80
            rect = self.cv.create_rectangle(bx, by, bx + 400, by + 60, fill=C_BTN, outline=C_GOLD, width=3)
            self.cv.create_text(bx + 200, by + 30, text=label, fill=C_TEXT, font=("Segoe UI", 22, "bold"))
            self._menu_rects.append((bx, by, bx + 400, by + 60, cmd))

        self.cv.create_text(CANVAS_W // 2, 750, text="CONTROLS", fill=C_GOLD, font=("Segoe UI", 24, "bold"))
        controls = [
            "Left Click: Select / Plant / Collect Sun",
            "Right Click: Cancel Selection",
            "ESC: Return to Main Menu (anytime)",
        ]
        y = 810
        for line in controls:
            self.cv.create_text(CANVAS_W // 2, y, text=line, fill=C_TEXT, font=("Consolas", 14))
            y += 30

        self.cv.bind("<Button-1>", self._menu_click)

    def _menu_click(self, event):
        for x1, y1, x2, y2, cmd in self._menu_rects:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                cmd()
                return

    def show_level_select(self):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")

        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_MENU_BG, outline="")
        self.cv.create_text(CANVAS_W // 2, 60, text="LEVEL SELECT", fill=C_GOLD, font=("Segoe UI", 32, "bold"))

        self._menu_rects = []
        cols = 5
        for i, lvl in enumerate(LEVELS):
            c = i % cols
            r = i // cols
            bx = 150 + c * 280
            by = 130 + r * 90
            self.cv.create_rectangle(bx, by, bx + 240, by + 70, fill=C_BTN, outline=C_GOLD, width=2)
            self.cv.create_text(bx + 120, by + 35, text=lvl["name"], fill=C_TEXT, font=("Consolas", 14, "bold"))
            self._menu_rects.append((bx, by, bx + 240, by + 70, lambda idx=i: self.start_level(idx)))

        bx, by = 40, CANVAS_H - 70
        self.cv.create_rectangle(bx, by, bx + 180, by + 50, fill=C_RED, outline="", width=2)
        self.cv.create_text(bx + 90, by + 25, text="BACK", fill=C_TEXT, font=("Consolas", 16, "bold"))
        self._menu_rects.append((bx, by, bx + 180, by + 50, self.show_main_menu))
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self.cv.bind("<Button-1>", self._menu_click)

    def show_minigame_select(self):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")

        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_MENU_BG, outline="")
        self.cv.create_text(CANVAS_W // 2, 60, text="MINIGAMES", fill=C_GOLD, font=("Segoe UI", 32, "bold"))

        self._menu_rects = []
        for i, mg in enumerate(MINIGAMES):
            bx = CANVAS_W // 2 - 300
            by = 150 + i * 90
            self.cv.create_rectangle(bx, by, bx + 600, by + 70, fill=C_BTN, outline=C_GOLD, width=2)
            self.cv.create_text(bx + 300, by + 25, text=mg["name"], fill=C_TEXT, font=("Consolas", 16, "bold"))
            self.cv.create_text(bx + 300, by + 50, text=mg["desc"], fill=C_DIM, font=("Consolas", 12))
            self._menu_rects.append((bx, by, bx + 600, by + 70, lambda idx=i: self.start_minigame(idx)))

        bx, by = 40, CANVAS_H - 70
        self.cv.create_rectangle(bx, by, bx + 180, by + 50, fill=C_RED, outline="", width=2)
        self.cv.create_text(bx + 90, by + 25, text="BACK", fill=C_TEXT, font=("Consolas", 16, "bold"))
        self._menu_rects.append((bx, by, bx + 180, by + 50, self.show_main_menu))
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self.cv.bind("<Button-1>", self._menu_click)

    def show_almanac(self):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self._menu_rects = []

        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_DARK, outline="")
        self.cv.create_text(CANVAS_W // 2, 40, text="ALMANAC", fill=C_GOLD, font=("Segoe UI", 32, "bold"))

        btns = [
            ("PLANTS", self._show_almanac_plants),
            ("ZOMBIES", self._show_almanac_zombies),
            ("BACK", self.show_main_menu),
        ]
        for i, (label, cmd) in enumerate(btns):
            bx = 150 + i * 500
            by = 80
            self.cv.create_rectangle(bx, by, bx + 300, by + 50, fill=C_BTN, outline=C_GOLD, width=2)
            self.cv.create_text(bx + 150, by + 25, text=label, fill=C_TEXT, font=("Consolas", 16, "bold"))
            self._menu_rects.append((bx, by, bx + 300, by + 50, cmd))

        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self._show_almanac_plants()
        self.cv.bind("<Button-1>", self._menu_click)

    def _show_almanac_plants(self):
        self.cv.delete("almanac_content")
        y = 160
        for name, d in PLANT_DATA.items():
            self.cv.create_oval(50, y - 15, 80, y + 15, fill=d["color"], outline="#000", width=2, tags="almanac_content")
            self.cv.create_text(90, y, text=d["char"], fill=C_TEXT, font=("Consolas", 16, "bold"), anchor="w", tags="almanac_content")
            self.cv.create_text(120, y - 10, text=name, fill=C_GOLD, font=("Consolas", 14, "bold"), anchor="w", tags="almanac_content")
            self.cv.create_text(120, y + 12, text=f"HP:{d['hp']}  Cost:{d['cost']}  DMG:{d['damage']}  {d['desc']}", fill=C_DIM, font=("Consolas", 10), anchor="w", tags="almanac_content")
            y += 45

    def _show_almanac_zombies(self):
        self.cv.delete("almanac_content")
        y = 160
        for name, d in ZOMBIE_DATA.items():
            self.cv.create_rectangle(50, y - 15, 80, y + 15, fill=d["color"], outline="#000", width=2, tags="almanac_content")
            self.cv.create_text(90, y, text=d["char"], fill=C_TEXT, font=("Consolas", 16, "bold"), anchor="w", tags="almanac_content")
            self.cv.create_text(120, y - 10, text=name, fill=C_RED, font=("Consolas", 14, "bold"), anchor="w", tags="almanac_content")
            self.cv.create_text(120, y + 12, text=f"HP:{d['hp']}  SPD:{d['speed']:.1f}  DMG:{d['damage']}  {d['desc']}", fill=C_DIM, font=("Consolas", 10), anchor="w", tags="almanac_content")
            y += 45

    def show_credits(self):
        self.engine = None
        self.credits_screen = CreditsScreen(self.cv, self.show_main_menu)

    # ---- GAME START ----

    def start_level(self, idx):
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.unbind("<Button-3>")
        self.engine = PVZEngine(self.cv, LEVELS[idx], lambda: self._on_win(idx), self._on_lose, self.show_main_menu)

    def start_minigame(self, idx):
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.unbind("<Button-3>")
        mg = MINIGAMES[idx]
        if mg["type"] == "bowling":
            self.engine = WallnutBowling(self.cv, self._on_mg_win, self._on_lose, self.show_main_menu)
        elif mg["type"] == "blitz":
            self.engine = ZombieBlitz(self.cv, self._on_mg_win, self._on_lose, self.show_main_menu)
        else:
            level = {"name": mg["name"], "night": False, "pool": False,
                     "waves": [make_wave([("Basic", r) for r in range(ROWS)], 200),
                               make_wave([("Conehead", r) for r in range(ROWS)], 250),
                               make_wave([("Buckethead", r) for r in range(ROWS)] + [("Flag", 2)], 300),
                               make_wave([("Football", r) for r in range(ROWS)] + [("Conehead", r) for r in range(ROWS)], 350),
                               make_wave([("Gargantuar", 2)] + [("Buckethead", r) for r in range(ROWS)] + [("Flag", 0)], 400)],
                     "plants": list(PLANT_DATA.keys())[:8]}
            self.engine = PVZEngine(self.cv, level, self._on_mg_win, self._on_lose, self.show_main_menu)
            if mg["type"] == "laststand":
                self.engine.sun = 5000
            elif mg["type"] == "slots":
                self.engine.sun = 0
                self.engine.sun_timer = 0

    def _on_win(self, level_idx):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_MENU_BG, outline="")
        self.cv.create_text(CANVAS_W // 2, CANVAS_H // 2 - 50, text="LEVEL COMPLETE!", fill=C_GOLD, font=("Segoe UI", 48, "bold"))
        self.cv.create_text(CANVAS_W // 2, CANVAS_H // 2 + 30, text=LEVELS[level_idx]["name"], fill=C_TEXT, font=("Consolas", 20))
        self._menu_rects = []
        bx, by = CANVAS_W // 2 - 150, CANVAS_H // 2 + 100
        self.cv.create_rectangle(bx, by, bx + 300, by + 60, fill=C_BTN, outline=C_GOLD, width=3)
        self.cv.create_text(bx + 150, by + 30, text="CONTINUE", fill=C_TEXT, font=("Consolas", 18, "bold"))
        self._menu_rects.append((bx, by, bx + 300, by + 60, self.show_level_select))
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self.cv.bind("<Button-1>", self._menu_click)

    def _on_mg_win(self):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=C_MENU_BG, outline="")
        self.cv.create_text(CANVAS_W // 2, CANVAS_H // 2 - 30, text="MINIGAME COMPLETE!", fill=C_GOLD, font=("Segoe UI", 40, "bold"))
        self._menu_rects = []
        bx, by = CANVAS_W // 2 - 150, CANVAS_H // 2 + 50
        self.cv.create_rectangle(bx, by, bx + 300, by + 60, fill=C_BTN, outline=C_GOLD, width=3)
        self.cv.create_text(bx + 150, by + 30, text="CONTINUE", fill=C_TEXT, font=("Consolas", 18, "bold"))
        self._menu_rects.append((bx, by, bx + 300, by + 60, self.show_minigame_select))
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self.cv.bind("<Button-1>", self._menu_click)

    def _on_lose(self):
        self.engine = None
        self.cv.delete("all")
        self.cv.unbind("<Button-1>")
        self.cv.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#1a0000", outline="")
        self.cv.create_text(CANVAS_W // 2, CANVAS_H // 2 - 30, text="THE ZOMBIES ATE YOUR BRAINS!", fill=C_RED, font=("Segoe UI", 36, "bold"))
        self._menu_rects = []
        bx, by = CANVAS_W // 2 - 150, CANVAS_H // 2 + 50
        self.cv.create_rectangle(bx, by, bx + 300, by + 60, fill=C_RED, outline=C_GOLD, width=3)
        self.cv.create_text(bx + 150, by + 30, text="RETRY", fill=C_TEXT, font=("Consolas", 18, "bold"))
        self._menu_rects.append((bx, by, bx + 300, by + 60, self.show_main_menu))
        self.cv.create_text(CANVAS_W - 120, CANVAS_H - 35, text="ESC = Menu", fill=C_DIM, font=("Consolas", 12))
        self.cv.bind("<Button-1>", self._menu_click)


if __name__ == "__main__":
    # WINDOWS 10 OPTIMIZATIONS
    if os.name == 'nt':
        try:
            # Set Windows Timer Resolution to 1ms for perfect 60 FPS timing
            ctypes.windll.winmm.timeBeginPeriod(1)
            # Make Window High-DPI Aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    root = tk.Tk()
    app = PVZApp(root)
    root.mainloop()

    # Clean up timer resolution on exit
    if os.name == 'nt':
        try:
            ctypes.windll.winmm.timeEndPeriod(1)
        except Exception:
            pass