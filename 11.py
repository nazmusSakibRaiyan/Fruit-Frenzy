import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18
import random


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BASKET_WIDTH = 40
BASKET_HEIGHT = 30
MAX_MISSED_FRUITS = 20


BUTTON_SIZE = 40
BUTTON_SPACING = 10
BUTTON_Y = WINDOW_HEIGHT - 50


game_paused = False
game_over = False
score = 0
hearts = 5
missed_fruits = 0
basket_position = WINDOW_WIDTH // 2

fruits = []
bombs = []
eggs = []

class GameObject:    
    def __init__(self, x, y, radius, speed, object_type):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.type = object_type
        self.missed = False

# Button
buttons = {
    'restart': {'x': WINDOW_WIDTH - 3*BUTTON_SIZE - 2*BUTTON_SPACING, 'hover': False,  'color': (0.2, 0.7, 0.2) },

    'pause': { 'x': WINDOW_WIDTH - 2*BUTTON_SIZE - BUTTON_SPACING, 'hover': False, 'color': (0.2, 0.2, 0.7) },

    'exit': { 'x': WINDOW_WIDTH - BUTTON_SIZE,'hover': False,'color': (0.7, 0.2, 0.2) }
    
}

def midpoint_line(x1, y1, x2, y2):    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy

    glBegin(GL_POINTS)
    while True:
        glVertex2f(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    glEnd()

def fill_circle(x, y, radius):    
    glBegin(GL_POINTS)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx*dx + dy*dy <= radius*radius:
                glVertex2f(x + dx, y + dy)
    glEnd()

def draw_apple(x, y, radius):    
    glBegin(GL_POINTS)
    glColor3f(0.8, 0.1, 0.1)
    for dy in range(-radius, radius + 1):
        height_scale = 1.1  
        width = int(math.sqrt(radius*radius - (dy/height_scale)**2))
        for dx in range(-width, width + 1):
            glVertex2f(x + dx, y + dy)

    glColor3f(0.4, 0.2, 0.0)#stem
    for i in range(10):
        stem_x = x + math.sin(i/3.0) * 2
        stem_y = y + radius + i
        for dx in range(-1, 2):
            glVertex2f(stem_x + dx, stem_y)

    glColor3f(0.2, 0.8, 0.2)#leaf
    for i in range(8):
        leaf_x = x + 3 + i
        leaf_y = y + radius + math.sin(i/2.0) * 3
        for dy in range(-2, 3):
            glVertex2f(leaf_x, leaf_y + dy)    
    glEnd()

def draw_banana(x, y, radius):
    glBegin(GL_POINTS)
    glColor3f(1.0, 0.8, 0.0) 
    for t in range(60):
        angle = t * math.pi / 60  
        curve_x = x + radius * math.cos(angle)
        curve_y = y + radius * math.sin(angle) * 0.7  

        thickness = int(5 + 3 * abs(math.sin(angle)))  
        for r in range(-thickness, thickness + 1):
            px = curve_x + r * math.cos(angle + math.pi/2)
            py = curve_y + r * math.sin(angle + math.pi/2)
            glVertex2f(px, py)
    

    glColor3f(0.4, 0.2, 0.0)  # Stem
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx*dx + dy*dy <= 9:
                glVertex2f(x - radius + dx, y + dy)   
                glVertex2f(x + radius + dx, y + dy)  
    glEnd()


def draw_grape(x, y, radius):
    glBegin(GL_POINTS)

    glColor3f(0.6, 0.2, 0.8)  
    offsets = [
        (0, 0), (radius, 0), (-radius, 0),  # First row
        (-radius//2, -radius), (radius//2, -radius),  # Second row
        (0, -2*radius)  # Third row
    ]
    for ox, oy in offsets:
        for dy in range(-radius, radius + 1):
            circle_width = int(math.sqrt(radius*radius - dy**2))
            for dx in range(-circle_width, circle_width + 1):
                glVertex2f(x + ox + dx, y + oy + dy)
    
    glEnd()
    

    glBegin(GL_POINTS)
    glColor3f(0.4, 0.2, 0.0)  # Stem
    for i in range(radius * 2):
        stem_x = x
        stem_y = y + radius + i
        for dx in range(-1, 2):  
            glVertex2f(stem_x + dx, stem_y)
    glEnd()



def draw_egg(x, y, radius):
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.9)
    for dy in range(-radius, radius + 1):
        width_scale = 1.0 + 0.3 * (dy / radius)
        width = int(math.sqrt(radius*radius - dy*dy) * width_scale)
        for dx in range(-width, width + 1):
            glVertex2f(x + dx, y + dy)

    glColor3f(1.0, 1.0, 1.0)
    highlight_radius = radius // 3
    for dy in range(-highlight_radius, highlight_radius + 1):
        for dx in range(-highlight_radius, highlight_radius + 1):
            if dx*dx + dy*dy <= highlight_radius*highlight_radius:
                glVertex2f(x - radius//3 + dx, y + radius//3 + dy)    
    glEnd()

def draw_bomb(x, y, radius):
    glColor3f(0.1, 0.1, 0.1)
    fill_circle(x, y, radius)
    
    glBegin(GL_POINTS)
    glColor3f(0.6, 0.3, 0.0)
    for i in range(12):
        fuse_x = x + math.sin(i/2.0) * 2
        fuse_y = y + radius + i
        for dx in range(-1, 2):
            glVertex2f(fuse_x + dx, fuse_y)
    glColor3f(0.3, 0.3, 0.3)
    highlight_radius = radius // 3
    for dy in range(-highlight_radius, highlight_radius + 1):
        for dx in range(-highlight_radius, highlight_radius + 1):
            if dx*dx + dy*dy <= highlight_radius*highlight_radius:
                glVertex2f(x - radius//3 + dx, y + radius//3 + dy)
    glEnd()

def draw_button(x, y, button_type, hover):
    button = buttons[button_type]
    color = button['color']

    if hover:
        glColor3f(color[0] + 0.2, color[1] + 0.2, color[2] + 0.2)
    else:
        glColor3f(*color)

    fill_circle(x + BUTTON_SIZE//2, y + BUTTON_SIZE//2, BUTTON_SIZE//2)
    
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)
    

    if button_type == 'restart':
        for i in range(30):
            angle = i * math.pi / 15
            r = BUTTON_SIZE//3
            px = x + BUTTON_SIZE//2 + r * math.cos(angle)
            py = y + BUTTON_SIZE//2 + r * math.sin(angle)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    glVertex2f(px + dx, py + dy)
    elif button_type == 'pause':
        for i in range(BUTTON_SIZE//2):
            glVertex2f(x + BUTTON_SIZE//3, y + BUTTON_SIZE//3 + i)
            glVertex2f(x + 2*BUTTON_SIZE//3, y + BUTTON_SIZE//3 + i)
    elif button_type == 'exit':
        for i in range(-BUTTON_SIZE//4, BUTTON_SIZE//4):
            glVertex2f(x + BUTTON_SIZE//2 + i, y + BUTTON_SIZE//2 + i)
            glVertex2f(x + BUTTON_SIZE//2 + i, y + BUTTON_SIZE//2 - i)
    
    glEnd()

def check_button_hover(mouse_x, mouse_y):
    for button_name, button in buttons.items():
        center_x = button['x'] + BUTTON_SIZE//2
        center_y = BUTTON_Y + BUTTON_SIZE//2
        distance = math.sqrt((mouse_x - center_x)**2 + (mouse_y - center_y)**2)
        button['hover'] = distance <= BUTTON_SIZE//2

def mouse_motion(x, y):
    y = WINDOW_HEIGHT - y  
    check_button_hover(x, y)
    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global game_paused, game_over
    
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        y = WINDOW_HEIGHT - y
        for button_name, button_data in buttons.items():
            center_x = button_data['x'] + BUTTON_SIZE//2
            center_y = BUTTON_Y + BUTTON_SIZE//2
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            if distance <= BUTTON_SIZE//2:
                if button_name == 'restart':
                    reset_game()
                elif button_name == 'pause':
                    game_paused = not game_paused
                elif button_name == 'exit':
                    glutLeaveMainLoop()

def create_fruit():
    fruit_types = [
        ('apple', 1, (1.0, 0.0, 0.0)),
        ('banana', 2, (1.0, 0.8, 0.0)),
        ('grape',3, (0.6, 0.2, 0.8))
    ]
    fruit_type = random.choice(fruit_types)
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,15,
        random.uniform(1, 2),
        {'name': fruit_type[0], 'points': fruit_type[1], 'color': fruit_type[2]}
    )

def create_bomb():
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,
        12,
        random.uniform(2.5, 3.5),
        {'name': 'bomb', 'damage': 2, 'color': (0.2, 0.2, 0.2)}
    )

def create_egg():
    return GameObject(
        random.randint(30, WINDOW_WIDTH - 30),
        WINDOW_HEIGHT + 20,10, random.uniform(2.0, 3.0),
        {'name': 'egg', 'heal': 1, 'color': (1.0, 1.0, 0.9)}
    )

def draw_basket():
    glColor3f(0.8, 0.6, 0.4)
    for i in range(-BASKET_WIDTH, BASKET_WIDTH + 1, 2):
        x = basket_position + i
        y = 60 - int((-i * i) / (BASKET_WIDTH * 4))
        midpoint_line(x, y, x + 2, y)

    midpoint_line(basket_position - BASKET_WIDTH, 60,
                 basket_position - BASKET_WIDTH + 15, 30)
    midpoint_line(basket_position + BASKET_WIDTH, 60,
                 basket_position + BASKET_WIDTH - 15, 30)
    midpoint_line(basket_position - BASKET_WIDTH + 15, 30,
                 basket_position + BASKET_WIDTH - 15, 30)

def update_game_state():
    global score, hearts, missed_fruits, game_over    
    if game_paused or game_over:
        return
    
    for fruit in fruits[:]:
        fruit.y -= fruit.speed
        if fruit.y < 0:
            fruits.remove(fruit)
            missed_fruits += 1
            if missed_fruits % 3 == 0:  
                hearts -= 1
                if hearts <= 0:
                    game_over = True
        elif check_collision(fruit):
            score += fruit.type['points']
            fruits.remove(fruit)
            missed_fruits = 0 
             
    for bomb in bombs[:]:
        bomb.y -= bomb.speed
        if bomb.y < 0:
            bombs.remove(bomb)
        elif check_collision(bomb):
            hearts -= 2  # Decrease hearts by 2 for bomb collision
            bombs.remove(bomb)
            if hearts <= 0:
                game_over = True

    for egg in eggs[:]:
        egg.y -= egg.speed
        if egg.y < 0:
            eggs.remove(egg)
        elif check_collision(egg):
            hearts = min(hearts + 1, 5)  
            eggs.remove(egg)


def check_collision(obj):
    basket_left = basket_position - BASKET_WIDTH
    basket_right = basket_position + BASKET_WIDTH
    basket_top = 60
    basket_bottom = 30
    if obj.y - obj.radius <= basket_top and obj.y - obj.radius >= basket_bottom:
        if basket_left <= obj.x <= basket_right:
            return True
    return False

def spawn_objects():
    if game_paused or game_over:
        return

    fruit_chance = 0.02 + min(score / 1000, 0.03)  # Increases with score
    bomb_chance = 0.01 + min(score / 2000, 0.02)   # Increases with score
    egg_chance = 0.005                             # Remains constant
    
    if random.random() < fruit_chance:
        fruits.append(create_fruit())
    if random.random() < bomb_chance:
        bombs.append(create_bomb())
    if random.random() < egg_chance:
        eggs.append(create_egg())

def draw_hearts():
    for i in range(hearts):
        heart_x = WINDOW_WIDTH // 2 - (hearts * 15) + i * 30
        heart_y = WINDOW_HEIGHT - 30        
        glColor3f(1.0, 0.2, 0.2)
        glBegin(GL_POINTS)
        for t in range(360):
            angle = math.radians(t)
            x = 16 * math.sin(angle) ** 3
            y = 13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle)
            scale = 0.7
            glVertex2f(heart_x + x * scale, heart_y + y * scale)
        glEnd()

def draw_text(x, y, text):
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x + 1, y - 1)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT)    
    if not game_over:
        draw_basket()        
        for fruit in fruits:
            if fruit.type['name'] == 'apple':
                draw_apple(fruit.x, fruit.y, fruit.radius)
            elif fruit.type['name'] == 'banana':
                draw_banana(fruit.x, fruit.y, fruit.radius)
            elif fruit.type['name'] == 'grape':
                draw_grape(fruit.x, fruit.y, fruit.radius)
        
        for bomb in bombs:
            draw_bomb(bomb.x, bomb.y, bomb.radius)
        
        for egg in eggs:
            draw_egg(egg.x, egg.y, egg.radius)
        
        draw_hearts()
        draw_text(10, WINDOW_HEIGHT - 30,f"Score: {score}  Missed: {missed_fruits}/{MAX_MISSED_FRUITS}")

        if game_paused:
            draw_text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2, "PAUSED")
        

        for button_name, button in buttons.items():
            draw_button(button['x'], BUTTON_Y, button_name, button['hover'])
    else:
        draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 
                 f"Game Over! Final Score: {score}")
        draw_text(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 30,
                 "Click the Restart button to play again!")
        
        for button_name, button in buttons.items():
            if button_name in ['restart', 'exit']:
                draw_button(button['x'], BUTTON_Y, button_name, button['hover'])
    
    glutSwapBuffers()

def update(value):
    spawn_objects()
    update_game_state()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0) 

def keyboard(key, x, y):
    global basket_position, game_paused    
    movement_speed = 10    
    if key == b'a' and basket_position > BASKET_WIDTH:
        basket_position = max(BASKET_WIDTH, basket_position - movement_speed)
    elif key == b'd' and basket_position < WINDOW_WIDTH - BASKET_WIDTH:
        basket_position = min(WINDOW_WIDTH - BASKET_WIDTH, 
                            basket_position + movement_speed)
    elif key == b'p':
        game_paused = not game_paused
    elif key == b'q':
        glutLeaveMainLoop()

def reset_game():
    global game_paused, game_over, score, hearts, missed_fruits
    global fruits, bombs, eggs, basket_position
    
    game_paused = False
    game_over = False
    score = 0
    hearts = 5
    missed_fruits = 0
    basket_position = WINDOW_WIDTH // 2
    fruits.clear()
    bombs.clear()
    eggs.clear()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Fruit Frenzy")
glClearColor(0.0, 0.0, 0.1, 1.0)  ##Dark Blue BG
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutTimerFunc(16, update, 0)
glutPassiveMotionFunc(mouse_motion)
glutMouseFunc(mouse_click)

print("\nFruit Frenzy Controls:")
print("a/d - Move basket left/right")
print("p - Pause/Unpause game")
print("q - Quit game")
print("\nMouse Controls:")
print("- Click the circular buttons to:")
print("  * Restart game (Green)")
print("  * Pause/Play (Blue)")
print("  * Exit game (Red)")

glutMainLoop()
