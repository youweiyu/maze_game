import pygame

# 优化：减小缓冲区，提升音效响应速度
pygame.mixer.init(buffer=256)

SOUND_DIR = "sounds/"  # 你的音乐目录

# 背景音乐
MUSIC = {
    "bk": SOUND_DIR + "bk.wav",
    "boss": SOUND_DIR + "boss.wav",
    "menu": SOUND_DIR + "menu.wav"
}

# 音效
SOUNDS = {
    "click": pygame.mixer.Sound(SOUND_DIR + "click.wav"),
    "explosion": pygame.mixer.Sound(SOUND_DIR + "explosion.wav"),
    "fireball": pygame.mixer.Sound(SOUND_DIR + "fireball.wav"),
    "laugh": pygame.mixer.Sound(SOUND_DIR + "laugh.wav"),
    "level": pygame.mixer.Sound(SOUND_DIR + "level.wav"),
    "lose": pygame.mixer.Sound(SOUND_DIR + "lose.wav"),
    "spend": pygame.mixer.Sound(SOUND_DIR + "spend.wav"),
    "whoosh": pygame.mixer.Sound(SOUND_DIR + "whoosh.wav"),
    "win": pygame.mixer.Sound(SOUND_DIR + "win.wav"),
    "coin": pygame.mixer.Sound(SOUND_DIR + "coin.wav"),  # 新增金币音效
}

def play_music(name, loop=True):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(MUSIC[name])
    pygame.mixer.music.play(-1 if loop else 0)

def stop_music():
    pygame.mixer.music.stop()

def play_sound(name):
    SOUNDS[name].play()
