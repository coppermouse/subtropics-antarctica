import os
import pygame

res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

pygame.display.set_mode((2, 2))

for f in os.listdir(res_path):
    if not f.endswith(".png"): 
        continue
    print(f)
    path = os.path.join(res_path,f)

    s = pygame.image.load(path).convert()
    s.set_colorkey('blue')

    n = pygame.Surface(s.get_size())
    n.fill((128,255,255))
    n.blit(s)

    pygame.image.save(n, path)


