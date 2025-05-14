import pygame
import sys
import math
import time
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 223, 0)
TOMATO_RED = (255, 99, 71)
UPGRADE_PANEL_WIDTH = 300

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pizza Clicker")
clock = pygame.time.Clock()

# Game variables
dough = 0
dough_per_click = 1
dough_per_second = 0
last_update_time = time.time()

# Rhythm system variables
pizza_rhythm = [
    "Mix-mix-mix the dough!",
    "Roll-roll-roll it flat!",
    "Sauce-sauce-saucy top!",
    "Cheese-cheese-cheese it up!",
    "Top-top-toppings time!",
    "Bake-bake-bake it now!",
    "Pizza-pizza-pizza time!"
]
current_rhythm = ""
rhythm_timer = 0
RHYTHM_INTERVAL = 2  # seconds between rhythm changes
rhythm_colors = [
    (255, 223, 0),    # YELLOW
    (255, 160, 0),    # ORANGE
    (255, 99, 71),    # TOMATO_RED
    (200, 50, 30),    # SAUCE RED
    (250, 230, 140),  # CHEESE
    (220, 170, 90),   # CRUST
    (50, 200, 50)     # GREEN
]
current_rhythm_color = YELLOW

# Floating text effect for clicks
class FloatingText:
    def __init__(self, x, y, text, color, font, speed=1, lifetime=1):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.speed = speed
        self.lifetime = lifetime
        self.creation_time = time.time()
    
    def update(self):
        # Move upward
        self.y -= self.speed
        
        # Calculate alpha based on remaining lifetime
        elapsed = time.time() - self.creation_time
        if elapsed > self.lifetime:
            return False  # Text should be removed
        
        return True  # Text is still active
    
    def draw(self):
        # Calculate alpha (fade out over time)
        elapsed = time.time() - self.creation_time
        alpha = 255 * (1 - (elapsed / self.lifetime))
        
        # Create a temporary surface with per-pixel alpha
        text_surface = self.font.render(self.text, True, self.color)
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, alpha))
        
        # Blit with alpha blending
        text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y))

# Font setup
small_font = pygame.font.SysFont('Arial', 14)
medium_font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 36)

# Upgrade definitions
upgrades = [
    {
        "name": "Better Flour",
        "description": "Double click value",
        "cost": 10,
        "base_cost": 10,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_click', dough_per_click * 2),
        "owned": 0,
        "color": BROWN,
        "type": "click"
    },
    {
        "name": "Pizza Oven",
        "description": "+1 dough per second",
        "cost": 15,
        "base_cost": 15,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_second', dough_per_second + 1),
        "owned": 0,
        "color": RED,
        "type": "passive"
    },
    {
        "name": "Pizza Chef",
        "description": "+5 dough per second",
        "cost": 100,
        "base_cost": 100,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_second', dough_per_second + 5),
        "owned": 0,
        "color": WHITE,
        "type": "passive"
    },
    {
        "name": "Pepperoni",
        "description": "Triple click value",
        "cost": 250,
        "base_cost": 250,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_click', dough_per_click * 3),
        "owned": 0,
        "color": TOMATO_RED,
        "type": "click"
    },
    {
        "name": "Pizzeria",
        "description": "+25 dough per second",
        "cost": 1000,
        "base_cost": 1000,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_second', dough_per_second + 25),
        "owned": 0,
        "color": GREEN,
        "type": "passive"
    },
    {
        "name": "Pizza Chain",
        "description": "+100 dough per second",
        "cost": 5000,
        "base_cost": 5000,
        "effect": lambda: setattr(sys.modules[__name__], 'dough_per_second', dough_per_second + 100),
        "owned": 0,
        "color": YELLOW,
        "type": "passive"
    }
]

# Function to draw the pizza
def draw_pizza(center_x, center_y, radius, clicked=False):
    # Pizza base (crust)
    pygame.draw.circle(screen, (220, 170, 90), (center_x, center_y), radius)
    
    # Pizza sauce (smaller circle)
    pygame.draw.circle(screen, (200, 50, 30), (center_x, center_y), radius - 10)
    
    # Pizza cheese
    pygame.draw.circle(screen, (250, 230, 140), (center_x, center_y), radius - 15)
    
    # Draw pepperoni
    for i in range(8):
        angle = i * (2 * math.pi / 8)
        pepperoni_x = center_x + (radius - 40) * math.cos(angle)
        pepperoni_y = center_y + (radius - 40) * math.sin(angle)
        pygame.draw.circle(screen, (200, 30, 30), (int(pepperoni_x), int(pepperoni_y)), 10)
    
    # Draw some olives
    for i in range(5):
        angle = i * (2 * math.pi / 5) + 0.3
        olive_x = center_x + (radius - 60) * math.cos(angle)
        olive_y = center_y + (radius - 60) * math.sin(angle)
        pygame.draw.circle(screen, (30, 30, 30), (int(olive_x), int(olive_y)), 7)
    
    # Visual feedback when clicked
    if clicked:
        # Draw a "click effect"
        pygame.draw.circle(screen, WHITE, (center_x, center_y), radius + 5, 3)

# Function to format large numbers
def format_number(number):
    if number < 1000:
        return str(int(number))
    elif number < 1000000:
        return f"{number/1000:.1f}K"
    else:
        return f"{number/1000000:.1f}M"

# Button class for upgrades
class Button:
    def __init__(self, x, y, width, height, upgrade):
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade = upgrade
        self.clicked = False
        self.hover = False
    
    def draw(self):
        # Button background
        color = self.upgrade["color"] if self.hover else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        
        # Button text
        name_text = medium_font.render(self.upgrade["name"], True, WHITE)
        desc_text = small_font.render(self.upgrade["description"], True, WHITE)
        cost_text = small_font.render(f"Cost: {format_number(self.upgrade['cost'])} dough", True, WHITE)
        owned_text = small_font.render(f"Owned: {self.upgrade['owned']}", True, WHITE)
        
        # Draw text
        screen.blit(name_text, (self.rect.x + 10, self.rect.y + 5))
        screen.blit(desc_text, (self.rect.x + 10, self.rect.y + 30))
        screen.blit(cost_text, (self.rect.x + 10, self.rect.y + 50))
        screen.blit(owned_text, (self.rect.x + 10, self.rect.y + 70))
        
        # Affordable indicator
        if dough >= self.upgrade["cost"]:
            pygame.draw.circle(screen, GREEN, (self.rect.right - 15, self.rect.y + 15), 7)
        else:
            pygame.draw.circle(screen, RED, (self.rect.right - 15, self.rect.y + 15), 7)
    
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True
            return True
        return False
    
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# Create upgrade buttons
upgrade_buttons = []
for i, upgrade in enumerate(upgrades):
    button = Button(WIDTH - UPGRADE_PANEL_WIDTH + 10, 120 + i * 100, UPGRADE_PANEL_WIDTH - 20, 90, upgrade)
    upgrade_buttons.append(button)

# Pizza click animation variables
pizza_clicked = False
click_time = 0
CLICK_DURATION = 0.1

# Floating text list
floating_texts = []

# Rhythm bonus system
rhythm_bonus_active = False
RHYTHM_BONUS_MULTIPLIER = 2
RHYTHM_BONUS_DURATION = 0.5
rhythm_bonus_time = 0

# Game loop
running = True
while running:
    current_time = time.time()
    dt = current_time - last_update_time
    
    # Add passive income
    if dt >= 0.1:  # Update every 100ms
        dough += dough_per_second * dt
        last_update_time = current_time
    
    # Manage click animation
    if pizza_clicked and current_time - click_time > CLICK_DURATION:
        pizza_clicked = False
    
    # Pizza cooking rhythm
    rhythm_timer += dt
    if rhythm_timer >= RHYTHM_INTERVAL:
        rhythm_timer = 0
        rhythm_index = random.randrange(len(pizza_rhythm))
        current_rhythm = pizza_rhythm[rhythm_index]
        current_rhythm_color = rhythm_colors[rhythm_index]
        
        # Flash the screen slightly
        rhythm_bonus_active = True
        rhythm_bonus_time = current_time
    
    # Check if rhythm bonus is still active
    if rhythm_bonus_active and current_time - rhythm_bonus_time > RHYTHM_BONUS_DURATION:
        rhythm_bonus_active = False
    
    # Update floating texts
    i = 0
    while i < len(floating_texts):
        if floating_texts[i].update():
            i += 1
        else:
            floating_texts.pop(i)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Mouse click handling
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if pizza was clicked
            pizza_center = (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2, HEIGHT // 2)
            pizza_radius = 100
            mouse_pos = pygame.mouse.get_pos()
            
            # Calculate distance from pizza center
            distance = math.sqrt((mouse_pos[0] - pizza_center[0]) ** 2 + 
                                (mouse_pos[1] - pizza_center[1]) ** 2)
            
            if distance <= pizza_radius:
                # Apply rhythm bonus if active
                click_value = dough_per_click
                if rhythm_bonus_active:
                    click_value *= RHYTHM_BONUS_MULTIPLIER
                    bonus_text = FloatingText(
                        pizza_center[0], 
                        pizza_center[1] - 30, 
                        "RHYTHM BONUS!", 
                        YELLOW, 
                        medium_font,
                        speed=2,
                        lifetime=1
                    )
                    floating_texts.append(bonus_text)
                
                dough += click_value
                pizza_clicked = True
                click_time = current_time
                
                # Create a floating text effect for click value
                click_text = FloatingText(
                    mouse_pos[0], 
                    mouse_pos[1], 
                    f"+{click_value}", 
                    WHITE, 
                    small_font
                )
                floating_texts.append(click_text)
                
                # Generate a new rhythm phrase when clicking
                if random.random() < 0.3:  # 30% chance
                    rhythm_timer = RHYTHM_INTERVAL  # Force a new rhythm
            
            # Check upgrade buttons
            for button in upgrade_buttons:
                if button.check_click(mouse_pos):
                    # Try to purchase the upgrade
                    if dough >= button.upgrade["cost"]:
                        dough -= button.upgrade["cost"]
                        button.upgrade["owned"] += 1
                        button.upgrade["effect"]()
                        
                        # Increase cost for next purchase (30% more expensive)
                        button.upgrade["cost"] = int(button.upgrade["base_cost"] * (1.3 ** button.upgrade["owned"]))
                        
                        # Create a purchase text
                        purchase_text = FloatingText(
                            button.rect.centerx,
                            button.rect.centery,
                            f"Purchased {button.upgrade['name']}!",
                            GREEN,
                            medium_font,
                            lifetime=1.5
                        )
                        floating_texts.append(purchase_text)
        
        # Mouse movement for hover effects
        if event.type == pygame.MOUSEMOTION:
            for button in upgrade_buttons:
                button.check_hover(event.pos)
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw game area background (with slight rhythm effect)
    bg_color = (50, 50, 50)
    if rhythm_bonus_active:
        # Lighten the background slightly during rhythm bonus
        bg_color = (70, 70, 70)
    pygame.draw.rect(screen, bg_color, (0, 0, WIDTH - UPGRADE_PANEL_WIDTH, HEIGHT))
    
    # Draw upgrade panel background
    pygame.draw.rect(screen, (30, 30, 30), (WIDTH - UPGRADE_PANEL_WIDTH, 0, UPGRADE_PANEL_WIDTH, HEIGHT))
    pygame.draw.line(screen, WHITE, (WIDTH - UPGRADE_PANEL_WIDTH, 0), (WIDTH - UPGRADE_PANEL_WIDTH, HEIGHT), 2)
    
    # Draw pizza
    draw_pizza(WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2, HEIGHT // 2, 100, pizza_clicked)
    
    # Draw dough counter
    dough_text = large_font.render(f"{format_number(dough)} Dough", True, WHITE)
    screen.blit(dough_text, (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2 - dough_text.get_width() // 2, 50))
    
    # Draw stats
    stats_text1 = medium_font.render(f"Per Click: {format_number(dough_per_click)}", True, WHITE)
    stats_text2 = medium_font.render(f"Per Second: {format_number(dough_per_second)}", True, WHITE)
    screen.blit(stats_text1, (20, 20))
    screen.blit(stats_text2, (20, 50))
    
    # Draw rhythm system info
    if rhythm_bonus_active:
        bonus_info = medium_font.render("RHYTHM BONUS ACTIVE!", True, YELLOW)
        screen.blit(bonus_info, (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2 - bonus_info.get_width() // 2, HEIGHT - 180))
    
    # Draw current rhythm
    if current_rhythm:
        rhythm_text = medium_font.render(current_rhythm, True, current_rhythm_color)
        screen.blit(rhythm_text, (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2 - rhythm_text.get_width() // 2, HEIGHT - 150))
    
    # Draw panel title
    panel_title = large_font.render("Upgrades", True, WHITE)
    screen.blit(panel_title, (WIDTH - UPGRADE_PANEL_WIDTH // 2 - panel_title.get_width() // 2, 20))
    
    # Draw click indicator
    click_text = medium_font.render("Click the pizza!", True, WHITE)
    screen.blit(click_text, (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2 - click_text.get_width() // 2, HEIGHT - 100))
    
    # Draw rhythm bonus info
    rhythm_info = small_font.render("Click during rhythm changes for 2x bonus!", True, YELLOW)
    screen.blit(rhythm_info, (WIDTH // 2 - UPGRADE_PANEL_WIDTH // 2 - rhythm_info.get_width() // 2, HEIGHT - 80))
    
    # Draw upgrade buttons
    for button in upgrade_buttons:
        button.draw()
    
    # Draw floating texts
    for text in floating_texts:
        text.draw()
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit the game
pygame.quit()
sys.exit()
