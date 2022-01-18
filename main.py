import sys
import pygame
import random
import os
from pygame import font
import sqlite3

pygame.init()

USERNAME = None
Pepega = False

def main():
    clock = pygame.time.Clock()
    FPS = 60
    game = False
    game_over = False

    # Получаем константы, находим разрешение экрана и включаем игру на полный экран
    screen_height = pygame.display.Info().current_h
    screen_width = pygame.display.Info().current_w
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption('Flappy Bird')

    # Подгрузка фона
    bg = pygame.image.load(os.path.join("assets/photo", "background.png"))
    bg = pygame.transform.scale(bg, (screen_width, screen_height * 0.85))
    bg_ground = pygame.image.load(os.path.join("assets/photo", "ground.png"))
    bg_ground = pygame.transform.scale(bg_ground, (screen_width * 1.08, screen_height * 0.15))

    scrolling_ground = 0
    scrolling_speed = 3
    pipe_gap = screen_height * 0.25
    pipe_frequency = 3000
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    font_name = pygame.font.match_font('arail')
    WHITE = (255, 255, 255)
    passage_through_pipe = False
    pygame.font.init()
    myfont = font.SysFont('Comic Sans MS', 30)
    # Подключение бд
    db = sqlite3.connect('Flap.db')
    cur = db.cursor()

    # Функция для счётчика
    def score(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    # Лучший счёт
    def best_score(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    # Класс с птичкой
    class Bird(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            pygame.sprite.Sprite.__init__(self)
            self.images_bird = []
            self.index_image = 0
            self.counter = 0
            for i in range(1, 4):
                img = pygame.image.load(f'assets/photo/bird{i}.png')
                img = pygame.transform.scale(img, (51 * 1.7, 36 * 1.7))
                self.images_bird.append(img)
            self.image = self.images_bird[self.index_image]
            self.rect = self.image.get_rect()
            self.rect.center = [pos_x, pos_y]
            self.speed_bird = 0
            self.clicked = False

        def update(self):
            # Гравитация
            if game:
                if self.speed_bird < 8:
                    self.speed_bird += screen_height * 0.0006
                if self.rect.bottom < screen_height * 0.85:
                    self.rect[1] += int(self.speed_bird)

            if game_over == False:
                # Прыжок
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    self.clicked = True
                    self.speed_bird -= screen_height * 0.015
                    pygame.mixer.music.load('assets/sounds/wing.wav')
                    pygame.mixer.music.play(0)
                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

                # Обрабатка анимации
                self.counter += 1
                flap_cooldown = 5

                if self.counter > flap_cooldown:
                    self.counter = 0
                    self.index_image += 1
                    if self.index_image >= len(self.images_bird):
                        self.index_image = 0
                self.image = self.images_bird[self.index_image]

                self.image = pygame.transform.rotate(self.images_bird[self.index_image], self.speed_bird * -1.5)

    # Класс с трубами
    class Pipe(pygame.sprite.Sprite):
        def __init__(self, x, y, position):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('assets/photo/pipe.png')
            self.image = pygame.transform.scale(self.image, (screen_width * 0.1, screen_height * 1))
            self.rect = self.image.get_rect()
            if position == 1:
                self.image = pygame.transform.flip(self.image, False, True)
                self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
            if position == -1:
                self.rect.topleft = [x, y + int(pipe_gap / 2)]

        def update(self):
            self.rect.x -= 4
            if self.rect.right < 0:
                self.kill()

    bird_group = pygame.sprite.Group()
    player = Bird(screen_width * 0.1, screen_height // 2)
    bird_group.add(player)

    pipe_group = pygame.sprite.Group()

    run = True

    # Счёт
    score_pl = 0

    # Основное меню
    def name_edit():
        scrolling_ground = 0
        text_wel = myfont.render('Welcome', True, WHITE)
        name = 'User Name'
        find_name = False
        while not find_name:
            screen.blit(bg, (0, 0))

            # Отрисовака труб
            pipe_group.draw(screen)

            # Прорисовка земли
            screen.blit(bg_ground, (scrolling_ground, screen_height - screen_height * 0.15))
            scrolling_ground -= scrolling_speed

            # Прокрутка земли
            if abs(scrolling_ground) > screen_width * 0.08:
                scrolling_ground = 0

            # Отрисовка птицы
            bird_group.draw(screen)
            bird_group.update()

            text_name = myfont.render(name, True, WHITE)
            rec_name = text_name.get_rect()
            rec_name.center = screen.get_rect().center

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha():
                        if name == 'User Name':
                            name = event.unicode
                        else:
                            name += event.unicode
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(name) > 1:
                            global USERNAME
                            USERNAME = name
                            find_name = True
                            break

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            global Pepega
            Pepega = True
            score(screen, 'Welcome', 50, screen_width / 2, 10)
            screen.blit(text_name, rec_name)
            pygame.display.update()
            clock.tick(FPS)
    global Pepega
    if not Pepega:
        name_edit()
    detect = db.execute("SELECT * FROM main WHERE name=?",
                        (USERNAME,)).fetchall()
    if detect:
        best = db.execute("SELECT * FROM main WHERE name=?",
                          (USERNAME,)).fetchall()[0][2]
    else:
        best = 0
        db.execute(f"""INSERT INTO main
                                  (name, score)
                                  VALUES
                                  ('{USERNAME}', '{best}');""")
        db.commit()
    # Основной цикл
    while run:

        # Прорисовка фона
        if game_over == False:
            # Прорисовка заднего фона
            screen.blit(bg, (0, 0))

            # Отрисовака труб
            pipe_group.draw(screen)

            # Прорисовка земли
            screen.blit(bg_ground, (scrolling_ground, screen_height - screen_height * 0.15))
            scrolling_ground -= scrolling_speed

            # Прокрутка земли
            if abs(scrolling_ground) > screen_width * 0.08:
                scrolling_ground = 0

            # Отрисовка птицы
            bird_group.draw(screen)
            bird_group.update()
        else:
            gameover = myfont.render("Press R to Respawn", False, (255, 255, 255))
            rect = gameover.get_rect()
            rect.center = screen.get_rect().center
            screen.blit(gameover, rect)

        # Проверка прикосновения к трубом
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or player.rect.top < 0:
            if best < score_pl:
                db.execute(f"""INSERT or REPLACE INTO main
                                                  (name, score)
                                                  VALUES
                                                  ('{USERNAME}', '{score_pl}');""")
                db.commit()
            game_over = True

        # Проверка выхода за пределы поля
        if player.rect.bottom > screen_height * 0.85 or player.rect.bottom < 0:
            if best < score_pl:
                db.execute(f"""INSERT or REPLACE INTO main
                                                (name, score)
                                                VALUES
                                                ('{USERNAME}', '{score_pl}');""")
                db.commit()
            game_over = True
            game = False

        if game_over == False and game == True:

            # Генирация новых труб

            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            pipe_group.update()

        # Счёт
        if game_over == False and game == True:
            if game_over == False and game == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                        and passage_through_pipe == False:
                    passage_through_pipe = True
                if passage_through_pipe == True:
                    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        score_pl += 1
                        passage_through_pipe = False
                        pygame.mixer.music.load('assets/sounds/point.wav')
                        pygame.mixer.music.play(0)

        # Проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_ESCAPE:
                    run = False

            if event.type == pygame.MOUSEBUTTONDOWN and game == False and game_over == False:
                game = True

        score(screen, str(score_pl), 50, screen_width / 2, 10)
        best_score(screen, 'Best score ' + str(best), 50, screen_width / 3, 10)
        pygame.display.update()
        clock.tick(FPS)


main()
pygame.quit()