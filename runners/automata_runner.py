from typing import Callable, List, Tuple
import pygame

from automata.automaton import Automaton

def run(screen_size: Tuple[int, int], upscaling_factor: int, automata: List[Callable[[], Automaton]], caption = 'Automata', show_text_overlays = True, framerate = 120):
    pygame.init()

    screen_size = pygame.Vector2(screen_size[0], screen_size[1])
    main_screen = pygame.display.set_mode(screen_size * upscaling_factor)
    screen = pygame.Surface(screen_size)
    pygame.display.set_caption(caption)
    font_size = int(screen_size[1] * upscaling_factor * 0.025)
    my_font = pygame.font.SysFont('Comic Sans MS', font_size)

    clock = pygame.time.Clock()

    running = True

    dt = 0
    framerate = framerate

    current_automaton_index = 0
    current_automaton = automata[current_automaton_index]()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_automaton = automata[current_automaton_index]()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                current_automaton_index = (current_automaton_index + 1) % len(automata)
                current_automaton.cleanup()
                current_automaton = automata[current_automaton_index]()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                current_automaton_index = (current_automaton_index - 1) % len(automata)
                current_automaton.cleanup()
                current_automaton = automata[current_automaton_index]()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if framerate == 1:
                    framerate = 5
                else:
                    framerate = max(1, framerate + 5)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                framerate = max(1, framerate - 5)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_automaton.toggle_pause()

        screen.fill('black')

        current_automaton.render(screen)

        upscaled = pygame.transform.scale_by(screen, upscaling_factor)
        main_screen.blit(upscaled, (0, 0))

        if show_text_overlays:
            # TEXT
            text_surface = my_font.render(f'{current_automaton.name}{(", " + current_automaton.debug_string()) if len(current_automaton.debug_string()) > 0 else ""}', False, (255, 255, 255)).convert()
            padding = 8
            temp_surface = pygame.Surface((text_surface.get_width() + (padding * 2), text_surface.get_height() + padding))
            temp_surface.fill((0, 0, 0))
            temp_surface.blit(text_surface, (padding, padding / 2))
            main_screen.blit(temp_surface, (0, main_screen.get_height() - temp_surface.get_height()))

            # Global Text
            text_surface = my_font.render(f'{framerate} FPS', False, (255, 255, 255)).convert()
            padding = 8
            temp_surface = pygame.Surface((text_surface.get_width() + (padding * 2), text_surface.get_height() + padding))
            temp_surface.fill((0, 0, 0))
            temp_surface.blit(text_surface, (padding, padding / 2))
            main_screen.blit(temp_surface, (0, 0))

        pygame.display.flip()
        current_automaton.iterate(dt)

        dt = clock.tick(framerate) / 1000
