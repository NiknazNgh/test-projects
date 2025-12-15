import pygame
import time
import random

# --- INITIAL SETUP ---
pygame.init()

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
PURPLE = (128, 0, 128)

# Screen Dimensions
DIS_WIDTH = 600
DIS_HEIGHT = 400

dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
pygame.display.set_caption("Chaotic Snake by Gemini")

clock = pygame.time.Clock()

# Snake Settings
SNAKE_BLOCK = 10
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)
SCORE_FONT = pygame.font.SysFont("comicsansms", 35)


def message(msg, color):
    mesg = FONT_STYLE.render(msg, True, color)
    # Center the message
    text_rect = mesg.get_rect(center=(DIS_WIDTH / 2, DIS_HEIGHT / 2))
    dis.blit(mesg, text_rect)


def gameLoop():
    game_over = False
    game_close = False

    # Starting Position
    x1 = DIS_WIDTH / 2
    y1 = DIS_HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Food Position
    foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
    foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0

    # CHAOS VARIABLES
    last_chaos_time = time.time()
    chaos_interval = 10  # Seconds between chaos events
    chaos_duration = 5  # How long the chaos lasts
    current_chaos = None  # 'REVERSE', 'SPEED', 'COLOR'
    chaos_end_time = 0

    # Base Speed
    snake_speed = 15

    while not game_over:

        while game_close == True:
            dis.fill(BLACK)
            message("You Lost! Press Q-Quit or C-Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # --- CHAOS LOGIC ---
        current_time = time.time()

        # Trigger Chaos
        if current_chaos is None and (current_time - last_chaos_time > chaos_interval):
            modes = ["REVERSE", "SPEED", "FLASH"]
            current_chaos = random.choice(modes)
            chaos_end_time = current_time + chaos_duration
            last_chaos_time = chaos_end_time  # Reset timer for next cycle

        # Check if Chaos is over
        if current_chaos and current_time > chaos_end_time:
            current_chaos = None
            snake_speed = 15  # Reset speed

        # --- INPUT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Normal Controls
                left = pygame.K_LEFT
                right = pygame.K_RIGHT
                up = pygame.K_UP
                down = pygame.K_DOWN

                # REVERSE CHAOS: Swap the keys!
                if current_chaos == "REVERSE":
                    left, right = right, left
                    up, down = down, up

                if event.key == left:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                elif event.key == right:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                elif event.key == up:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                elif event.key == down:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0

        # Boundary Check
        if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change

        # Background Color Logic
        bg_color = BLACK
        if current_chaos == "FLASH":
            bg_color = random.choice([BLACK, PURPLE, BLUE])
        elif current_chaos == "REVERSE":
            bg_color = (50, 50, 50)  # Dark Grey
        elif current_chaos == "SPEED":
            bg_color = (50, 0, 0)  # Dark Red

        dis.fill(bg_color)

        # Draw Food
        pygame.draw.rect(dis, GREEN, [foodx, foody, SNAKE_BLOCK, SNAKE_BLOCK])

        # Snake Movement Logic
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        # Draw Snake
        for x in snake_List:
            pygame.draw.rect(dis, YELLOW, [x[0], x[1], SNAKE_BLOCK, SNAKE_BLOCK])

        # Draw Chaos Status Text
        if current_chaos:
            status = f"CHAOS: {current_chaos}!"
            text = SCORE_FONT.render(status, True, WHITE)
            dis.blit(text, [10, 10])
        else:
            # Show Score
            value = SCORE_FONT.render(
                "Score: " + str(Length_of_snake - 1), True, YELLOW
            )
            dis.blit(value, [0, 0])

        pygame.display.update()

        # Handle Food Consumption
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
            foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
            Length_of_snake += 1

        # SPEED CHAOS: Double the framerate
        if current_chaos == "SPEED":
            clock.tick(30)
        else:
            clock.tick(snake_speed)

    pygame.quit()
    quit()


gameLoop()
