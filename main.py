import sys
import os
import pygame

root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.')
sys.path.append(os.path.join(root_path, 'source'))
sys.path.append(os.path.join(root_path, 'user'))

from on_signal import send_signal

# -- force import all modules in source, this is so decorators can be called
for file in os.listdir(os.path.join(root_path, 'source')):
    if not file.endswith('.py'):
        continue
    with open(os.path.join(root_path, 'source', file)) as f:
        m = __import__(file[:-3])
# --

send_signal('on setup')

pygame.font.init()
pygame.init()
pygame.font.init()

font = pygame.font.SysFont(None,20)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():

        if ( (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) 
           or event.type == pygame.QUIT ):
                running = False

        send_signal('on event', event)

    send_signal('on update')
    send_signal('on draw')

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
