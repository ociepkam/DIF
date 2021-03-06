# -*- coding: utf-8 -*-
import atexit
from psychopy import visual, event, core, logging
from os.path import join
import time
import os
import csv
import random


from sources.experiment_info import experiment_info
from sources.load_data import load_config
from sources.screen import get_screen_res, get_frame_rate
from sources.show_info import show_info, show_image
from sources.matrix import Matrix
from sources.draw_matrix import TrialMatrix
from sources.check_exit import check_exit



SCREEN_RES = get_screen_res()
ALL_LINES = ['row', 'column']
KEYS = ['left', 'right']
KEYS_TO_TRIAL_TYPE = {k: a for k, a in zip(KEYS, ALL_LINES)}

part_id, part_sex, part_age, date = experiment_info()
NAME = "{}_{}_{}".format(part_id, part_sex, part_age)

RESULTS = list()
RESULTS.append(['NR', 'EXPERIMENT', 'ACC', 'RT', 'TIME', 'LEVEL', 'TRIAL_TYPE'])
RAND = str(random.randint(100, 999))

logging.LogFile(join('.', 'results', 'logging', NAME + '_' + RAND + '.log'), level=logging.INFO)


@atexit.register
def save_beh():
    logging.flush()
    with open(os.path.join('results', 'behavioral_data', 'beh_{}_{}.csv'.format(NAME, RAND)), 'w') as csvfile:
        beh_writer = csv.writer(csvfile)
        beh_writer.writerows(RESULTS)

def replace_polish(text):
    letters = {"Ĺ»": "Ż", "Ã": "Ó", "Ă“": "Ł", "Ä†": "Ć", "Ä": "Ę", "Ĺš": "Ś", "Ä„": "Ą", "Ĺą": "Ź", "Å": "Ń",
               "ĹĽ": "ż", "Ã³": "ó", "Ĺ‚": "ł", "Ä‡": "ć", "Ä™": "ę", "Ĺ›": "ś", "Ä…": "ą", "Ĺş": "ź", "Ĺ„": "ń"}

    for k, v in letters.items():
        text = text.replace(k, v)
    return text

def create_items_frames(stimulus_matrix):
    frames = []
    for elem in stimulus_matrix:
        frames.append(visual.Rect(window, width=config["width"], height=config["height"], opacity=0,
                                  lineColor=config["click_color"], pos=elem.pos, lineWidth=config["lineWidth"]))
    return frames


def create_answer_frame(answer_line_type, answer_line_number, n):
    if answer_line_type == 'row':
        pos = [0, answer_line_number * config["VIZ_OFFSET"] - (n-3)*config["VIZ_OFFSET"]/2]
        answer = visual.Rect(window, width=config["width"] * n * 1.3, height=config["height"], opacity=1,
                             lineColor=config["answer_color"], pos=pos, lineWidth=config["lineWidth"])
    elif answer_line_type == 'column':
        pos = [answer_line_number * config["VIZ_OFFSET"] - (n-1)*config["VIZ_OFFSET"]/2, config["VIZ_OFFSET"]]
        answer = visual.Rect(window, width=config["width"], height=config["height"] * n * 1.3, opacity=1,
                             lineColor=config["answer_color"], pos=pos, lineWidth=config["lineWidth"])
    else:
        raise Exception("Wrong answer_line_type")
    return answer


def run_trial(n, feedback=False):
    # Prepare trial
    m = Matrix(n=n, possible_answers=ALL_LINES)
    m.fill_matrix(distractors=config['DISTRACTORS'])
    matrix = TrialMatrix(matrix=m, position=0, window=window, viz_offset=config['VIZ_OFFSET'],
                         text_size=config['TEXT_SIZE'])
    idx_info = visual.TextStim(window, color='black', pos=(500, 400), height=50,
                               text=i)
    stim_time = config['CONST_TIME'] + m.n * config['LEVEL_TIME']
    acc = None
    rt = -1
    window.callOnFlip(response_clock.reset)
    event.clearEvents()

    # draw trial
    matrix.set_auto_draw(True)
    idx_info.setAutoDraw(True)
    frames = create_items_frames(matrix.stimulus_matrix)

    for frame in frames:
        frame.setAutoDraw(True)

    window.flip()

    # run trial
    clicked = []
    while response_clock.getTime() < stim_time and len(clicked) < 2:

        for idx, frame in enumerate(frames):
            if mouse.isPressedIn(frame) and frame.opacity == 0:
                frame.opacity = 1
                clicked.append(idx)
        if stim_time - response_clock.getTime() < config['SHOW_CLOCK']:
            clock_image.draw()
        check_exit()
        window.flip()
    rt = response_clock.getTime()
    time.sleep(config["wait_after_answer"])

    # check answer
    if m.answer_line_type == "column":
        # good_answer = [m.answer_line_number, m.answer_line_number + n*n - n]  # have to click first and last
        good_answer = list(range(m.answer_line_number, m.answer_line_number + n * n, n))  # any two elements in line

    elif m.answer_line_type == "row":
        # good_answer = [m.answer_line_number * n, m.answer_line_number * n + n - 1]  # have to click first and last
        good_answer = list(range(m.answer_line_number * n, m.answer_line_number * n + n))  # any two elements in line
    else:
        raise Exception("Wrong answer type")

    if len(clicked) == 2:
        acc = 1 if clicked[0] in good_answer and clicked[1] in good_answer else 0

    # draw feedback
    if feedback:
        answer_frame = create_answer_frame(m.answer_line_type, m.answer_line_number, n)
        answer_frame.setAutoDraw(True)
        if acc == 1:
            feedb_msg = pos_feedb
        elif acc == 0:
            feedb_msg = neg_feedb
        else:
            feedb_msg = no_feedb
        feedb_msg.setAutoDraw(True)
        window.flip()

        if config["feedback_time"] > 0:
            time.sleep(config["feedback_time"])
        elif config["feedback_time"] == -1:
            press_space_msg.setAutoDraw(True)
            window.flip()
            key = event.waitKeys(keyList=['f7', 'space'])
            if key == ['f7']:
                logging.critical('Experiment finished by user! {} pressed.'.format(key[0]))
                exit(0)

        feedb_msg.setAutoDraw(False)
        answer_frame.setAutoDraw(False)
        press_space_msg.setAutoDraw(False)

    # cleaning
    for frame in frames:
        frame.setAutoDraw(False)
    matrix.set_auto_draw(False)
    idx_info.setAutoDraw(False)
    window.flip()

    time.sleep(config['JITTER_TIME'])

    return acc, rt, stim_time, m.n, m.answer_line_type


config = load_config("config_click.yaml")

window = visual.Window(SCREEN_RES, fullscr=True, monitor='testMonitor', units='pix', color='Gainsboro')
FRAMES_PER_SEC = get_frame_rate(window)
response_clock = core.Clock()
mouse = event.Mouse(visible=True)

clock_image = visual.ImageStim(win=window, image=join('images', 'clock.png'), interpolate=True,
                               size=config['CLOCK_SIZE'], pos=config['CLOCK_POS'])
pos_feedb = visual.TextStim(window, text=replace_polish(config["pos_feedb"]), color='black', height=25, pos=(0, -200))
neg_feedb = visual.TextStim(window, text=replace_polish(config["neg_feedb"]), color='black', height=25, pos=(0, -200))
no_feedb = visual.TextStim(window, text=replace_polish(config["no_feedb"]), color='black', height=25, pos=(0, -200))

press_space_msg = visual.TextStim(window, text=u'Przyci\u015Bnij spacje', color='black', height=25, pos=(0, -300))



# TRAINING
mean_acc = 0
training_nr = 0
while mean_acc < config["min_training_acc"]:
    show_image(window, 'instruction1.png', SCREEN_RES)
    show_image(window, 'instruction2.png', SCREEN_RES)
    show_image(window, 'instruction3.png', SCREEN_RES)
    show_image(window, 'instruction4.png', SCREEN_RES)
    mean_acc = 0
    training_nr += 1
    i = 1
    for elem in config['TRAINING_TRIALS']:
        for trail in range(elem['n_trails']):
            acc, rt, stim_time, n, answer_line_type = run_trial(n=elem['level'], feedback=True)
            RESULTS.append([i, "train", acc, rt, stim_time, n, answer_line_type])
            i += 1
            if not acc:
                acc = 0
            mean_acc += acc
    if i > 1:
        mean_acc /= (i-1)
    else:
        break
    if mean_acc < config["min_training_acc"] and training_nr == 5:
        show_info(window, join('.', 'messages', "end.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
        logging.critical('Training not completed')
        exit(1)
    if mean_acc < config["min_training_acc"]:
        show_info(window, join('.', 'messages', "training_info.txt"),
                  text_size=config['TEXT_SIZE'],screen_width=SCREEN_RES[0])

# EXPERIMENT
show_info(window, join('.', 'messages', "instruction2.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])

i = 1
for elem in config['EXPERIMENT_TRIALS']:
    for trail in range(elem['n_trails']):
        acc, rt, stim_time, n, answer_line_type = run_trial(n=elem['level'])
        RESULTS.append([i, "exp", acc, rt, stim_time, n, answer_line_type])
        i += 1

show_info(window, join('.', 'messages', "end.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
