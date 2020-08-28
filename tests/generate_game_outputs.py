import sys, os
sys.path.append(os.path.join('..', 'levels'))
import matplotlib.pyplot as plt

"""
Can run `generate_level_output(level=x)` to play the game and save the output as files in `game_outputs` folder.
This data can then be processed and tested using `test_game_outputs`.

The files are indexed by a variable #x. If e.g. file #1 exists then the new file will be labelled by #2 etc.
"""

dir_name = 'game_outputs'
if not os.path.exists(dir_name):
    os.makedirs(dir_name)


def generate_level_output(level=1):
    level_class = getattr(__import__("level_{}".format(level), fromlist=["Level{}".format(level)]), "Level{}".format(level))

    level_filename = 'test_level_{}'.format(level)
    filenames = os.listdir(dir_name)
    x = 1
    while [f for f in filenames if level_filename + '_#{}'.format(x) in f]:  # is not empty
        x += 1

    g = level_class(output_filename=level_filename + '_#{}'.format(x), output_dir='game_outputs')
    plt.show()


if __name__ == '__main__':
    generate_level_output(level=8)
