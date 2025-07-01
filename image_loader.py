"""
Image Asset Loader for First Aid Quiz Game
This module handles loading and managing all visual assets for the game.
"""

import pygame
import os
from typing import Dict, Optional

class ImageAssetManager:
    """Manages loading and caching of all game images"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.asset_paths = {
            # Backgrounds
            'main_menu_bg': 'assets/backgrounds/main_menu_bg.png',
            'quiz_bg': 'assets/backgrounds/quiz_bg.png',
            'settings_bg': 'assets/backgrounds/settings_bg.png',
            'level_select_bg': 'assets/backgrounds/level_select_bg.png',
            'results_bg': 'assets/backgrounds/results_bg.png',
            
            # Characters
            'doctor_mascot': 'assets/characters/doctor_mascot.png',
            'nurse_character': 'assets/characters/nurse_character.png',
            'paramedic_character': 'assets/characters/paramedic_character.png',
            'patient_character': 'assets/characters/patient_character.png',
            'success_character': 'assets/characters/success_character.png',
            
            # Icons
            'medical_cross': 'assets/icons/medical_cross.png',
            'heart_icon': 'assets/icons/heart_icon.png',
            'star_icon': 'assets/icons/star_icon.png',
            'settings_icon': 'assets/icons/settings_icon.png',
            'play_icon': 'assets/icons/play_icon.png',
            'pause_icon': 'assets/icons/pause_icon.png',
            'back_icon': 'assets/icons/back_icon.png',
            'lock_icon': 'assets/icons/lock_icon.png',
            'trophy_icon': 'assets/icons/trophy_icon.png',
            'first_aid_kit': 'assets/icons/first_aid_kit.png',
            
            # Level Images
            'basic_first_aid': 'assets/images/basic_first_aid.png',
            'emergency_response': 'assets/images/emergency_response.png',
            'cpr_training': 'assets/images/cpr_training.png',
            'advanced_equipment': 'assets/images/advanced_equipment.png',
            'expert_badge': 'assets/images/expert_badge.png',
            
            # UI Elements
            'progress_fill': 'assets/images/progress_fill.png',
            'button_glow': 'assets/images/button_glow.png',
            'card_shadow': 'assets/images/card_shadow.png',
            'success_particle': 'assets/images/success_particle.png',
            'error_particle': 'assets/images/error_particle.png',
        }
    
    def load_image(self, image_name: str, scale: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """
        Load an image by name, with optional scaling
        
        Args:
            image_name: Name of the image to load
            scale: Optional tuple (width, height) to scale the image
            
        Returns:
            pygame.Surface or None if image not found
        """
        # Check if already loaded
        cache_key = f"{image_name}_{scale}" if scale else image_name
        if cache_key in self.images:
            return self.images[cache_key]
        
        # Get file path
        if image_name not in self.asset_paths:
            print(f"Warning: Image '{image_name}' not found in asset paths")
            return None
        
        file_path = self.asset_paths[image_name]
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: Image file not found: {file_path}")
            return None
        
        try:
            # Load image
            image = pygame.image.load(file_path).convert_alpha()
            
            # Scale if requested
            if scale:
                image = pygame.transform.scale(image, scale)
            
            # Cache the image
            self.images[cache_key] = image
            return image
            
        except pygame.error as e:
            print(f"Error loading image {file_path}: {e}")
            return None
    
    def load_all_images(self):
        """Preload all images for better performance"""
        print("Loading all game assets...")
        loaded_count = 0
        total_count = len(self.asset_paths)
        
        for image_name in self.asset_paths:
            if self.load_image(image_name):
                loaded_count += 1
        
        print(f"Loaded {loaded_count}/{total_count} images successfully")
    
    def get_image(self, image_name: str, scale: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """Get an image, loading it if not already cached"""
        return self.load_image(image_name, scale)
    
    def create_fallback_image(self, size: tuple, color: tuple = (200, 200, 200)) -> pygame.Surface:
        """Create a fallback image when assets are missing"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface

# Enhanced drawing functions that use images
def draw_background_image(screen, asset_manager, bg_name: str, fallback_gradient=None):
    """Draw background image or fallback to gradient"""
    bg_image = asset_manager.get_image(bg_name, (1200, 800))
    
    if bg_image:
        screen.blit(bg_image, (0, 0))
    elif fallback_gradient:
        # Draw gradient fallback
        start_color, end_color = fallback_gradient
        for y in range(800):
            ratio = y / 800
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (1200, y))

def draw_character(screen, asset_manager, character_name: str, x: int, y: int, scale: Optional[tuple] = None):
    """Draw a character image at specified position"""
    character_image = asset_manager.get_image(character_name, scale)
    
    if character_image:
        # Center the character at the given position
        rect = character_image.get_rect()
        rect.center = (x, y)
        screen.blit(character_image, rect)
        return rect
    return None

def draw_icon_button(screen, asset_manager, icon_name: str, x: int, y: int, 
                    button_size: tuple, icon_scale: Optional[tuple] = None):
    """Draw a button with an icon"""
    # Draw button background (you can customize this)
    button_rect = pygame.Rect(x, y, button_size[0], button_size[1])
    pygame.draw.rect(screen, (100, 150, 200), button_rect, border_radius=10)
    
    # Draw icon
    icon_image = asset_manager.get_image(icon_name, icon_scale)
    if icon_image:
        icon_rect = icon_image.get_rect()
        icon_rect.center = button_rect.center
        screen.blit(icon_image, icon_rect)
    
    return button_rect

def draw_level_card_with_image(screen, asset_manager, level_data: dict, x: int, y: int, 
                              width: int, height: int, is_unlocked: bool):
    """Draw a level selection card with associated image"""
    # Draw card background
    card_color = (200, 255, 200) if is_unlocked else (200, 200, 200)
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, card_color, card_rect, border_radius=15)
    
    # Draw level-specific image
    level_images = {
        1: 'basic_first_aid',
        2: 'emergency_response', 
        3: 'advanced_equipment',
        4: 'cpr_training',
        5: 'expert_badge'
    }
    
    level_num = level_data.get('level', 1)
    if level_num in level_images:
        image_name = level_images[level_num]
        level_image = asset_manager.get_image(image_name, (width-20, height//2))
        if level_image:
            image_rect = level_image.get_rect()
            image_rect.centerx = card_rect.centerx
            image_rect.y = y + 10
            screen.blit(level_image, image_rect)
    
    return card_rect

# Example integration function
def integrate_assets_into_game(game_instance):
    """
    Example function showing how to integrate the asset manager into your game
    Call this in your game's __init__ method
    """
    # Add asset manager to game
    game_instance.asset_manager = ImageAssetManager()
    
    # Load all images at startup
    game_instance.asset_manager.load_all_images()
    
    print("Asset manager integrated successfully!")

# Usage example for your main game file:
"""
# In your FirstAidQuizGame.__init__ method, add:
from image_loader import ImageAssetManager, integrate_assets_into_game

# Initialize asset manager
self.asset_manager = ImageAssetManager()
self.asset_manager.load_all_images()

# In your drawing methods, use:
from image_loader import draw_background_image, draw_character, draw_icon_button

# Example in draw_menu method:
draw_background_image(self.screen, self.asset_manager, 'main_menu_bg', 
                     fallback_gradient=((52, 152, 219), (155, 89, 182)))

# Example for drawing mascot:
draw_character(self.screen, self.asset_manager, 'doctor_mascot', 
              SCREEN_WIDTH//2, 200, scale=(200, 200))
"""
