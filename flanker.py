import csv
import errno
import random
import sys
import os

import pygame

BLOCK_N = 2
TRIALS_N = 8

INSTR_SIZE = 50
ID_SIZE = 30
COUNT_SIZE = 80
ST_SIZE = 200
BGCOLOR = (0, 0, 0)
INSTRCOLOR = (255, 255, 255)
STCOLOR = (255, 255, 255)

START_DELAY = 1000
FIXED_DELAY = 1500
ENDING_DELAY = 2000
STIMULUS_DELAY = 1000
RESPONSE_DELAY = 3000

fps = 60

STIMULI_TYPE = ['>>>>>', '<<<<<', '<<><<', '>><>>']

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Flanker Task')
clock = pygame.time.Clock()

DISPLAY_WIDTH, DISPLAY_HEIGHT = screen.get_size()


def line_blit_surface(screen, text, font=None, size=50, color=(255, 255, 255)):                 ### 한 문장 출력
    textfont = pygame.font.Font(font, size)
    textsurf = textfont.render(text, True, color)
    screen.blit(textsurf, ((DISPLAY_WIDTH - textsurf.get_width()) // 2, (DISPLAY_HEIGHT - textsurf.get_height()) // 2))


def lines_blit_surface(screen, text, font=None, size=50, color=(255, 255, 255)):                ### 여러 문장 출력
    linesfont = pygame.font.Font(font, size)
    lines = text.splitlines()
    index = 0
    for line in lines:
        line_surf = linesfont.render(line, True, color)
        screen.blit(line_surf, ((DISPLAY_WIDTH - line_surf.get_width()) // 2,
                                (DISPLAY_HEIGHT - len(
                                    lines) * line_surf.get_height()) // 2 + index * line_surf.get_height()))
        index += 1


class BlockStimuli:                                                        ### 블록당 자극 생성
    def __init__(self):
        self.trials_stimuli = ['' for _ in range(TRIALS_N)]
        self.trials_corresponse = ['' for _ in range(TRIALS_N)]
        self.trials_condition = ['' for _ in range(TRIALS_N)]

    def set_stimuli(self):
        self.make_stimuli(0, {n for n in range(TRIALS_N)}, random.randint(0, len(STIMULI_TYPE) - 1))

    def make_stimuli(self, count, possible, type):
        if count == TRIALS_N:
            return True
        while True:
            if len(possible) == 0: return False

            tmpTrial = random.sample(possible, 1)[0]

            if not tmpTrial in possible:
                continue

            if self.trials_stimuli[tmpTrial] != '':
                possible.remove(tmpTrial)
                continue


            if tmpTrial > 2:
                if STIMULI_TYPE[type][2] == self.trials_corresponse[tmpTrial - 1] and STIMULI_TYPE[type][2] == \
                        self.trials_corresponse[tmpTrial - 2] and STIMULI_TYPE[type][2] == self.trials_corresponse[
                    tmpTrial - 3]:
                    possible.remove(tmpTrial)
                    continue
                if self.trials_condition[tmpTrial-1] == self.trials_condition[tmpTrial-2] == self.trials_condition[tmpTrial-3]:
                    if type < 2 and self.trials_condition[tmpTrial - 1] == 'con':
                        possible.remove(tmpTrial)
                        continue
                    elif type > 1 and self.trials_condition[tmpTrial - 1] == 'inc':
                        possible.remove(tmpTrial)
                        continue
            if 1 < tmpTrial < TRIALS_N - 1:
                if STIMULI_TYPE[type][2] == self.trials_corresponse[tmpTrial - 1] and STIMULI_TYPE[type][2] == \
                        self.trials_corresponse[tmpTrial - 2] and STIMULI_TYPE[type][2] == self.trials_corresponse[
                    tmpTrial + 1]:
                    possible.remove(tmpTrial)
                    continue
                if self.trials_condition[tmpTrial-1] == self.trials_condition[tmpTrial-2] == self.trials_condition[tmpTrial+1]:
                    if type < 2 and self.trials_condition[tmpTrial - 1] == 'con':
                        possible.remove(tmpTrial)
                        continue
                    elif type > 1 and self.trials_condition[tmpTrial - 1] == 'inc':
                        possible.remove(tmpTrial)
                        continue

            if 0 < tmpTrial < TRIALS_N - 2:
                if STIMULI_TYPE[type][2] == self.trials_corresponse[tmpTrial - 1] and STIMULI_TYPE[type][2] == \
                        self.trials_corresponse[tmpTrial + 1] and STIMULI_TYPE[type][2] == self.trials_corresponse[
                    tmpTrial + 2]:
                    possible.remove(tmpTrial)
                    continue
                if self.trials_condition[tmpTrial-1] == self.trials_condition[tmpTrial+1] == self.trials_condition[tmpTrial+2]:
                    if type < 2 and self.trials_condition[tmpTrial - 1] == 'con' :
                        possible.remove(tmpTrial)
                        continue
                    elif type > 1 and self.trials_condition[tmpTrial - 1] == 'inc' :
                        possible.remove(tmpTrial)
                        continue

            if tmpTrial < TRIALS_N - 3:
                if STIMULI_TYPE[type][2] == self.trials_corresponse[tmpTrial + 1] and STIMULI_TYPE[type][2] == \
                        self.trials_corresponse[tmpTrial + 2] and STIMULI_TYPE[type][2] == self.trials_corresponse[
                    tmpTrial + 3]:
                    possible.remove(tmpTrial)
                    continue
                if self.trials_condition[tmpTrial+1] == self.trials_condition[tmpTrial+2] == self.trials_condition[tmpTrial+3]:
                    if type < 2 and self.trials_condition[tmpTrial+1] == 'con':
                        possible.remove(tmpTrial)
                        continue
                    elif type > 1 and self.trials_condition[tmpTrial+1] == 'inc':
                        possible.remove(tmpTrial)
                        continue

            self.trials_stimuli[tmpTrial] = STIMULI_TYPE[type]

            if type == 0 or type == 2:
                self.trials_corresponse[tmpTrial] = '>'
            else:
                self.trials_corresponse[tmpTrial] = '<'
            if type == 0 or type == 1:
                self.trials_condition[tmpTrial] = 'con'
            else:
                self.trials_condition[tmpTrial] = 'inc'

            if self.make_stimuli(count + 1, {n for n in range(TRIALS_N)}, (type + 1) % len(STIMULI_TYPE)):
                return True
            self.trials_stimuli[tmpTrial] = ''
            self.trials_corresponse[tmpTrial] = ''
            self.trials_condition[tmpTrial] = ''

            possible.remove(tmpTrial)


### 시작 화면

screen.fill(BGCOLOR)
line_blit_surface(screen, "Flanker Task", size=INSTR_SIZE, color=INSTRCOLOR)
pygame.display.flip()
pygame.time.delay(START_DELAY)

### 참가자 순번 확인

try:
    if not(os.path.isdir('./data')):
        os.makedirs(os.path.join('./data'))
except OSError as e:
    if e.errno != errno.EEXIST:
        print("Failed to create directory!!!!!")
        raise

id_font = pygame.font.Font(None, 30)
id_surf = id_font.render('Participant number : ', True, INSTRCOLOR)
id_box = pygame.Rect((DISPLAY_WIDTH - 150) // 2, (DISPLAY_HEIGHT - 25) // 2, 150, 25)
id_used = 1

while id_used:
    finished = 0
    input_id = '999'
    while not finished:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                finished = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    finished = 1
                elif event.key == pygame.K_BACKSPACE:
                    input_id = input_id[:-1]
                elif event.unicode.isdecimal():
                    input_id += event.unicode

            screen.fill(BGCOLOR)

            screen.blit(id_surf, ((DISPLAY_WIDTH - id_surf.get_width()) // 2,
                                  (DISPLAY_HEIGHT - id_surf.get_height()) // 2 - int(id_surf.get_height() * 1.5)))
            pygame.draw.rect(screen, (255, 255, 255), id_box)
            line_blit_surface(screen, input_id, size=ID_SIZE, color=(0, 0, 0))
            pygame.display.flip()

    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        pygame.quit()
        sys.exit()

    filepath = './data/flanker_task_' + input_id + '.csv'
    if os.path.isfile(filepath):
        screen.fill(BGCOLOR)
        NtBlock_TEXT = "This id number is used previously.\nPlease, check the number"
        lines_blit_surface(screen, NtBlock_TEXT, size=ID_SIZE, color=INSTRCOLOR)
        pygame.display.flip()

        finished = 0
        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    finished = 1
    else:
        id_used = 0

id_file = open(filepath, 'w', newline='')
fieldnames = ['block', 'trial', 'stimuli', 'condition', 'corr', 'resp', 'acc', 'rt']
writer = csv.DictWriter(id_file, fieldnames=fieldnames)
writer.writeheader()


### 지시문 출력


pygame.event.get()
screen.fill(BGCOLOR)
INSTRUCTION_TEXT = "Press the key that matches the Target in the CENTER\ntry to ignore all other arrows.\n\
Press on Z if the target is < \nPress on M if the target is >.\n\nPress the SPACEBAR to start the test."

lines_blit_surface(screen, INSTRUCTION_TEXT, size=INSTR_SIZE, color=INSTRCOLOR)
pygame.display.flip()

finished = 0
while not finished:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            finished = 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            finished = 1

if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
    pygame.quit()
    sys.exit()

### 준비시간 카운트다운 5초


finished = 0
tm = 0
clock.tick(0)
while not finished:
    screen.fill(BGCOLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            finished = 1

    if tm >= 5000:
        finished = 1
    line_blit_surface(screen, str(5 - (tm // 1000)), font=None, size=COUNT_SIZE, color=INSTRCOLOR)
    pygame.display.flip()
    clock.tick(fps)
    tm += clock.get_time()

if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
    pygame.quit()
    sys.exit()

### 실험 시작 - 고정점


for block_n in range(BLOCK_N):
    blockStimuli = BlockStimuli()
    blockStimuli.set_stimuli()

    for trial_n in range(TRIALS_N):
        key, rt = '', -1
        screen.fill(BGCOLOR)

        pygame.draw.line(screen, INSTRCOLOR,
                         (DISPLAY_WIDTH // 2 - 5, DISPLAY_HEIGHT // 2), (DISPLAY_WIDTH // 2 + 5, DISPLAY_HEIGHT // 2))
        pygame.draw.line(screen, INSTRCOLOR,
                         (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 5), (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 5))

        pygame.display.flip()

        pygame.time.delay(FIXED_DELAY)

        screen.fill(BGCOLOR)
        line_blit_surface(screen, blockStimuli.trials_stimuli[trial_n], font=None, size=ST_SIZE, color=STCOLOR)
        pygame.display.flip()

        ### 실험 - 자극 제시

        finished = 0
        tm = 0
        pygame.event.get()
        clock.tick(0)
        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and (event.key == pygame.K_z or event.key == pygame.K_m):
                    if event.key == pygame.K_z:
                        key, rt = '<', tm
                    else:
                        key, rt = '>', tm
                    finished = 1
                    break

            if tm >= STIMULUS_DELAY:
                break
            clock.tick(fps)
            tm += clock.get_time()

        screen.fill(BGCOLOR)
        pygame.display.flip()

        ### 실험 자극 철회, 반응 대기

        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and (event.key == pygame.K_z or event.key == pygame.K_m):
                    if event.key == pygame.K_z:
                        key, rt = '<', tm
                    else:
                        key, rt = '>', tm
                    finished = 1
                    break

            if tm >= STIMULUS_DELAY + RESPONSE_DELAY:
                finished = 1
            clock.tick(fps)
            tm += clock.get_time()

        if blockStimuli.trials_corresponse[trial_n] == key:
            writer.writerow(
                {'block': block_n + 1, 'trial': trial_n + 1, 'stimuli': blockStimuli.trials_stimuli[trial_n],
                 'condition': blockStimuli.trials_condition[trial_n],
                 'corr': blockStimuli.trials_corresponse[trial_n], 'acc': 'O', 'resp': key, 'rt': rt})
        else:
            writer.writerow(
                {'block': block_n + 1, 'trial': trial_n + 1, 'stimuli': blockStimuli.trials_stimuli[trial_n],
                 'condition': blockStimuli.trials_condition[trial_n],
                 'corr': blockStimuli.trials_corresponse[trial_n], 'acc': 'X', 'resp': key, 'rt': rt})

    ### 블럭 종료, 다음 블럭 준비

    if block_n < BLOCK_N - 1:
        screen.fill(BGCOLOR)
        NtBlock_TEXT = "Short break\nThat was block : " + str(block_n + 1) + \
                       "\nPress the SPACEBAR to start the Next block."
        lines_blit_surface(screen, NtBlock_TEXT, size=INSTR_SIZE, color=INSTRCOLOR)
        pygame.display.flip()

        finished = 0
        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    finished = 1

###


screen.fill(BGCOLOR)
line_blit_surface(screen, 'Thank you!!!', size=INSTR_SIZE, color=INSTRCOLOR)
pygame.display.flip()

pygame.time.delay(ENDING_DELAY)

pygame.quit()
sys.exit()
