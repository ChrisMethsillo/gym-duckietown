#!/usr/bin/env python
# manual

"""
This script allows you to manually control the simulator or Duckiebot
using the keyboard arrows.
"""

import sys
import argparse
import pyglet
from pyglet.window import key
import numpy as np
import gym
import gym_duckietown
from gym_duckietown.envs import DuckietownEnv
from gym_duckietown.wrappers import UndistortWrapper
from gym_duckietown.distortion import Distortion

# from experiments.utils import save_img

parser = argparse.ArgumentParser()
parser.add_argument('--env-name', default=None)
parser.add_argument('--map-name', default='udem1')
parser.add_argument('--distortion', default=0, type=int, help="Activate eye fish distortion")
parser.add_argument('--draw-curve', default=0, type=int, help='draw the lane following curve')
parser.add_argument('--draw-bbox', default=0, type=int, help='draw draw_bbox detection bounding boxes')
parser.add_argument('--domain-rand', action='store_true', help='enable domain randomization')
parser.add_argument('--frame-skip', default=1, type=int, help='number of frames to skip')
parser.add_argument('--seed', default=1, type=int, help='seed')
parser.add_argument('--linearspeed', default=0.44, type=float, help='linear speed')
parser.add_argument('--bend', default=0.35, type=float, help='bend')
parser.add_argument('--camera', default='human', type=str, help='Camera position')
parser.add_argument('--camerachanger', default='', type=str, help='Camera Changer')
args = parser.parse_args()

if args.env_name and args.env_name.find('Duckietown') != -1:
    env = DuckietownEnv(
        seed = args.seed,
        map_name = args.map_name,
        draw_curve = bool(args.draw_curve),
        draw_bbox = bool(args.draw_bbox),
        domain_rand = args.domain_rand,
        frame_skip = args.frame_skip,
        distortion = bool(args.distortion),
    )
else:
    env = gym.make(args.env_name)
env.reset()
env.render()

camera=args.camera

@env.unwrapped.window.event
def on_key_press(symbol, modifiers):
    """
    This handler processes keyboard commands that
    control the simulation
    """

    if symbol == key.BACKSPACE or symbol == key.SLASH:
        print('RESET')
        camera=args.camera
        env.reset()
        env.render(camera)
    elif symbol == key.PAGEUP:
        env.unwrapped.cam_angle[0] = 0
    elif symbol == key.ESCAPE:
        env.close()
        sys.exit(0)

    # Take a screenshot
    # UNCOMMENT IF NEEDED - Skimage dependency
    # elif symbol == key.RETURN:
    #     print('saving screenshot')
    #     img = env.render('rgb_array')
    #     save_img('screenshot.png', img)

# Register a keyboard handler
key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

def update(dt):
    global camera
    action = np.array([0.0, 0.0])
    
    bend=args.bend
    lspeed=args.linearspeed

    if key_handler[key.UP]:
        action = np.array([lspeed, 0.0])
    if key_handler[key.DOWN]:
        action = np.array([-lspeed, 0])
    if key_handler[key.LEFT]:
        action = np.array([lspeed*0.8, +bend])
    if key_handler[key.RIGHT]:
        action = np.array([lspeed*0.8, -bend])
    if key_handler[key.SPACE]:
        action = np.array([0, 0])

    if key_handler[key.Z]:
        camera="top_down"
        env.render(camera)
        env.distortion=False
        env.draw_bbox=False

    if key_handler[key.X]:
        camera="human"
        env.render(camera)
        env.distortion=False
        env.draw_bbox=False

    if key_handler[key.C]:
        env.camera_model = Distortion()
        camera="human"
        env.distortion=True
        env.draw_bbox=False

    if key_handler[key.V]:
        env.camera_model = Distortion()
        camera="human"
        env.render(camera)
        env.distortion=False
        env.draw_bbox=True


    # Speed boost
    if key_handler[key.LSHIFT]:
        action *= 1.5

    obs, reward, done, info = env.step(action)
    print('step_count = %s, reward=%.3f' % (env.unwrapped.step_count, reward))

    if key_handler[key.RETURN]:
        from PIL import Image
        im = Image.fromarray(obs)

        im.save('screen.png')

    if done:
        print('done!')
        env.reset()
        env.render()

    env.render(camera)

pyglet.clock.schedule_interval(update, 1.0 / env.unwrapped.frame_rate)

# Enter main event loop
pyglet.app.run()

env.close()
