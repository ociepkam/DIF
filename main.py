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
from sources.parameters import KEYS, KEYS_TO_TRIAL_TYPE, ALL_LINES
from sources.adaptives.NUpNDown import NUpNDown

part_id, part_sex, part_age, date = experiment_info()
NAME = "{}_{}_{}".format(part_id, part_sex, part_age)

RESULTS = list()
RESULTS.append(['NR', 'EXPERIMENTAL', 'ACC', 'RT', 'TIME', 'LEVEL', 'REVERSAL', 'REVERSAL_COUNT', 'TRIAL_TYPE'])

RAND = str(random.randint(100, 999))

logging.LogFile(join('.', 'results', 'logging', NAME + '_' + RAND + '.log'), level=logging.INFO)


@atexit.register
def save_beh():
    logging.flush()
    with open(os.path.join('results', 'behavioral_data', 'beh_{}_{}.csv'.format(NAME, RAND)), 'w') as csvfile:
        beh_writer = csv.writer(csvfile)
        beh_writer.writerows(RESULTS)


def run_trial(n):
    m = Matrix(n=n, possible_answers=ALL_LINES)
    m.fill_matrix(distractors=config['DISTRACTORS'])
    matrix = TrialMatrix(matrix=m, position=0, window=window, viz_offset=config['VIZ_OFFSET'],
                         text_size=config['TEXT_SIZE'])
    stim_time = config['CONST_TIME'] + m.n * config['LEVEL_TIME']
    acc = 0
    rt = -1
    window.callOnFlip(response_clock.reset)
    event.clearEvents()
    help_line.setAutoDraw(True)
    matrix.set_auto_draw(True)
    window.flip()
    while response_clock.getTime() < stim_time:
        if stim_time - response_clock.getTime() < config['SHOW_CLOCK']:
            clock_image.draw()
        check_exit()
        window.flip()
        keys = event.getKeys(keyList=KEYS)
        if keys:
            rt = response_clock.getTime()
            resp = KEYS_TO_TRIAL_TYPE[keys[0]]
            acc = 1 if resp == m.answer_line_type else -1
            break

    help_line.setAutoDraw(False)
    matrix.set_auto_draw(False)
    window.flip()
    time.sleep(config['JITTER_TIME'])

    return acc, rt, stim_time, m.n, m.answer_line_type


config = load_config()

SCREEN_RES = get_screen_res()
window = visual.Window(SCREEN_RES, fullscr=True, monitor='testMonitor', units='pix',
                       screen=0, color='Gainsboro', winType='pygame')
FRAMES_PER_SEC = get_frame_rate(window)
mouse = event.Mouse(visible=False)

help_text = "wiersz" + " " * 15 + "kolumna" + " " * 15 + "przekątna"  # + " " * 15 + "no"
help_line = visual.TextStim(win=window, antialias=True, font=u'Arial',
                            text=help_text, height=config['TEXT_SIZE'],
                            wrapWidth=SCREEN_RES[0], color=u'black',
                            pos=(0, -300))
clock_image = visual.ImageStim(win=window, image=join('images', 'clock.png'), interpolate=True,
                               size=config['CLOCK_SIZE'], pos=config['CLOCK_POS'])

response_clock = core.Clock()

# TRAINING
# show_info(window, join('.', 'messages', "instruction1.txt"),text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
show_image(window, 'instruction.png', SCREEN_RES)

i = 1
for elem in config['TRAINING_TRIALS']:
    print(elem)
    for trail in range(elem['n_trails']):
        acc, rt, stim_time, n, answer_line_type = run_trial(n=elem['level'])
        RESULTS.append([i, 0, acc, rt, stim_time, n, 0, 0, answer_line_type])
        i += 1

# EXPERIMENT
show_info(window, join('.', 'messages', "instruction2.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])


experiment = NUpNDown(start_val=config['START_LEVEL'], max_revs=config['MAX_REVS'],
                      min_level=config["MIN_LEVEL"], max_level=config['MAX_LEVEL'])


old_rev_count_val = -1
for i, soa in enumerate(experiment, i):
    if i > config['MAX_TRIALS']:
        break
    acc, rt, stim_time, n, answer_line_type = run_trial(soa)
    level, reversal, revs_count = map(int, experiment.get_jump_status())
    if old_rev_count_val != revs_count:
        old_rev_count_val = revs_count
        rev_count_val = revs_count
    else:
        rev_count_val = '-'

    RESULTS.append([config['TRAINING_TRIALS'] + i, 1, acc, rt, stim_time, n, reversal, rev_count_val, answer_line_type])
    experiment.set_corr(acc)


show_info(window, join('.', 'messages', "end.txt"), text_size=config['TEXT_SIZE'], screen_width=SCREEN_RES[0])
