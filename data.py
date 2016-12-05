import logging
import os
import shutil
import sys
import wave
from decimal import Decimal

from slugify import slugify

AUDIO_EXTS = ['.wav', '.mp3']

# initialize path and logger
CUR_DIR = os.path.dirname(os.path.realpath(__name__))
DATA_DIR = os.path.join(CUR_DIR, 'data/')
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def import_folder(path):
    """
    Import a flat folder into /data.
    Flat folder only contains speech files and no other subfolders.
    """
    for file_ in os.listdir(path):
        if os.path.splitext(file_)[1] in AUDIO_EXTS:
            file_path = os.path.join(path, file_)
            file_id = slugify(file_)
            working_dir = os.path.join(DATA_DIR, file_id + '/')
            raw_dir = os.path.join(working_dir, 'raw/')
            resampled_dir = os.path.join(working_dir, 'resampled/')
            diarize_dir = os.path.join(working_dir, 'diarization/')
            trans_dir = os.path.join(working_dir, 'transcript/')
            googleapi_dir = os.path.join(trans_dir, 'googleapi/')
            textgrid_dir = os.path.join(trans_dir, 'textgrid/')
            dir_list = [raw_dir, resampled_dir,
                        diarize_dir, trans_dir, googleapi_dir, textgrid_dir]
            for dir_ in dir_list:
                if not os.path.exists(dir_):
                    os.makedirs(dir_)
            shutil.copy2(file_path, raw_dir)
            LOG.info('Processed %s', file_id)


def clear_temp(path):
    """
    Clear all /temp folders from a path.
    Useful to prepare completed folder for long term storage.
    """
    # get list of folders that conforms to /data structure
    key = set(['raw', 'resampled', 'diarization', 'transcript', 'temp'])
    completed_dirs = set()
    for root, dirs, files in os.walk(path):
        if key.issubset(dirs):
            completed_dirs.add(root)

    for dir_ in completed_dirs:
        temp_dir = os.path.join(dir_, 'temp/')
        shutil.rmtree(temp_dir, ignore_errors=True)
        LOG.info('Processed %s', dir_)


def migrate(path):
    """
    Convert all folders in a path from old to new structure.
    Path must contain all folders with the old structure.
    """
    for dir_ in os.listdir(path):
        working_dir = os.path.join(path, dir_)
        resampled_dir = os.path.join(working_dir, 'resampled/')
        diarize_dir = os.path.join(working_dir, 'diarization/')
        trans_dir = os.path.join(working_dir, 'transcript/')
        googleapi_dir = os.path.join(trans_dir, 'googleapi/')
        textgrid_dir = os.path.join(trans_dir, 'textgrid/')

        old_resampled = os.path.join(resampled_dir, dir_ + '-resampled.wav')
        new_resampled = os.path.join(resampled_dir, dir_ + '.wav')
        old_diarize = os.path.join(diarize_dir, dir_ + '-diarize.seg')
        new_diarize = os.path.join(diarize_dir, dir_ + '.seg')
        old_trans = os.path.join(googleapi_dir, dir_ + '-diarize.txt')
        new_trans = os.path.join(googleapi_dir, dir_ + '.txt')
        old_textgrid = os.path.join(textgrid_dir, dir_ + '-diarize.TextGrid')
        new_textgrid = os.path.join(textgrid_dir, dir_ + '.TextGrid')

        if os.path.exists(old_resampled):
            os.rename(old_resampled, new_resampled)
        if os.path.exists(old_diarize):
            os.rename(old_diarize, new_diarize)
        if os.path.exists(old_trans):
            os.rename(old_trans, new_trans)
        if os.path.exists(old_textgrid):
            os.rename(old_textgrid, new_textgrid)

        LOG.info('Processed %s', dir_)


def stats(path):
    """
    Return some statistics for the folder.
    Useful for completion statistics.
    """
    # get list of folders that conforms to /data structure
    key = set(['raw', 'resampled', 'diarization', 'transcript'])
    completed_dirs = set()
    for root, dirs, files in os.walk(path):
        if key.issubset(dirs):
            completed_dirs.add(root)

    # get total time and no of file_ids processed
    count = 0
    time = Decimal(0)
    for dir_ in completed_dirs:
        resampled_dir = os.path.join(dir_, 'resampled/')
        if len(os.listdir(resampled_dir)) == 1:
            resampled_file = os.path.join(
                resampled_dir, os.listdir(resampled_dir)[0])
            file_ = wave.open(resampled_file, 'r')
            time += Decimal(file_.getnframes()) / file_.getframerate()
            file_.close()
            count += 1

    # convert to human readable times
    hours = int(time / 3600)
    time -= hours * 3600
    minutes = int(time / 60)
    seconds = time - minutes * 60

    LOG.info('Processed %s files, total time %s hours %s minutes %s seconds.',
             count, hours, minutes, seconds)


def print_completed(path):
    """
    Print a list of completed file_ids in a path.
    Useful to check /data.
    """
    # get list of folders that conforms to /data structure
    key = set(['raw', 'resampled', 'diarization', 'transcript'])
    completed_dirs = set()
    for root, dirs, files in os.walk(path):
        if key.issubset(dirs):
            completed_dirs.add(root)

    count = 0
    for dir_ in sorted(completed_dirs):
        textgrid_dir = os.path.join(dir_, 'transcript/textgrid')
        if len(os.listdir(textgrid_dir)) == 1:
            print dir_
            count += 1

    LOG.info('%s file_ids completed.', count)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        LOG.info('Invalid arguments. Exiting.')
    elif (sys.argv[1] in ['-i', '--import']):
        import_folder(sys.argv[2])
    elif (sys.argv[1] in ['-c', '--clear']):
        clear_temp(sys.argv[2])
    elif (sys.argv[1] in ['-m', '--migrate']):
        migrate(sys.argv[2])
    elif (sys.argv[1] in ['-s', '--stats']):
        stats(sys.argv[2])
    elif (sys.argv[1] in ['-p', '--print-completed']):
        print_completed(sys.argv[2])
    else:
        LOG.info('Invalid arguments. Exiting.')
