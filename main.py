import pygame
import json
import random
import sys
import os
import math
from enum import Enum

# Optional imports for enhanced features
try:
    import pygame.gfxdraw
    GFXDRAW_AVAILABLE = True
except ImportError:
    GFXDRAW_AVAILABLE = False
    print("pygame.gfxdraw not available - using basic graphics")

try:
    import pygame_gui
    PYGAME_GUI_AVAILABLE = True
except ImportError:
    PYGAME_GUI_AVAILABLE = False
    # pygame_gui is optional - using basic UI

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Enhanced Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (25, 42, 86)
BLUE = (52, 152, 219)
LIGHT_BLUE = (174, 214, 241)
GREEN = (46, 204, 113)
DARK_GREEN = (39, 174, 96)
LIGHT_GREEN = (200, 255, 200)
RED = (231, 76, 60)
DARK_RED = (192, 57, 43)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)
YELLOW = (241, 196, 15)
GRAY = (149, 165, 166)
LIGHT_GRAY = (236, 240, 241)
DARK_GRAY = (52, 73, 94)
CREAM = (253, 251, 251)
GOLD = (255, 215, 0)

# Game States
class GameState(Enum):
    MENU = 1
    SETTINGS = 2
    LEVEL_SELECT = 3
    QUIZ = 4
    FEEDBACK = 5
    RESULTS = 6
    LEVEL_COMPLETE = 7
    PAUSE = 8

# Level Configuration
LEVELS = {
    1: {"name": "Basic First Aid", "questions": 3, "difficulty": "easy", "unlock_score": 0, "icon": "❤️"},
    2: {"name": "Emergency Response", "questions": 4, "difficulty": "medium", "unlock_score": 20, "icon": "⭐"},
    3: {"name": "Advanced Techniques", "questions": 3, "difficulty": "hard", "unlock_score": 50, "icon": "➕"},
    4: {"name": "CPR Mastery", "questions": 5, "difficulty": "hard", "unlock_score": 80, "icon": "💓"},
    5: {"name": "Expert Level", "questions": 5, "difficulty": "hard", "unlock_score": 120, "icon": "🏆"}
}

class FirstAidQuizGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🏥 First Aid Quiz Game - Professional Edition")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.MENU
        self.previous_state = GameState.MENU
        self.current_question_index = 0
        self.score = 0
        self.total_score = 0
        self.total_questions = 0
        self.selected_answer = -1
        self.show_feedback = False
        self.user_answers = []
        
        # Level system
        self.current_level = 1
        self.max_unlocked_level = 1
        self.level_questions = []
        self.lives = 3
        self.badges = []
        
        # Settings
        self.settings = {
            'sound_enabled': True,
            'music_enabled': True,
            'sound_volume': 0.7,
            'music_volume': 0.3,
            'show_animations': True,
            'difficulty_hints': True
        }
        
        # Animation timers
        self.glow_timer = 0
        self.pulse_timer = 0
        
        # Enhanced systems
        self.particles = []
        self.sounds = {}
        self.create_sound_effects()
        
        # Load game data
        self.load_questions()
        self.load_progress()
    
    def create_sound_effects(self):
        """Create sound effects programmatically"""
        try:
            import numpy as np
            
            # Click sound
            duration = 0.1
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            for i in range(frames):
                time = float(i) / sample_rate
                wave = int(4096 * math.sin(time * 2 * math.pi * 800) * math.exp(-time * 10))
                arr[i] = [wave, wave]
            self.sounds['click'] = pygame.sndarray.make_sound(arr)
            
            # Success sound
            duration = 0.5
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            for i in range(frames):
                time = float(i) / sample_rate
                freq = 523 + (time * 200)  # Rising tone
                wave = int(4096 * math.sin(time * 2 * math.pi * freq) * math.exp(-time * 2))
                arr[i] = [wave, wave]
            self.sounds['correct'] = pygame.sndarray.make_sound(arr)
            
            # Error sound
            duration = 0.3
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            for i in range(frames):
                time = float(i) / sample_rate
                freq = 200 - (time * 50)  # Falling tone
                wave = int(4096 * math.sin(time * 2 * math.pi * freq) * (1 - time / duration))
                arr[i] = [wave, wave]
            self.sounds['wrong'] = pygame.sndarray.make_sound(arr)
            
        except ImportError:
            # NumPy not available - sound effects disabled
            pass
        except Exception as e:
            print(f"Could not create sound effects: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.settings['sound_enabled'] and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.settings['sound_volume'])
            sound.play()
    
    def add_particle(self, x, y, color, velocity, life):
        """Add a particle to the system"""
        self.particles.append({
            'x': x, 'y': y, 'color': color,
            'vx': velocity[0], 'vy': velocity[1],
            'life': life, 'max_life': life
        })
    
    def update_particles(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            size = max(1, int(3 * (particle['life'] / particle['max_life'])))
            try:
                pygame.gfxdraw.filled_circle(self.screen, int(particle['x']), int(particle['y']), size, particle['color'])
                pygame.gfxdraw.aacircle(self.screen, int(particle['x']), int(particle['y']), size, particle['color'])
            except:
                pygame.draw.circle(self.screen, particle['color'], (int(particle['x']), int(particle['y'])), size)
    
    def create_success_particles(self, x, y):
        """Create success particle effect"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(2, 4)
            colors = [GREEN, YELLOW, GOLD]
            color = random.choice(colors)
            life = random.randint(30, 50)
            self.add_particle(x, y, color, (vx, vy), life)
    
    def create_error_particles(self, x, y):
        """Create error particle effect"""
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1, 3)
            colors = [RED, DARK_RED, ORANGE]
            color = random.choice(colors)
            life = random.randint(20, 35)
            self.add_particle(x, y, color, (vx, vy), life)
        
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open('data/questions.json', 'r') as file:
                data = json.load(file)
                all_questions = data['first_aid_questions']
                
                # Organize questions by difficulty
                self.questions_by_difficulty = {
                    'easy': [q for q in all_questions if q['difficulty'] == 'easy'],
                    'medium': [q for q in all_questions if q['difficulty'] == 'medium'],
                    'hard': [q for q in all_questions if q['difficulty'] == 'hard']
                }
                
                # Shuffle each difficulty group
                for difficulty in self.questions_by_difficulty:
                    random.shuffle(self.questions_by_difficulty[difficulty])
                    
        except FileNotFoundError:
            print("Questions file not found!")
            self.questions_by_difficulty = {'easy': [], 'medium': [], 'hard': []}
            
    def load_progress(self):
        """Load game progress from file"""
        try:
            with open('progress.json', 'r') as file:
                progress = json.load(file)
                self.total_score = progress.get('total_score', 0)
                self.max_unlocked_level = progress.get('max_unlocked_level', 1)
                self.badges = progress.get('badges', [])
                self.settings.update(progress.get('settings', {}))
        except FileNotFoundError:
            self.total_score = 0
            self.max_unlocked_level = 1
            self.badges = []
            
    def save_progress(self):
        """Save game progress to file"""
        progress = {
            'total_score': self.total_score,
            'max_unlocked_level': self.max_unlocked_level,
            'badges': self.badges,
            'settings': self.settings
        }
        try:
            with open('progress.json', 'w') as file:
                json.dump(progress, file)
        except Exception as e:
            print(f"Could not save progress: {e}")
            
    def prepare_level_questions(self, level):
        """Prepare questions for a specific level"""
        level_config = LEVELS[level]
        difficulty = level_config['difficulty']
        question_count = level_config['questions']
        
        available_questions = self.questions_by_difficulty[difficulty].copy()
        random.shuffle(available_questions)
        
        self.level_questions = available_questions[:question_count]
        self.total_questions = len(self.level_questions)
        
    def draw_gradient_background(self, start_color=BLUE, end_color=PURPLE):
        """Draw gradient background"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_card(self, x, y, width, height, color=WHITE, shadow=True, border_radius=15):
        """Draw modern card with shadow"""
        if shadow:
            # Shadow
            shadow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (5, 5, width, height), border_radius=border_radius)
            self.screen.blit(shadow_surface, (x - 5, y - 5))
        
        # Main card
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=border_radius)
        pygame.draw.rect(self.screen, LIGHT_GRAY, (x, y, width, height), 2, border_radius=border_radius)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_text(self, text, font, color, x, y, center=False, max_width=None):
        """Draw text with proper alignment"""
        if max_width:
            words = text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            total_height = 0
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, color)
                if center:
                    text_rect = text_surface.get_rect(center=(x, y + i * font.get_height()))
                    self.screen.blit(text_surface, text_rect)
                else:
                    self.screen.blit(text_surface, (x, y + i * font.get_height()))
                total_height += font.get_height()
            
            return total_height
        else:
            text_surface = font.render(text, True, color)
            if center:
                text_rect = text_surface.get_rect(center=(x, y))
                self.screen.blit(text_surface, text_rect)
            else:
                self.screen.blit(text_surface, (x, y))
            return text_surface.get_height()
    
    def draw_button(self, text, x, y, width, height, color, text_color, hover=False):
        """Draw professional button"""
        # Hover effect
        if hover:
            color = tuple(min(255, c + 30) for c in color)
            # Glow effect
            glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
            glow_color = (*color[:3], 100)
            pygame.draw.rect(glow_surface, glow_color, (10, 10, width, height), border_radius=12)
            self.screen.blit(glow_surface, (x - 10, y - 10))
        
        # Button shadow
        shadow_surface = pygame.Surface((width + 6, height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), (3, 3, width, height), border_radius=10)
        self.screen.blit(shadow_surface, (x - 3, y - 3))
        
        # Main button
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=10)
        
        # Border
        border_color = tuple(max(0, c - 30) for c in color)
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2, border_radius=10)
        
        # Text - properly centered
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_progress_bar(self, x, y, width, height, progress, bg_color=LIGHT_GRAY, fill_color=GREEN):
        """Draw animated progress bar"""
        # Background
        pygame.draw.rect(self.screen, bg_color, (x, y, width, height), border_radius=height//2)
        
        # Progress fill
        fill_width = int(width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color, (x, y, fill_width, height), border_radius=height//2)
        
        # Border
        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, width, height), 2, border_radius=height//2)
    
    def draw_lives_display(self):
        """Draw hearts representing lives with animation"""
        heart_size = 30
        start_x = 50
        start_y = 50
        
        for i in range(3):
            heart_x = start_x + i * (heart_size + 10)
            if i < self.lives:
                # Animated beating heart
                beat_scale = 1.0 + 0.1 * math.sin(self.pulse_timer * 3 + i * 0.5)
                heart_surface = self.font_medium.render("❤️", True, RED)
                scaled_heart = pygame.transform.scale(heart_surface, 
                    (int(heart_surface.get_width() * beat_scale), 
                     int(heart_surface.get_height() * beat_scale)))
                self.screen.blit(scaled_heart, (heart_x, start_y))
            else:
                # Empty heart
                self.draw_text("🤍", self.font_medium, LIGHT_GRAY, heart_x, start_y)
    
    def draw_animated_background(self):
        """Draw animated gradient background with floating elements"""
        # Base animated gradient
        wave_offset = math.sin(self.glow_timer * 0.5) * 20
        for y in range(SCREEN_HEIGHT):
            ratio = (y + wave_offset) / SCREEN_HEIGHT
            ratio = max(0, min(1, ratio))
            
            # Dynamic colors
            start_color = (30 + int(20 * math.sin(self.glow_timer * 0.3)), 
                          80 + int(30 * math.cos(self.glow_timer * 0.2)), 
                          150 + int(40 * math.sin(self.glow_timer * 0.4)))
            end_color = (80 + int(30 * math.cos(self.glow_timer * 0.2)), 
                        50 + int(20 * math.sin(self.glow_timer * 0.3)), 
                        120 + int(35 * math.cos(self.glow_timer * 0.5)))
            
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Floating medical symbols
        symbols = ["⚕️", "🏥", "💊", "🩺", "🚑"]
        for i, symbol in enumerate(symbols):
            x = 100 + i * 200 + 50 * math.sin(self.glow_timer * 0.8 + i)
            y = 100 + 30 * math.cos(self.glow_timer * 0.6 + i * 0.7)
            alpha = int(100 + 50 * math.sin(self.glow_timer * 0.4 + i))
            
            symbol_surface = self.font_large.render(symbol, True, (255, 255, 255, alpha))
            self.screen.blit(symbol_surface, (x, y))
    
    def draw_enhanced_card(self, x, y, width, height):
        """Draw enhanced card with multiple layers and effects"""
        # Multiple shadow layers for depth
        for i in range(5):
            shadow_offset = i * 2
            shadow_alpha = 60 - i * 10
            shadow_surface = pygame.Surface((width + shadow_offset * 2, height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (shadow_offset, shadow_offset, width, height), border_radius=20)
            self.screen.blit(shadow_surface, (x - shadow_offset, y - shadow_offset))
        
        # Main card with gradient
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(height):
            ratio = i / height
            r = int(255 * (1 - ratio * 0.1))
            g = int(255 * (1 - ratio * 0.1))
            b = int(255 * (1 - ratio * 0.1))
            pygame.draw.line(card_surface, (r, g, b), (0, i), (width, i))
        
        pygame.draw.rect(card_surface, (0, 0, 0, 0), (0, 0, width, height), 3, border_radius=20)
        self.screen.blit(card_surface, (x, y))
        
        # Glowing border
        glow_intensity = int(100 + 50 * math.sin(self.glow_timer))
        glow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 150, 255, glow_intensity), 
                        (5, 5, width, height), 3, border_radius=20)
        self.screen.blit(glow_surface, (x - 5, y - 5))
    
    def draw_glowing_title(self, text, center_x, center_y):
        """Draw title with glowing effect"""
        # Glow layers
        glow_colors = [(100, 150, 255, 30), (150, 200, 255, 20), (200, 230, 255, 10)]
        for i, color in enumerate(glow_colors):
            offset = (i + 1) * 2
            glow_surface = self.font_title.render(text, True, color[:3])
            glow_rect = glow_surface.get_rect(center=(center_x + offset, center_y + offset))
            self.screen.blit(glow_surface, glow_rect)
        
        # Main title
        title_surface = self.font_title.render(text, True, DARK_BLUE)
        title_rect = title_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(title_surface, title_rect)
        
        # Animated shine effect
        shine_x = center_x - 200 + (400 * ((self.glow_timer * 0.5) % 2))
        if 0 <= shine_x <= SCREEN_WIDTH:
            shine_surface = pygame.Surface((20, 80), pygame.SRCALPHA)
            pygame.draw.rect(shine_surface, (255, 255, 255, 100), (0, 0, 20, 80))
            self.screen.blit(shine_surface, (shine_x, center_y - 40))
    
    def draw_animated_subtitle(self, text, center_x, center_y):
        """Draw subtitle with typewriter effect"""
        # Pulsing color effect
        pulse = math.sin(self.pulse_timer * 2)
        r = int(155 + 50 * pulse)
        g = int(89 + 30 * pulse)
        b = int(182 + 40 * pulse)
        
        subtitle_surface = self.font_medium.render(text, True, (r, g, b))
        subtitle_rect = subtitle_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_medical_decorations(self, card_x, card_y, card_width, card_height):
        """Draw decorative medical elements around the card"""
        # Corner decorations
        decorations = ["⚕️", "🏥", "💊", "🩺"]
        positions = [
            (card_x - 30, card_y - 30),  # Top left
            (card_x + card_width + 10, card_y - 30),  # Top right
            (card_x - 30, card_y + card_height + 10),  # Bottom left
            (card_x + card_width + 10, card_y + card_height + 10)  # Bottom right
        ]
        
        for i, (decoration, pos) in enumerate(zip(decorations, positions)):
            # Rotating animation
            angle = self.glow_timer * 30 + i * 90
            scale = 1.0 + 0.2 * math.sin(self.pulse_timer * 2 + i)
            
            decoration_surface = self.font_large.render(decoration, True, GOLD)
            scaled_surface = pygame.transform.scale(decoration_surface, 
                (int(decoration_surface.get_width() * scale), 
                 int(decoration_surface.get_height() * scale)))
            rotated_surface = pygame.transform.rotate(scaled_surface, angle)
            
            rect = rotated_surface.get_rect(center=pos)
            self.screen.blit(rotated_surface, rect)
    
    def draw_menu(self):
        """Draw the main menu with enhanced game-like visuals"""
        # Animated gradient background with floating elements
        self.draw_animated_background()
        
        # Main content card with enhanced styling
        card_width = 900
        card_height = 650
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2
        
        # Enhanced card with multiple layers and glow
        self.draw_enhanced_card(card_x, card_y, card_width, card_height)
        
        # Animated title with glow effect
        title_text = "🏥 FIRST AID QUIZ GAME"
        self.draw_glowing_title(title_text, card_x + card_width // 2, card_y + 80)
        
        # Animated subtitle with typewriter effect
        subtitle_text = "⚡ PROFESSIONAL MEDICAL TRAINING SIMULATOR ⚡"
        self.draw_animated_subtitle(subtitle_text, card_x + card_width // 2, card_y + 140)
        
        # Game-like decorative elements
        self.draw_medical_decorations(card_x, card_y, card_width, card_height)
        
        # Stats card - properly aligned
        stats_card_y = card_y + 200
        stats_card_height = 80
        self.draw_card(card_x + 50, stats_card_y, card_width - 100, stats_card_height, LIGHT_BLUE)
        
        # Stats text - evenly distributed
        stats_y = stats_card_y + 30
        col_width = (card_width - 100) // 3
        
        # Total Score
        score_text = f"Total Score: {self.total_score}"
        score_x = card_x + 70 + col_width // 2 - self.font_small.size(score_text)[0] // 2
        self.draw_text(score_text, self.font_small, DARK_BLUE, score_x, stats_y)
        
        # Max Level
        level_text = f"Max Level: {self.max_unlocked_level}/5"
        level_x = card_x + 70 + col_width + col_width // 2 - self.font_small.size(level_text)[0] // 2
        self.draw_text(level_text, self.font_small, DARK_BLUE, level_x, stats_y)
        
        # Badges
        badge_text = f"Badges: {len(self.badges)}"
        badge_x = card_x + 70 + col_width * 2 + col_width // 2 - self.font_small.size(badge_text)[0] // 2
        self.draw_text(badge_text, self.font_small, DARK_BLUE, badge_x, stats_y)
        
        # Action buttons - properly centered and aligned
        button_y = stats_card_y + 120
        button_width = 180
        button_height = 60
        button_spacing = 20
        total_button_width = (button_width * 4) + (button_spacing * 3)
        start_button_x = card_x + (card_width - total_button_width) // 2
        
        mouse_pos = pygame.mouse.get_pos()
        buttons = {}
        
        # Level Select button
        level_select_x = start_button_x
        level_select_rect = pygame.Rect(level_select_x, button_y, button_width, button_height)
        level_hover = level_select_rect.collidepoint(mouse_pos)
        buttons['level_select'] = self.draw_button("🎯 Select Level", level_select_x, button_y, 
                                                  button_width, button_height, GREEN, WHITE, level_hover)
        
        # Quick Play button
        quick_play_x = start_button_x + button_width + button_spacing
        quick_play_rect = pygame.Rect(quick_play_x, button_y, button_width, button_height)
        quick_hover = quick_play_rect.collidepoint(mouse_pos)
        buttons['quick_play'] = self.draw_button("⚡ Quick Play", quick_play_x, button_y, 
                                                button_width, button_height, BLUE, WHITE, quick_hover)
        
        # Settings button
        settings_x = start_button_x + (button_width + button_spacing) * 2
        settings_rect = pygame.Rect(settings_x, button_y, button_width, button_height)
        settings_hover = settings_rect.collidepoint(mouse_pos)
        buttons['settings'] = self.draw_button("⚙️ Settings", settings_x, button_y, 
                                              button_width, button_height, PURPLE, WHITE, settings_hover)
        
        # Exit button
        exit_x = start_button_x + (button_width + button_spacing) * 3
        exit_rect = pygame.Rect(exit_x, button_y, button_width, button_height)
        exit_hover = exit_rect.collidepoint(mouse_pos)
        buttons['exit'] = self.draw_button("🚪 Exit", exit_x, button_y, 
                                          button_width, button_height, RED, WHITE, exit_hover)
        
        return buttons
    
    def draw_settings(self):
        """Draw the enhanced settings screen with game-like visuals"""
        # Enhanced animated background
        self.draw_animated_background()
        
        # Main content card with enhanced styling
        card_width = 1000
        card_height = 700
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2
        
        # Enhanced card with glow and multiple layers
        self.draw_enhanced_card(card_x, card_y, card_width, card_height)
        
        # Animated title with glow effect
        title_text = "⚙️ GAME SETTINGS"
        self.draw_glowing_title(title_text, card_x + card_width // 2, card_y + 70)
        
        # Animated subtitle
        subtitle_text = "🎮 CUSTOMIZE YOUR EXPERIENCE 🎮"
        self.draw_animated_subtitle(subtitle_text, card_x + card_width // 2, card_y + 130)
        
        mouse_pos = pygame.mouse.get_pos()
        buttons = {}
        
        # Enhanced settings sections with floating animation
        section_start_y = card_y + 200
        section_width = card_width - 100
        section_height = 120
        section_spacing = 30
        
        # Audio Settings Section with enhanced styling
        audio_float_offset = math.sin(self.glow_timer * 2) * 3
        audio_section_y = section_start_y + audio_float_offset
        self.draw_enhanced_settings_section(card_x + 50, audio_section_y, section_width, section_height, 
                                          "🔊 Audio Settings", LIGHT_BLUE, True)
        
        # Enhanced toggle buttons for audio
        toggle_y = audio_section_y + 60
        toggle_width = 220
        toggle_height = 40
        toggle_spacing = 40
        
        # Sound Effects toggle
        sound_toggle_x = card_x + 100
        sound_rect = pygame.Rect(sound_toggle_x, toggle_y, toggle_width, toggle_height)
        sound_hover = sound_rect.collidepoint(mouse_pos)
        sound_text = f"Sound Effects: {'ON' if self.settings['sound_enabled'] else 'OFF'}"
        sound_color = GREEN if self.settings['sound_enabled'] else RED
        buttons['sound_toggle'] = self.draw_enhanced_toggle_button(sound_text, sound_toggle_x, toggle_y, 
                                                                  toggle_width, toggle_height, sound_color, 
                                                                  WHITE, sound_hover, self.settings['sound_enabled'])
        
        # Music toggle
        music_toggle_x = sound_toggle_x + toggle_width + toggle_spacing
        music_rect = pygame.Rect(music_toggle_x, toggle_y, toggle_width, toggle_height)
        music_hover = music_rect.collidepoint(mouse_pos)
        music_text = f"Music: {'ON' if self.settings['music_enabled'] else 'OFF'}"
        music_color = GREEN if self.settings['music_enabled'] else RED
        buttons['music_toggle'] = self.draw_enhanced_toggle_button(music_text, music_toggle_x, toggle_y, 
                                                                  toggle_width, toggle_height, music_color, 
                                                                  WHITE, music_hover, self.settings['music_enabled'])
        
        # Visual Settings Section with enhanced styling
        visual_float_offset = math.sin(self.glow_timer * 2 + 1) * 3
        visual_section_y = section_start_y + section_height + section_spacing + visual_float_offset
        self.draw_enhanced_settings_section(card_x + 50, visual_section_y, section_width, section_height, 
                                          "🎨 Visual Settings", LIGHT_GREEN, False)
        
        # Enhanced toggle buttons for visual
        visual_toggle_y = visual_section_y + 60
        
        # Animations toggle
        anim_toggle_x = card_x + 100
        anim_rect = pygame.Rect(anim_toggle_x, visual_toggle_y, toggle_width, toggle_height)
        anim_hover = anim_rect.collidepoint(mouse_pos)
        anim_text = f"Animations: {'ON' if self.settings['show_animations'] else 'OFF'}"
        anim_color = GREEN if self.settings['show_animations'] else RED
        buttons['anim_toggle'] = self.draw_enhanced_toggle_button(anim_text, anim_toggle_x, visual_toggle_y, 
                                                                 toggle_width, toggle_height, anim_color, 
                                                                 WHITE, anim_hover, self.settings['show_animations'])
        
        # Hints toggle
        hints_toggle_x = anim_toggle_x + toggle_width + toggle_spacing
        hints_rect = pygame.Rect(hints_toggle_x, visual_toggle_y, toggle_width, toggle_height)
        hints_hover = hints_rect.collidepoint(mouse_pos)
        hints_text = f"Hints: {'ON' if self.settings['difficulty_hints'] else 'OFF'}"
        hints_color = GREEN if self.settings['difficulty_hints'] else RED
        buttons['hints_toggle'] = self.draw_enhanced_toggle_button(hints_text, hints_toggle_x, visual_toggle_y, 
                                                                  toggle_width, toggle_height, hints_color, 
                                                                  WHITE, hints_hover, self.settings['difficulty_hints'])
        
        # Enhanced back button with glow
        back_button_y = card_y + card_height - 80
        back_button_x = card_x + (card_width - 200) // 2
        back_rect = pygame.Rect(back_button_x, back_button_y, 200, 60)
        back_hover = back_rect.collidepoint(mouse_pos)
        buttons['back'] = self.draw_enhanced_button("⬅️ Back to Menu", back_button_x, back_button_y, 
                                                   200, 60, ORANGE, WHITE, back_hover)
        
        # Decorative elements around the settings card
        self.draw_settings_decorations(card_x, card_y, card_width, card_height)
        
        return buttons
    
    def draw_enhanced_settings_section(self, x, y, width, height, title, color, is_audio):
        """Draw enhanced settings section with animations and effects"""
        # Multiple shadow layers for depth
        for i in range(4):
            shadow_offset = (i + 1) * 2
            shadow_alpha = 80 - i * 15
            shadow_surface = pygame.Surface((width + shadow_offset * 2, height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (shadow_offset, shadow_offset, width, height), border_radius=20)
            self.screen.blit(shadow_surface, (x - shadow_offset, y - shadow_offset))
        
        # Main section with gradient
        section_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(height):
            ratio = i / height
            r = int(color[0] * (1 - ratio * 0.1))
            g = int(color[1] * (1 - ratio * 0.1))
            b = int(color[2] * (1 - ratio * 0.1))
            pygame.draw.line(section_surface, (r, g, b), (0, i), (width, i))
        
        # Glowing border
        glow_intensity = int(80 + 40 * math.sin(self.glow_timer * 3))
        border_color = (100, 150, 255, glow_intensity) if is_audio else (100, 255, 150, glow_intensity)
        pygame.draw.rect(section_surface, border_color[:3], (0, 0, width, height), 4, border_radius=20)
        self.screen.blit(section_surface, (x, y))
        
        # Animated title with glow
        title_glow_colors = [(150, 200, 255, 40), (200, 230, 255, 25)] if is_audio else [(150, 255, 200, 40), (200, 255, 230, 25)]
        for i, glow_color in enumerate(title_glow_colors):
            offset = (i + 1) * 2
            glow_surface = self.font_large.render(title, True, glow_color[:3])
            glow_rect = glow_surface.get_rect(center=(x + width // 2 + offset, y + 25 + offset))
            self.screen.blit(glow_surface, glow_rect)
        
        # Main title
        title_surface = self.font_large.render(title, True, DARK_BLUE)
        title_rect = title_surface.get_rect(center=(x + width // 2, y + 25))
        self.screen.blit(title_surface, title_rect)
    
    def draw_enhanced_toggle_button(self, text, x, y, width, height, color, text_color, hover, is_enabled):
        """Draw enhanced toggle button with animations and state indicators"""
        # Enhanced hover effect with glow
        if hover:
            # Pulsing glow effect
            glow_intensity = int(120 + 60 * math.sin(self.pulse_timer * 4))
            glow_surface = pygame.Surface((width + 30, height + 30), pygame.SRCALPHA)
            glow_color = (*GOLD[:3], glow_intensity)
            pygame.draw.rect(glow_surface, glow_color, (15, 15, width, height), border_radius=15)
            self.screen.blit(glow_surface, (x - 15, y - 15))
            
            # Brighten color
            color = tuple(min(255, c + 50) for c in color)
        
        # Multiple shadow layers for depth
        for i in range(3):
            shadow_offset = (i + 1) * 2
            shadow_alpha = 100 - i * 25
            shadow_surface = pygame.Surface((width + shadow_offset * 2, height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (shadow_offset, shadow_offset, width, height), border_radius=15)
            self.screen.blit(shadow_surface, (x - shadow_offset, y - shadow_offset))
        
        # Main button with gradient and state animation
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Animated gradient based on state
        if is_enabled:
            # Pulsing effect for enabled state
            pulse = math.sin(self.pulse_timer * 2) * 0.1
            for i in range(height):
                ratio = i / height
                r = max(0, min(255, int(color[0] * (1 - ratio * 0.2 + pulse))))
                g = max(0, min(255, int(color[1] * (1 - ratio * 0.2 + pulse))))
                b = max(0, min(255, int(color[2] * (1 - ratio * 0.2 + pulse))))
                pygame.draw.line(button_surface, (r, g, b), (0, i), (width, i))
        else:
            # Static gradient for disabled state
            for i in range(height):
                ratio = i / height
                r = max(0, min(255, int(color[0] * (1 - ratio * 0.3))))
                g = max(0, min(255, int(color[1] * (1 - ratio * 0.3))))
                b = max(0, min(255, int(color[2] * (1 - ratio * 0.3))))
                pygame.draw.line(button_surface, (r, g, b), (0, i), (width, i))
        
        # Enhanced border with state indication
        border_color = GOLD if is_enabled else GRAY
        if hover:
            border_width = 4
        else:
            border_width = 2
        pygame.draw.rect(button_surface, border_color, (0, 0, width, height), border_width, border_radius=15)
        self.screen.blit(button_surface, (x, y))
        
        # State indicator icon
        state_icon = "✅" if is_enabled else "❌"
        icon_surface = self.font_medium.render(state_icon, True, WHITE)
        icon_rect = icon_surface.get_rect(center=(x + 25, y + height // 2))
        self.screen.blit(icon_surface, icon_rect)
        
        # Text with enhanced styling and shadow
        text_shadow = self.font_medium.render(text, True, (0, 0, 0))
        text_shadow_rect = text_shadow.get_rect(center=(x + width // 2 + 2, y + height // 2 + 2))
        self.screen.blit(text_shadow, text_shadow_rect)
        
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_settings_decorations(self, card_x, card_y, card_width, card_height):
        """Draw decorative elements around the settings card"""
        # Floating settings icons
        settings_icons = ["⚙️", "🔧", "🎛️", "🎚️", "🔊", "🎨", "💡", "🎮"]
        
        for i, icon in enumerate(settings_icons):
            # Circular motion around the card
            angle = (self.glow_timer * 50 + i * 45) % 360
            radius = 150 + 30 * math.sin(self.pulse_timer + i)
            
            center_x = card_x + card_width // 2
            center_y = card_y + card_height // 2
            
            icon_x = center_x + radius * math.cos(math.radians(angle))
            icon_y = center_y + radius * math.sin(math.radians(angle))
            
            # Ensure icons stay within screen bounds
            if 50 <= icon_x <= SCREEN_WIDTH - 50 and 50 <= icon_y <= SCREEN_HEIGHT - 50:
                # Pulsing scale
                scale = 1.0 + 0.3 * math.sin(self.pulse_timer * 3 + i)
                alpha = int(150 + 100 * math.sin(self.glow_timer + i))
                
                icon_surface = self.font_large.render(icon, True, (255, 255, 255, alpha))
                scaled_surface = pygame.transform.scale(icon_surface, 
                    (int(icon_surface.get_width() * scale), 
                     int(icon_surface.get_height() * scale)))
                
                icon_rect = scaled_surface.get_rect(center=(icon_x, icon_y))
                self.screen.blit(scaled_surface, icon_rect)
        
        # Corner accent decorations
        corner_decorations = ["🎯", "⭐", "💎", "🏆"]
        corner_positions = [
            (card_x - 40, card_y - 40),  # Top left
            (card_x + card_width + 20, card_y - 40),  # Top right
            (card_x - 40, card_y + card_height + 20),  # Bottom left
            (card_x + card_width + 20, card_y + card_height + 20)  # Bottom right
        ]
        
        for i, (decoration, pos) in enumerate(zip(corner_decorations, corner_positions)):
            # Rotating and scaling animation
            angle = self.glow_timer * 40 + i * 90
            scale = 1.0 + 0.4 * math.sin(self.pulse_timer * 2 + i)
            
            decoration_surface = self.font_title.render(decoration, True, GOLD)
            scaled_surface = pygame.transform.scale(decoration_surface, 
                (int(decoration_surface.get_width() * scale), 
                 int(decoration_surface.get_height() * scale)))
            rotated_surface = pygame.transform.rotate(scaled_surface, angle)
            
            rect = rotated_surface.get_rect(center=pos)
            self.screen.blit(rotated_surface, rect)
    
    def draw_level_select(self):
        """Draw the enhanced level selection screen"""
        # Enhanced animated background
        self.draw_animated_background()
        
        # Main content card with enhanced styling
        card_width = 1100
        card_height = 750
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2
        
        # Enhanced card with glow and multiple layers
        self.draw_enhanced_card(card_x, card_y, card_width, card_height)
        
        # Animated title with glow effect
        title_text = "🎯 CHOOSE YOUR CHALLENGE"
        self.draw_glowing_title(title_text, card_x + card_width // 2, card_y + 70)
        
        # Progress indicator
        progress_text = f"🏆 Total Score: {self.total_score} | 🔓 Unlocked: {self.max_unlocked_level}/5"
        progress_x = card_x + (card_width - self.font_medium.size(progress_text)[0]) // 2
        self.draw_text(progress_text, self.font_medium, GOLD, progress_x, card_y + 120)
        
        mouse_pos = pygame.mouse.get_pos()
        buttons = {}
        
        # Enhanced level cards with animations
        levels_per_row = 3
        card_width_level = 280
        card_height_level = 180
        card_spacing = 40
        start_x = card_x + (card_width - (levels_per_row * card_width_level + (levels_per_row - 1) * card_spacing)) // 2
        start_y = card_y + 180
        
        for level_num, level_data in LEVELS.items():
            row = (level_num - 1) // levels_per_row
            col = (level_num - 1) % levels_per_row
            
            level_x = start_x + col * (card_width_level + card_spacing)
            level_y = start_y + row * (card_height_level + card_spacing + 30)
            
            # Check if level is unlocked
            is_unlocked = self.total_score >= level_data['unlock_score']
            is_current_max = level_num <= self.max_unlocked_level
            can_play = is_unlocked and is_current_max
            
            level_rect = pygame.Rect(level_x, level_y, card_width_level, card_height_level)
            level_hover = level_rect.collidepoint(mouse_pos) and can_play
            
            # Draw enhanced level card
            self.draw_enhanced_level_card(level_x, level_y, card_width_level, card_height_level, 
                                        level_num, level_data, can_play, level_hover)
            
            if can_play:
                buttons[f'level_{level_num}'] = level_rect
        
        # Enhanced back button with glow
        back_button_y = card_y + card_height - 80
        back_button_x = card_x + 50
        back_rect = pygame.Rect(back_button_x, back_button_y, 180, 60)
        back_hover = back_rect.collidepoint(mouse_pos)
        buttons['back'] = self.draw_enhanced_button("⬅️ Back to Menu", back_button_x, back_button_y, 
                                                   180, 60, ORANGE, WHITE, back_hover)
        
        return buttons
    
    def draw_enhanced_level_card(self, x, y, width, height, level_num, level_data, can_play, is_hover):
        """Draw an enhanced level card with animations and effects"""
        # Animation offset for floating effect
        float_offset = math.sin(self.glow_timer * 2 + level_num) * 3
        card_y = y + float_offset
        
        # Card colors and effects based on state
        if can_play:
            if is_hover:
                # Hover effect with glow
                glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
                glow_color = (*GOLD[:3], 100)
                pygame.draw.rect(glow_surface, glow_color, (10, 10, width, height), border_radius=15)
                self.screen.blit(glow_surface, (x - 10, card_y - 10))
                
                card_color = LIGHT_GREEN
                border_color = GOLD
                text_color = DARK_BLUE
                scale_factor = 1.05
            else:
                card_color = LIGHT_GREEN
                border_color = GREEN
                text_color = DARK_BLUE
                scale_factor = 1.0
        else:
            card_color = LIGHT_GRAY
            border_color = GRAY
            text_color = GRAY
            scale_factor = 1.0
        
        # Apply scaling for hover effect
        if scale_factor != 1.0:
            scaled_width = int(width * scale_factor)
            scaled_height = int(height * scale_factor)
            scaled_x = x - (scaled_width - width) // 2
            scaled_y = card_y - (scaled_height - height) // 2
        else:
            scaled_width, scaled_height = width, height
            scaled_x, scaled_y = x, card_y
        
        # Multiple shadow layers for depth
        for i in range(3):
            shadow_offset = (i + 1) * 2
            shadow_alpha = 80 - i * 20
            shadow_surface = pygame.Surface((scaled_width + shadow_offset * 2, scaled_height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (shadow_offset, shadow_offset, scaled_width, scaled_height), border_radius=15)
            self.screen.blit(shadow_surface, (scaled_x - shadow_offset, scaled_y - shadow_offset))
        
        # Main card with gradient
        card_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        for i in range(scaled_height):
            ratio = i / scaled_height
            r = int(card_color[0] * (1 - ratio * 0.1))
            g = int(card_color[1] * (1 - ratio * 0.1))
            b = int(card_color[2] * (1 - ratio * 0.1))
            pygame.draw.line(card_surface, (r, g, b), (0, i), (scaled_width, i))
        
        pygame.draw.rect(card_surface, border_color, (0, 0, scaled_width, scaled_height), 3, border_radius=15)
        self.screen.blit(card_surface, (scaled_x, scaled_y))
        
        # Level content with enhanced styling
        content_y_offset = 0 if scale_factor == 1.0 else -5
        
        # Large animated icon
        icon_scale = 1.0 + 0.1 * math.sin(self.pulse_timer * 2 + level_num * 0.5)
        icon_surface = self.font_title.render(level_data['icon'], True, text_color)
        scaled_icon = pygame.transform.scale(icon_surface, 
            (int(icon_surface.get_width() * icon_scale), 
             int(icon_surface.get_height() * icon_scale)))
        icon_rect = scaled_icon.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 40 + content_y_offset))
        self.screen.blit(scaled_icon, icon_rect)
        
        # Level number with glow
        level_text = f"LEVEL {level_num}"
        if can_play and is_hover:
            # Glow effect for level number
            glow_surface = self.font_large.render(level_text, True, GOLD)
            glow_rect = glow_surface.get_rect(center=(scaled_x + scaled_width // 2 + 2, scaled_y + 85 + content_y_offset + 2))
            self.screen.blit(glow_surface, glow_rect)
        
        level_surface = self.font_large.render(level_text, True, text_color)
        level_rect = level_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 85 + content_y_offset))
        self.screen.blit(level_surface, level_rect)
        
        # Level name with enhanced font
        name_surface = self.font_medium.render(level_data['name'], True, text_color)
        name_rect = name_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 115 + content_y_offset))
        self.screen.blit(name_surface, name_rect)
        
        # Difficulty indicator with color coding
        difficulty_colors = {
            'easy': GREEN,
            'medium': ORANGE,
            'hard': RED
        }
        difficulty_color = difficulty_colors.get(level_data['difficulty'], text_color)
        
        info_text = f"{level_data['questions']} Questions • {level_data['difficulty'].upper()}"
        info_surface = self.font_small.render(info_text, True, difficulty_color)
        info_rect = info_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 140 + content_y_offset))
        self.screen.blit(info_surface, info_rect)
        
        # Lock indicator or unlock requirement
        if not can_play:
            # Lock icon
            lock_surface = self.font_large.render("🔒", True, RED)
            lock_rect = lock_surface.get_rect(center=(scaled_x + scaled_width - 25, scaled_y + 25))
            self.screen.blit(lock_surface, lock_rect)
            
            # Requirement text
            req_text = f"Need {level_data['unlock_score']} pts"
            req_surface = self.font_small.render(req_text, True, RED)
            req_rect = req_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 160 + content_y_offset))
            self.screen.blit(req_surface, req_rect)
        else:
            # Success checkmark for unlocked levels
            check_surface = self.font_medium.render("✅", True, GREEN)
            check_rect = check_surface.get_rect(center=(scaled_x + scaled_width - 25, scaled_y + 25))
            self.screen.blit(check_surface, check_rect)
    
    def draw_enhanced_button(self, text, x, y, width, height, color, text_color, hover=False):
        """Draw enhanced button with better styling"""
        # Enhanced hover effect
        if hover:
            # Glow effect
            glow_surface = pygame.Surface((width + 30, height + 30), pygame.SRCALPHA)
            glow_color = (*color[:3], 120)
            pygame.draw.rect(glow_surface, glow_color, (15, 15, width, height), border_radius=15)
            self.screen.blit(glow_surface, (x - 15, y - 15))
            
            # Brighten color
            color = tuple(min(255, c + 40) for c in color)
        
        # Multiple shadow layers
        for i in range(4):
            shadow_offset = (i + 1) * 2
            shadow_alpha = 100 - i * 20
            shadow_surface = pygame.Surface((width + shadow_offset * 2, height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           (shadow_offset, shadow_offset, width, height), border_radius=15)
            self.screen.blit(shadow_surface, (x - shadow_offset, y - shadow_offset))
        
        # Main button with gradient
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(height):
            ratio = i / height
            r = int(color[0] * (1 - ratio * 0.2))
            g = int(color[1] * (1 - ratio * 0.2))
            b = int(color[2] * (1 - ratio * 0.2))
            pygame.draw.line(button_surface, (r, g, b), (0, i), (width, i))
        
        # Border
        border_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.rect(button_surface, border_color, (0, 0, width, height), 3, border_radius=15)
        self.screen.blit(button_surface, (x, y))
        
        # Text with shadow
        text_shadow = self.font_medium.render(text, True, (0, 0, 0))
        text_shadow_rect = text_shadow.get_rect(center=(x + width // 2 + 2, y + height // 2 + 2))
        self.screen.blit(text_shadow, text_shadow_rect)
        
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_quiz(self):
        """Draw the quiz screen"""
        if not self.level_questions or self.current_question_index >= len(self.level_questions):
            return {}
        
        # Gradient background
        self.draw_gradient_background()
        
        # Back to Menu button (top left)
        mouse_pos = pygame.mouse.get_pos()
        back_button_x = 20
        back_button_y = 20
        back_rect = pygame.Rect(back_button_x, back_button_y, 120, 40)
        back_hover = back_rect.collidepoint(mouse_pos)
        
        # Lives display
        self.draw_lives_display()
        
        # Progress bar
        progress = (self.current_question_index + 1) / self.total_questions
        self.draw_progress_bar(300, 50, 600, 20, progress)
        
        # Progress text
        progress_text = f"Question {self.current_question_index + 1} of {self.total_questions}"
        progress_x = 300 + (600 - self.font_small.size(progress_text)[0]) // 2
        self.draw_text(progress_text, self.font_small, WHITE, progress_x, 25)
        
        # Score display
        score_text = f"Score: {self.score}"
        self.draw_text(score_text, self.font_medium, WHITE, SCREEN_WIDTH - 200, 50)
        
        # Question card
        question_card_width = 1000
        question_card_height = 600
        question_card_x = (SCREEN_WIDTH - question_card_width) // 2
        question_card_y = 120
        
        self.draw_card(question_card_x, question_card_y, question_card_width, question_card_height, WHITE)
        
        current_question = self.level_questions[self.current_question_index]
        
        # Question text
        question_text = current_question['question']
        question_y = question_card_y + 40
        self.draw_text(question_text, self.font_large, DARK_BLUE, question_card_x + 50, question_y, 
                      max_width=question_card_width - 100)
        
        # Answer buttons
        buttons = {}
        
        answer_start_y = question_card_y + 200
        answer_height = 60
        answer_spacing = 20
        answer_width = question_card_width - 100
        
        for i, answer in enumerate(current_question['options']):
            answer_y = answer_start_y + i * (answer_height + answer_spacing)
            answer_x = question_card_x + 50
            
            # Answer button color
            if self.show_feedback:
                if i == current_question['correct_answer']:
                    answer_color = GREEN
                elif i == self.selected_answer and i != current_question['correct_answer']:
                    answer_color = RED
                else:
                    answer_color = LIGHT_GRAY
            else:
                answer_color = LIGHT_BLUE if i == self.selected_answer else LIGHT_GRAY
            
            answer_rect = pygame.Rect(answer_x, answer_y, answer_width, answer_height)
            answer_hover = answer_rect.collidepoint(mouse_pos) and not self.show_feedback
            
            # Draw answer button
            if answer_hover:
                answer_color = tuple(min(255, c + 20) for c in answer_color)
            
            pygame.draw.rect(self.screen, answer_color, answer_rect, border_radius=10)
            
            # Answer text with letter prefix
            answer_letter = chr(65 + i)  # A, B, C, D
            answer_text = f"{answer_letter}. {answer}"
            text_x = answer_x + 20
            text_y = answer_y + (answer_height - self.font_medium.get_height()) // 2
            self.draw_text(answer_text, self.font_medium, DARK_BLUE, text_x, text_y, 
                          max_width=answer_width - 40)
            
            if not self.show_feedback:
                buttons[f'answer_{i}'] = answer_rect
        
        # Back to Menu button
        buttons['back_to_menu'] = self.draw_button("⬅️ Menu", back_button_x, back_button_y, 
                                                  120, 40, RED, WHITE, back_hover)
        
        # Pause button
        pause_button_x = SCREEN_WIDTH - 100
        pause_button_y = 120
        pause_rect = pygame.Rect(pause_button_x, pause_button_y, 80, 40)
        pause_hover = pause_rect.collidepoint(mouse_pos)
        buttons['pause'] = self.draw_button("⏸️ Pause", pause_button_x, pause_button_y, 
                                           80, 40, ORANGE, WHITE, pause_hover)
        
        # Next button (only show during feedback)
        if self.show_feedback:
            next_button_x = question_card_x + question_card_width - 150
            next_button_y = question_card_y + question_card_height - 60
            next_rect = pygame.Rect(next_button_x, next_button_y, 120, 40)
            next_hover = next_rect.collidepoint(mouse_pos)
            buttons['next'] = self.draw_button("Next ➡️", next_button_x, next_button_y, 
                                              120, 40, BLUE, WHITE, next_hover)
        
        return buttons
    
    def draw_results(self):
        """Draw the results screen"""
        # Gradient background
        self.draw_gradient_background()
        
        # Results card
        card_width = 800
        card_height = 600
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2
        
        self.draw_card(card_x, card_y, card_width, card_height, WHITE, shadow=True)
        
        # Title
        title_text = "🏆 Level Complete!"
        title_x = card_x + (card_width - self.font_title.size(title_text)[0]) // 2
        self.draw_text(title_text, self.font_title, DARK_BLUE, title_x, card_y + 40)
        
        # Score display
        score_text = f"Your Score: {self.score}/{self.total_questions * 10}"
        score_x = card_x + (card_width - self.font_large.size(score_text)[0]) // 2
        self.draw_text(score_text, self.font_large, GREEN, score_x, card_y + 120)
        
        # Performance message
        percentage = (self.score / (self.total_questions * 10)) * 100
        if percentage >= 80:
            message = "🌟 Excellent! You're a first aid expert!"
            message_color = GREEN
        elif percentage >= 60:
            message = "👍 Good job! Keep practicing!"
            message_color = BLUE
        else:
            message = "📚 Keep studying and try again!"
            message_color = ORANGE
        
        message_x = card_x + (card_width - self.font_medium.size(message)[0]) // 2
        self.draw_text(message, self.font_medium, message_color, message_x, card_y + 180)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        buttons = {}
        
        button_y = card_y + 300
        button_width = 200
        button_height = 60
        button_spacing = 50
        
        # Try Again button
        try_again_x = card_x + (card_width - (button_width * 2 + button_spacing)) // 2
        try_again_rect = pygame.Rect(try_again_x, button_y, button_width, button_height)
        try_again_hover = try_again_rect.collidepoint(mouse_pos)
        buttons['try_again'] = self.draw_button("🔄 Try Again", try_again_x, button_y, 
                                               button_width, button_height, BLUE, WHITE, try_again_hover)
        
        # Menu button
        menu_x = try_again_x + button_width + button_spacing
        menu_rect = pygame.Rect(menu_x, button_y, button_width, button_height)
        menu_hover = menu_rect.collidepoint(mouse_pos)
        buttons['menu'] = self.draw_button("🏠 Main Menu", menu_x, button_y, 
                                          button_width, button_height, GREEN, WHITE, menu_hover)
        
        return buttons
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.MENU:
                        return False
                    elif self.state == GameState.QUIZ:
                        self.previous_state = self.state
                        self.state = GameState.PAUSE
                    elif self.state == GameState.PAUSE:
                        self.state = self.previous_state
                    else:
                        self.state = GameState.MENU
                
                # Answer selection with keyboard
                elif self.state == GameState.QUIZ and not self.show_feedback:
                    if event.key == pygame.K_a:
                        self.selected_answer = 0
                    elif event.key == pygame.K_b:
                        self.selected_answer = 1
                    elif event.key == pygame.K_c:
                        self.selected_answer = 2
                    elif event.key == pygame.K_d:
                        self.selected_answer = 3
                    elif event.key == pygame.K_RETURN and self.selected_answer != -1:
                        self.check_answer()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.play_sound('click')
                    self.handle_mouse_click()
        
        return True
    
    def handle_mouse_click(self):
        """Handle mouse clicks based on current state"""
        if self.state == GameState.MENU:
            buttons = self.draw_menu()
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name == 'level_select':
                        self.state = GameState.LEVEL_SELECT
                    elif button_name == 'quick_play':
                        self.current_level = 1
                        self.prepare_level_questions(1)
                        self.reset_quiz_state()
                        self.state = GameState.QUIZ
                    elif button_name == 'settings':
                        self.state = GameState.SETTINGS
                    elif button_name == 'exit':
                        pygame.quit()
                        sys.exit()
        
        elif self.state == GameState.SETTINGS:
            buttons = self.draw_settings()
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name == 'sound_toggle':
                        self.settings['sound_enabled'] = not self.settings['sound_enabled']
                    elif button_name == 'music_toggle':
                        self.settings['music_enabled'] = not self.settings['music_enabled']
                    elif button_name == 'anim_toggle':
                        self.settings['show_animations'] = not self.settings['show_animations']
                    elif button_name == 'hints_toggle':
                        self.settings['difficulty_hints'] = not self.settings['difficulty_hints']
                    elif button_name == 'back' or button_name == 'back_to_menu':
                        self.save_progress()
                        self.state = GameState.MENU
        
        elif self.state == GameState.LEVEL_SELECT:
            buttons = self.draw_level_select()
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name.startswith('level_'):
                        level_num = int(button_name.split('_')[1])
                        self.current_level = level_num
                        self.prepare_level_questions(level_num)
                        self.reset_quiz_state()
                        self.state = GameState.QUIZ
                    elif button_name == 'back':
                        self.state = GameState.MENU
        
        elif self.state == GameState.QUIZ:
            buttons = self.draw_quiz()
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name.startswith('answer_') and not self.show_feedback:
                        answer_index = int(button_name.split('_')[1])
                        self.selected_answer = answer_index
                        self.check_answer()
                    elif button_name == 'next' and self.show_feedback:
                        self.next_question()
                    elif button_name == 'pause':
                        self.previous_state = self.state
                        self.state = GameState.PAUSE
                    elif button_name == 'back_to_menu':
                        self.state = GameState.MENU
        
        elif self.state == GameState.RESULTS:
            buttons = self.draw_results()
            mouse_pos = pygame.mouse.get_pos()
            
            for button_name, button_rect in buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    if button_name == 'try_again':
                        self.prepare_level_questions(self.current_level)
                        self.reset_quiz_state()
                        self.state = GameState.QUIZ
                    elif button_name == 'menu':
                        self.state = GameState.MENU
    
    def check_answer(self):
        """Check if the selected answer is correct"""
        if self.selected_answer == -1:
            return
        
        current_question = self.level_questions[self.current_question_index]
        correct_answer = current_question['correct_answer']
        
        if self.selected_answer == correct_answer:
            self.score += 10
            self.user_answers.append(True)
            self.play_sound('correct')
            # Create success particles
            if self.settings['show_animations']:
                self.create_success_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.lives -= 1
            self.user_answers.append(False)
            self.play_sound('wrong')
            # Create error particles
            if self.settings['show_animations']:
                self.create_error_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.show_feedback = True
    
    def next_question(self):
        """Move to the next question or show results"""
        self.current_question_index += 1
        self.selected_answer = -1
        self.show_feedback = False
        
        if self.current_question_index >= len(self.level_questions) or self.lives <= 0:
            self.end_level()
        
    def end_level(self):
        """End the current level and show results"""
        self.total_score += self.score
        
        # Check if level is completed successfully
        if self.lives > 0:
            # Unlock next level
            if self.current_level == self.max_unlocked_level and self.current_level < 5:
                self.max_unlocked_level += 1
        
        self.save_progress()
        self.state = GameState.RESULTS
    
    def reset_quiz_state(self):
        """Reset quiz state for a new game"""
        self.current_question_index = 0
        self.score = 0
        self.selected_answer = -1
        self.show_feedback = False
        self.user_answers = []
        self.lives = 3
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Update animation timers
            self.glow_timer += 0.1
            self.pulse_timer += 0.1
            
            # Update particle system
            if self.settings['show_animations']:
                self.update_particles()
            
            # Handle events
            running = self.handle_events()
            
            # Draw current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.SETTINGS:
                self.draw_settings()
            elif self.state == GameState.LEVEL_SELECT:
                self.draw_level_select()
            elif self.state == GameState.QUIZ:
                self.draw_quiz()
            elif self.state == GameState.RESULTS:
                self.draw_results()
            elif self.state == GameState.PAUSE:
                # Draw pause overlay
                self.draw_gradient_background()
                pause_text = "⏸️ PAUSED"
                pause_x = (SCREEN_WIDTH - self.font_title.size(pause_text)[0]) // 2
                pause_y = SCREEN_HEIGHT // 2 - 50
                self.draw_text(pause_text, self.font_title, WHITE, pause_x, pause_y)
                
                resume_text = "Press ESC to resume"
                resume_x = (SCREEN_WIDTH - self.font_medium.size(resume_text)[0]) // 2
                resume_y = pause_y + 100
                self.draw_text(resume_text, self.font_medium, LIGHT_GRAY, resume_x, resume_y)
            
            # Draw particles
            if self.settings['show_animations']:
                self.draw_particles()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FirstAidQuizGame()
    game.run()
