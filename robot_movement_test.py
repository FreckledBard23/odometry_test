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
# ^^ update, never

import pygame
from math import *
import random

pygame.init()

screen_size = 600
size = (screen_size * 1.5, screen_size)
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

# y is height, z is depth
scale_factor = 16
def project_3d(x, y, z):
    return (x * scale_factor / z, y * scale_factor / z)

def center_on_screen(pt):
    return (pt[0] * (screen_size / 2 / world_scale) + screen_size / 2, -pt[1] * (screen_size / 2 / world_scale) + screen_size / 2)

camera_rot = 0 #rotation of board

#there are 2 set positions for the camera - overhead (top) and at an angle (rest)
camera_y_rest = 20
camera_pitch_rot_rest = -0.75
camera_height_rest = 15
camera_y_top = 0
camera_pitch_rot_top = -pi / 2
camera_height_top = 30
camera_y = camera_y_rest
camera_pitch_rot = camera_pitch_rot_rest
camera_height = camera_height_rest

def draw_line_on_board(x1, y1, x2, y2, color):
    nx1, ny1 = rotate(x1, y1, camera_rot)
    nx2, ny2 = rotate(x2, y2, camera_rot)
    ny1, nz1 = rotate(-camera_height, ny1 + camera_y, camera_pitch_rot)
    ny2, nz2 = rotate(-camera_height, ny2 + camera_y, camera_pitch_rot)
    pt1 = project_3d(nx1, ny1, nz1)
    pt2 = project_3d(nx2, ny2, nz2)
    pygame.draw.line(screen, color, center_on_screen(pt1), center_on_screen(pt2))

class obstruction:
    x = 0
    y = 0
    rot = 0
    width = 1
    depth = 1
    height = 1

    def get_verticies(self): #coordinates of all points in the base of the rectangular prism
        raw_points = [(-self.width / 2, -self.height / 2), (-self.width / 2, self.height / 2), (self.width / 2, self.height / 2), (self.width / 2, -self.height / 2)]
        pts = []
        for i in range(4):
            rotated_x, rotated_y = rotate(raw_points[i][0], raw_points[i][1], self.rot)
            pts.append((rotated_x + self.x, rotated_y + self.y))

        return pts

    def draw(self):
        verticies = self.get_verticies()
        lower_screen_points = []
        upper_screen_points = []

        for vertex in verticies:
            nx, ny = rotate(vertex[0], vertex[1], camera_rot)
            ny, nz = rotate(-camera_height, ny + camera_y, camera_pitch_rot)
            projection = project_3d(nx, ny, nz)
            lower_screen_points.append(center_on_screen(projection))
    
        for vertex in verticies:
            nx, ny = rotate(vertex[0], vertex[1], camera_rot)
            ny, nz = rotate(-camera_height + self.depth, ny + camera_y, camera_pitch_rot)
            projection = project_3d(nx, ny, nz)
            upper_screen_points.append(center_on_screen(projection))
    
        for i in range(len(lower_screen_points)):
            pygame.draw.line(screen, (255, 0, 255), upper_screen_points[i], upper_screen_points[(i + 1) % len(upper_screen_points)], 1)
        
        for i in range(len(lower_screen_points)):
            pygame.draw.line(screen, (255, 0, 255), lower_screen_points[i], lower_screen_points[(i + 1) % len(lower_screen_points)], 1)
            pygame.draw.line(screen, (255, 0, 255), lower_screen_points[i], upper_screen_points[i], 1)
            pygame.draw.line(screen, (255, 0, 255), lower_screen_points[(i + 1) % len(lower_screen_points)],
                                                    upper_screen_points[(i + 1) % len(lower_screen_points)], 1)

def draw_border():
    border_points = [(-world_scale, -world_scale), (world_scale, -world_scale), (world_scale, world_scale), (-world_scale, world_scale)]
    screen_points = []
    
    for pt in border_points:
        nx, ny = rotate(pt[0], pt[1], camera_rot)
        ny, nz = rotate(-camera_height, ny + camera_y, camera_pitch_rot)
        pt2 = project_3d(nx, ny, nz)
        screen_points.append(center_on_screen(pt2))

    color = (80, 80, 80)
    color_bright = (160, 160, 160)
    for i in range(-world_scale + 1, world_scale):
        nx1, ny1 = rotate(i, world_scale + ((i == 0) * 0.2 * world_scale), camera_rot)
        ny1, nz1 = rotate(-camera_height, ny1 + camera_y, camera_pitch_rot)
        pt1 = project_3d(nx1, ny1, nz1)
        nx2, ny2 = rotate(i, -world_scale, camera_rot)
        ny2, nz2 = rotate(-camera_height, ny2 + camera_y, camera_pitch_rot)
        pt2 = project_3d(nx2, ny2, nz2)

        if i != 0:
            pygame.draw.line(screen, color, center_on_screen(pt1), center_on_screen(pt2))
        else:
            pygame.draw.line(screen, color_bright, center_on_screen(pt1), center_on_screen(pt2))
    
    for i in range(-world_scale + 1, world_scale):
        nx1, ny1 = rotate(world_scale + ((i == 0) * 0.2 * world_scale), i, camera_rot)
        ny1, nz1 = rotate(-camera_height, ny1 + camera_y, camera_pitch_rot)
        pt1 = project_3d(nx1, ny1, nz1)
        nx2, ny2 = rotate(-world_scale, i, camera_rot)
        ny2, nz2 = rotate(-camera_height, ny2 + camera_y, camera_pitch_rot)
        pt2 = project_3d(nx2, ny2, nz2)
        
        if i != 0:
            pygame.draw.line(screen, color, center_on_screen(pt1), center_on_screen(pt2))
        else:
            pygame.draw.line(screen, color_bright, center_on_screen(pt1), center_on_screen(pt2))
    
    pygame.draw.lines(screen, (255, 255, 255), True, screen_points)

def draw_robot_outline(x, y, rotation, color):
    outline_points = [(-0.5, -0.5), (-0.5, 0.5), (0, 0.8), (0.5, 0.5), (0.5, -0.5)]
    screen_points = []
    
    for pt_raw in outline_points:
        new_x, new_y = rotate(pt_raw[0], pt_raw[1], rotation)
        pt = (new_x + x, new_y + y)
        nx, ny = rotate(pt[0], pt[1], camera_rot)
        ny, nz = rotate(-camera_height, ny + camera_y, camera_pitch_rot)
        pt2 = project_3d(nx, ny, nz)
        screen_points.append(center_on_screen(pt2))

    pygame.draw.lines(screen, color, True, screen_points)

#I'm too lazy to learn how pygame fonts work, I'll tally the hours wasted here for number display
# start time 5/22/2026 10:21 pm
# 10:54 -> nvm took like 40 min 
number_data = [[1, 1, 1, 1, 1, 1, 0], #0
               [0, 1, 1, 0, 0, 0, 0], #1
               [1, 1, 0, 1, 1, 0, 1], #2
               [1, 1, 1, 1, 0, 0, 1], #3
               [0, 1, 1, 0, 0, 1, 1], #4
               [1, 0, 1, 1, 0, 1, 1], #5
               [1, 0, 1, 1, 1, 1, 1], #6
               [1, 1, 1, 0, 0, 0, 0], #7
               [1, 1, 1, 1, 1, 1, 1], #8
               [1, 1, 1, 0, 0, 1, 1], #9
               [0, 0, 0, 0, 0, 0, 1], #minus sign
               [0, 0, 0, 0, 0, 0, 0]] #interpeted as decimal point
def display_digit(num, x, y, scale, thickness):
    #seven seg thing
    if number_data[num][0]:
        pygame.draw.rect(screen, UI, ((x, y), (0.6 * scale, thickness)))
    if number_data[num][6]:
        pygame.draw.rect(screen, UI, ((x, y + scale * 0.5 - thickness * 0.5), (scale * 0.6, thickness)))
    if number_data[num][3]:
        pygame.draw.rect(screen, UI, ((x, y + scale - thickness), (0.6 * scale, thickness)))   
    if number_data[num][5]:
        pygame.draw.rect(screen, UI, ((x, y), (thickness, 0.5 * scale)))
    if number_data[num][1]:
        pygame.draw.rect(screen, UI, ((x + scale * 0.6 - thickness, y), (thickness, 0.5 * scale)))
    if number_data[num][2]:
        pygame.draw.rect(screen, UI, ((x + scale * 0.6 - thickness, y + 0.5 * scale), (thickness, 0.5 * scale)))
    if number_data[num][4]:
        pygame.draw.rect(screen, UI, ((x, y + 0.5 * scale), (thickness, 0.5 * scale)))
    if num == 11:
        pygame.draw.rect(screen, UI, ((x + scale * 0.3 - thickness * 0.5, y + scale - thickness), (thickness, thickness)))
def display_number(num, x, y, scale, thickness, max_digits):
    string_num = str(num)

    offset = 0
    digit_num = 0
    for digit in string_num:
        if digit == '.':
            display_digit(11, x + offset, y, scale, thickness)
        elif digit == '-':
            display_digit(10, x + offset, y, scale, thickness)
        else:
            display_digit(int(digit), x + offset, y, scale, thickness)
        offset += scale * 0.65

        digit_num += 1
        if digit_num == max_digits:
            return

ROBOT = (0, 255, 0)
TARGET = (0, 127, 255)
STATION = (255, 127, 0)
DEBUG = (255, 255, 0)
UI = (255, 0, 0)


# --------------- movement helper functions ----------------
robot_x =   0
robot_y =   0
robot_rot = 0 #rotation
robot_ox =  0 #odometry x, assumes robot is always facing to +Y
robot_oy =  0 #odometry y,  ^^^^^^^^^^^
robot_oxt = 0 #odometry temporary x
robot_oyt = 0 #odometry temporary y
robot_tx  = 0 #target x relative to odometry info
robot_ty  = 0 #^^     y ^^       ^^ ^^       ^^
#no odometry rotation variable as it doesn't differ from what is actually happening. A simple PID controller or something else
#  to directly move the turn the robot if the odometry says that it doesn't have the right angle would suffice for control

robot_frame_ax = 0 #robot planned frame x movement (x dir is relative to heading)
robot_frame_ay = 0
robot_frame_arot = 0

speed = 0.05
movement_moe = 0.026 #margin of error, has to be at least this close in x and y to register as at a station
rotation_speed = 0.1
rotation_moe = 0.06
rotation_dir = 0

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
for i in range(6):
    stations.append(station())

obstructions = []
obstructions.append(obstruction())
obstructions[0].x = -5
obstructions[0].y = 3
obstructions[0].rot = 1
obstructions[0].width = 4
obstructions[0].height = 2
obstructions[0].depth = 5

for s in stations:
    s.generate_pos()

chosen_target = 0

#  0 - record current odometry readings to temp odometry vars, translate target station pos to be relative to odometry readings
#  1 - move to station
#  2 - rotate to match station rotation
#  3 - do nothing, wait until new chosen_target set and restart by changing step to 0
step = 0

#move the global position of the robot in order to update screen visualization, not needed in physical implementation
def handle_robot_pos_movement():
    global robot_x, robot_y

    dx, dy = rotate(robot_frame_ax, robot_frame_ay, robot_rot)
    robot_x = robot_x + dx
    robot_y = robot_y + dy

#purely used for the debug lines on the wheels
#serves 0 other purpose
wheel_visualization_pos = [0, 0, 0, 0]
wheel_height = 0.08
wheel_width = 0.06
wheel_line_amount = 5

#x and y are relative to the ui box on the right. x ranges from 0 - 0.5, y is 0 - 1
#angle is if the wheel 'sub wheels' are mirrored, text above is where to put the speed text
#wheel id is just for the 'animation'
#
# If this function breaks, give up
# it is too complicated and too messy
# go pray to the Machine Spirit and the Omnissiah and light some candles
def draw_wheel(x, y, angle, speed, text_above, wheel_id):
    pygame.draw.rect(screen, UI, ((screen_size * (1 + x), y * screen_size), (wheel_width * screen_size, wheel_height * screen_size)), 1)
    
    line_slope = 0.04
    if angle == True:
        line_slope = -line_slope
    line_y = y + (wheel_visualization_pos[wheel_id] - floor(wheel_visualization_pos[wheel_id])) * wheel_height
    for i in range(wheel_line_amount):
        y_offset = (i / wheel_line_amount) * wheel_height
        line_y_ = line_y + y_offset
        
        if line_y_ - y > wheel_height:
            line_y_ -= wheel_height

        #smart clamp the lines to be within the rectangle
        if (line_y_ - y + line_slope) > wheel_height:
            new_y_offset = (line_y_ - y + line_slope) - wheel_height
            new_x_offset = wheel_width * (1 - (new_y_offset / line_slope))
            pygame.draw.line(screen, UI, (screen_size * (1 + x),                     line_y_ * screen_size),
                                         (screen_size * (1 + x + new_x_offset) - 1, (line_y_ - new_y_offset + line_slope) * screen_size - 1))
            pygame.draw.line(screen, UI, (screen_size * (1 + x + new_x_offset),      y * screen_size),
                                         (screen_size * (1 + x + wheel_width) - 1,  (y + new_y_offset) * screen_size))
        elif (line_y_ - y + line_slope) < 0:
            new_y_offset = (line_y_ - y + line_slope)
            new_x_offset = wheel_width * (1 - (new_y_offset / line_slope))
            pygame.draw.line(screen, UI, (screen_size * (1 + x),                     line_y_ * screen_size),
                                         (screen_size * (1 + x + new_x_offset) - 1, (line_y_ - new_y_offset + line_slope) * screen_size))
            pygame.draw.line(screen, UI, (screen_size * (1 + x + new_x_offset),     (y + wheel_height) * screen_size - 1),
                                         (screen_size * (1 + x + wheel_width) - 1,  (y + new_y_offset + wheel_height) * screen_size))
        else:
            line_y_ *= screen_size
            pygame.draw.line(screen, UI, (screen_size * (1 + x), line_y_), (screen_size * (1 + x + wheel_width) - 1, line_y_ + line_slope * screen_size))
    
    if not text_above:
        display_number(speed / 0.1, (1 + x) * screen_size, (y - 0.06) * screen_size, screen_size / 40, screen_size / 200, 5)
    else: 
        display_number(speed / 0.1, (1 + x) * screen_size, (y + wheel_height + 0.04) * screen_size - screen_size / 200, screen_size / 40, screen_size / 200, 5)

def draw_robot_motor_info():
    pygame.draw.line(screen, UI, (screen_size, 0), (screen_size, screen_size))

    pygame.draw.rect(screen, UI, ((screen_size * 1.15, 0.1 * screen_size), (0.2 * screen_size, 0.3 * screen_size)), 1)


    speed_fl = -robot_frame_ay - robot_frame_ax - robot_frame_arot
    speed_fr = -robot_frame_ay + robot_frame_ax + robot_frame_arot
    speed_bl = -robot_frame_ay + robot_frame_ax - robot_frame_arot
    speed_br = -robot_frame_ay - robot_frame_ax + robot_frame_arot

    draw_wheel(0.15 - wheel_width - 0.01, 0.12, False, speed_fl, False, 0)
    draw_wheel(0.15 - wheel_width - 0.01, 0.38 - wheel_height, True, speed_bl, True, 1)
    draw_wheel(0.35 - (1 / (screen_size * 0.5)) + 0.01, 0.12, True, speed_fr, False, 2)
    draw_wheel(0.35 - (1 / (screen_size * 0.5)) + 0.01, 0.38 - wheel_height, False, speed_br, True, 3)

    wheel_visualization_pos[0] += speed_fl * 0.4
    wheel_visualization_pos[1] += speed_bl * 0.4
    wheel_visualization_pos[2] += speed_fr * 0.4
    wheel_visualization_pos[3] += speed_br * 0.4


mousex_temp = 0
mousey_temp = 0
camera_rot_temp = 0
old_pressed = [False, False, False]
mouse_sensitivity = 0.75
camera_move_speed = 0.05
while not quitting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitting = True
    
    # ------------ movement code -------------
    
    robot_frame_ax = 0
    robot_frame_ay = 0
    robot_frame_arot = 0
        
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
        #could replace with a straight line trajectory but this is easier
        #if robot_ox < robot_tx - movement_moe:
        #    robot_frame_ax = speed
        #elif robot_ox > robot_tx + movement_moe:
        #    robot_frame_ax = -speed
        #if robot_oy < robot_ty - movement_moe:
        #    robot_frame_ay = speed
        #elif robot_oy > robot_ty + movement_moe:
        #    robot_frame_ay = -speed
        
        x_difference = robot_tx - robot_ox
        y_difference = robot_ty - robot_oy
        magnitude = sqrt(x_difference ** 2 + y_difference ** 2)
        x_difference /= magnitude
        y_difference /= magnitude
    
        if abs(robot_tx - robot_ox) > movement_moe:
            robot_frame_ax = x_difference * speed
        if abs(robot_ty - robot_oy) > movement_moe:
            robot_frame_ay = y_difference * speed

        #simulate odometry changing as would happen during movement
        robot_ox += robot_frame_ax
        robot_oy += robot_frame_ay

        #updates robot_x/y so the screen is accurate
        handle_robot_pos_movement()

        if robot_frame_ax == 0 and robot_frame_ay == 0:
            step = 2
    elif step == 2:
        # if clockwise dist less than pi go clockwise, else ccw
        if rotation_dir == 0:
            if stations[chosen_target].rot > robot_rot:
                clockwise_dist = stations[chosen_target].rot - robot_rot

                if clockwise_dist < pi:
                    rotation_dir = 1
                else:
                    rotation_dir = 2
            else:
                counterclockwise_dist = robot_rot - stations[chosen_target].rot

                if counterclockwise_dist < pi:
                    rotation_dir = 2
                else:
                    rotation_dir = 1

        if rotation_dir == 1:
            robot_rot += rotation_speed
            robot_frame_arot += speed
            if robot_rot > 2 * pi:
                robot_rot -= 2 * pi
        elif rotation_dir == 2:
            robot_rot -= rotation_speed
            robot_frame_arot -= speed
            if robot_rot < 0:
                robot_rot += 2 * pi
        
        if abs(robot_rot - stations[chosen_target].rot) < rotation_moe:
            step = 3


    elif step == 3:
        # choose new station, in this case, just select next one in list, loop if needed
        chosen_target += 1
        if chosen_target == len(stations):
            chosen_target = 0
        step = 0
        rotation_dir = 0




    # --------------- mouse and other input ----------

    pressed = pygame.mouse.get_pressed(3)
    
    if pressed[0] and not old_pressed[0]:
        mpos = pygame.mouse.get_pos()
        mousex_temp = mpos[0]
        mousey_temp = mpos[1]
        camera_rot_temp = camera_rot

    if pressed[0]:
        mpos = pygame.mouse.get_pos()
        camera_rot = camera_rot_temp + -((mousex_temp - mpos[0]) / 100) * mouse_sensitivity
    
    if camera_rot > 2 * pi:
        camera_rot -= 2 * pi
    if camera_rot < 0:
        camera_rot += 2 * pi
   
    if pressed[2]:
        camera_y = camera_y * (1 - camera_move_speed) + camera_y_top * camera_move_speed
        camera_pitch_rot = camera_pitch_rot * (1 - camera_move_speed) + camera_pitch_rot_top * camera_move_speed
        camera_height = camera_height * (1 - camera_move_speed) + camera_height_top * camera_move_speed
    else:
        camera_y = camera_y * (1 - camera_move_speed) + camera_y_rest * camera_move_speed
        camera_pitch_rot = camera_pitch_rot * (1 - camera_move_speed) + camera_pitch_rot_rest * camera_move_speed
        camera_height = camera_height * (1 - camera_move_speed) + camera_height_rest * camera_move_speed

    old_pressed = pressed

    # --------------- rendering code -----------------
    screen.fill((0, 0, 0))
    
    draw_border()

    draw_robot_motor_info();

    draw_robot_outline(robot_x, robot_y, robot_rot, ROBOT)
    
    for i in range(len(stations)):
        if i != chosen_target:
            stations[i].render(STATION)
        else:
            stations[i].render(TARGET)
    
    for i in range(len(obstructions)):
        obstructions[i].draw()

    pygame.display.flip()
    clock.tick(40) #40 fps

pygame.quit()
