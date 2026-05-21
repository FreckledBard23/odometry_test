# odometry test
# made under the assumtion that the odometry X and Y values don't take heading into account
# odometry navigation is easier if this is not the case
#
# example:
#                             ^
# if robot is facing this way | and going forward, Y val increases and X is the same
#                             |
#
#                               ^
# if robot is facing this way  /  and going forward, still only the Y val increases because the X and Y readouts don't care about
#                             /                                          heading, only movement relative to the sensor orientation
#
# in other words, this is written assuming that the position readouts of the odometry sensor always assume that the robot has no angle
# 
# this is the easiest for the sensor to implement as it saves on trig math + calculations, but more difficult to use
#
# Psudocode coming shortly

import pygame
from math import *
import random

pygame.init()

screen_size = 400
size = (screen_size, screen_size)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("FTC Test")

quitting = False

clock = pygame.time.Clock()

world_scale = 10

def draw_robot_outline(x, y, rotation, color):
    #hardcoded 'sprite'
    #sorry about readability, whoever is seeing this in the future

    #rough drawing
    #      ___
    #  __--   --__
    #  |         |
    #  |         |
    #  |         |
    #  |_________|

    #     point xval                     yval                          <--------adjustment to fit onto screen-------->
    rot_x = [ ((-0.5) * cos(rotation) - (-0.5) * sin(rotation) + x) * (screen_size / 2 / world_scale) + screen_size / 2,
              ((-0.5) * cos(rotation) - (+0.5) * sin(rotation) + x) * (screen_size / 2 / world_scale) + screen_size / 2,
              ((   0) * cos(rotation) - (+0.8) * sin(rotation) + x) * (screen_size / 2 / world_scale) + screen_size / 2,
              ((+0.5) * cos(rotation) - (+0.5) * sin(rotation) + x) * (screen_size / 2 / world_scale) + screen_size / 2,
              ((+0.5) * cos(rotation) - (-0.5) * sin(rotation) + x) * (screen_size / 2 / world_scale) + screen_size / 2]
    #     point info repeats over here
    rot_y = [-((-0.5) * sin(rotation) + (-0.5) * cos(rotation) + y) * (screen_size / 2 / world_scale) + screen_size / 2,
             -((-0.5) * sin(rotation) + (+0.5) * cos(rotation) + y) * (screen_size / 2 / world_scale) + screen_size / 2,
             -((   0) * sin(rotation) + (+0.8) * cos(rotation) + y) * (screen_size / 2 / world_scale) + screen_size / 2,
             -((+0.5) * sin(rotation) + (+0.5) * cos(rotation) + y) * (screen_size / 2 / world_scale) + screen_size / 2,
             -((+0.5) * sin(rotation) + (-0.5) * cos(rotation) + y) * (screen_size / 2 / world_scale) + screen_size / 2]
    points = [(rot_x[0], rot_y[0]),(rot_x[1], rot_y[1]),(rot_x[2], rot_y[2]),(rot_x[3], rot_y[3]), (rot_x[4], rot_y[4])]

    pygame.draw.lines(screen, color, True, points)

#rotates a point around the origin
#prob should have made before draw_robot_outline func ig
def rotate(x, y, rotation):
    return x * cos(rotation) - y * sin(rotation), x * sin(rotation) + y * cos(rotation)

ROBOT = (0, 255, 0)
TARGET = (0, 127, 255)
STATION = (255, 127, 0)
DEBUG = (255, 255, 0)

robot_x =   0
robot_y =   0
robot_rot = 0 #rotation
robot_ox =  0 #odometry x, assumes robot is always facing to +Y
robot_oy =  0 #odometry y,  ^^^^^^^^^^^
robot_oxt = 0 #odometry temporary x
robot_oyt = 0 #odometry temporary y
robot_tx  = 0 #target x relative to odometry info
robot_ty  = 0 #^^     y ^^       ^^ ^^       ^^

robot_frame_ax = 0 #robot planned frame x movement (x dir is relative to heading)
robot_frame_ay = 0

#no odometry rotation variable as it doesn't differ from what is actually happening. A simple PID controller or something else
#  to directly move the turn the robot if the odometry says that it doesn't have the right angle would suffice for control

class station:
    x = 0
    y = 0
    rot = 0

    def generate_pos(self):
        self.x = (random.random() * 2 - 1) * world_scale * 0.8 # value between (-0.8 * world_scale, 0.8 * world_scale)
        self.y = (random.random() * 2 - 1) * world_scale * 0.8
        self.rot = random.random() * pi * 2

    def render(self, color):
        draw_robot_outline(self.x, self.y, self.rot, color)

stations = []
for i in range(8):
    stations.append(station())

for s in stations:
    s.generate_pos()

chosen_target = 0

#  0 - record current odometry readings to temp odometry vars, translate target station pos to be relative to odometry readings
#  1 - move to station
#  2 - rotate to match station rotation
#  3 - do nothing, wait until new chosen_target set and restart by changing step to 0
step = 0

def handle_robot_pos_movement():
    global robot_x, robot_y

    dx, dy = rotate(robot_frame_ax, robot_frame_ay, robot_rot)
    robot_x = robot_x + dx
    robot_y = robot_y + dy

speed = 0.05
movement_moe = 0.026 #margin of error, has to be at least this close in x and y to register as at a station
rotation_speed = 0.1
rotation_moe = 0.06
while not quitting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitting = True
    
    #movement code
    
    if step == 0:
        robot_oxt = robot_ox
        robot_oyt = robot_oy
        #technically the real code will not have access to robot_x and robot_y given the assumed nature of the odometry
        #however, at this point it is either at a station or at the origin, and both of those have known positions, so we can use those
        robot_tx, robot_ty = rotate(stations[chosen_target].x - robot_x, stations[chosen_target].y - robot_y, -robot_rot)
        robot_tx += robot_oxt
        robot_ty += robot_oyt
        step = 1
    elif step == 1:
        robot_frame_ax = 0
        robot_frame_ay = 0
        
        #could replace with a straight line trajectory but this is easier
        if robot_ox < robot_tx - movement_moe:
            robot_frame_ax = speed
        elif robot_ox > robot_tx + movement_moe:
            robot_frame_ax = -speed
        if robot_oy < robot_ty - movement_moe:
            robot_frame_ay = speed
        elif robot_oy > robot_ty + movement_moe:
            robot_frame_ay = -speed
        
        #simulate odometry changing as would happen during movement
        robot_ox += robot_frame_ax
        robot_oy += robot_frame_ay

        #updates robot_x/y so the screen is accurate
        handle_robot_pos_movement()

        if robot_frame_ax == 0 and robot_frame_ay == 0:
            step = 2
    elif step == 2:
        if robot_rot < stations[chosen_target].rot - rotation_moe:
            robot_rot += rotation_speed
        elif robot_rot > stations[chosen_target].rot + rotation_moe:
            robot_rot -= rotation_speed
        else:
            step = 3
    elif step == 3:
        print("at station", chosen_target)
        chosen_target += 1
        if chosen_target == len(stations):
            chosen_target = 0
        step = 0

    #rendering code
    screen.fill((0, 0, 0))
    
    draw_robot_outline(robot_x, robot_y, robot_rot, ROBOT)
    
    for i in range(len(stations)):
        if i != chosen_target:
            stations[i].render(STATION)
        else:
            stations[i].render(TARGET)

    # debug
    #draw_robot_outline(robot_tx, robot_ty, 0, DEBUG)

    pygame.display.flip()
    clock.tick(40) #40 fps

pygame.quit()
