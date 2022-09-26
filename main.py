# BLAST BEATS: Multiformat audio player with remastering on the go.
# 2022 Matías Zanolli / Tech For Music
# Just Because.
import queue
import sys
import threading
import traceback

import numpy as np
import matchering
from matchering.stage_helpers.match_levels import get_rms_c_and_amplify_pair
import librosa
import ffmpegio
import sounddevice as sd
from argparse import ArgumentParser

from matchering_mini import processor
from gui import GUI

CHUNK_SIZE = 32768
# q = queue.Queue(maxsize=16384)
MATCH_SAMPLE, MATCH_SR = librosa.load('samples/crow3.wav', mono=False)


def parse_args():
    parser = ArgumentParser(
        description="Simple Matchering 2.0 Command Line Application"
    )
    parser.add_argument("track", type=str, help="The track you want to play")

    parser.add_argument(
        '-b', '--blocksize', type=int, default=CHUNK_SIZE,
        help='block size (default: %(default)s)')

    parser.add_argument(
        '-q', '--buffersize', type=int, default=5000,
        help='number of blocks used for buffering (default: %(default)s)')

    args = parser.parse_args()

    try:
        info = ffmpegio.probe.full_details(args.track)
    except ffmpegio.FFmpegError as e:
        sys.stderr.buffer.write(e.ffmpeg_msg)
        parser.exit(e.ffmpeg_msg)

    streams = info.get('streams', [])
    streams = [strm for strm in streams if strm['codec_type'] == 'audio']
    if len(streams) != 1:
        parser.exit(1, 'There must be exactly one audio stream available')

    stream_data = streams[0]

    return args, stream_data


def play(args, strm):
    event = threading.Event()

    def callback(outdata, frames, time, status):
        assert frames == args.blocksize
        if status.output_underflow:
            print('Output underflow: increase blocksize?', file=sys.stderr)
            raise sd.CallbackAbort
        assert not status
        try:
            data = file.read(frames).astype('float32')
            if not len(data):
                print('Buffer is empty: increase buffersize?', file=sys.stderr)
                raise sd.CallbackAbort
            # print(data)
            # data = np.hstack((data[0].reshape(-1, 1), data[1].reshape(-1, 1)))
            x = processor.main(
                data,
                reference.transpose(1, 0).astype('float32'),
                matchering.core.Config(),
                need_default=True,
                _target_mid_loudest_pieces=mid_loudest_pieces,
                _target_side_loudest_pieces=side_loudest_pieces,
                _reference_match_rms=reference_match_rms,
                _target_rms=match_rms,
                _rms_coefficient=rms_coefficient,
                _final_amplitude_coefficient=final_amplitude_coefficient
            )[0].copy(order='C').astype('float32')
            outdata[:] = x
        except queue.Empty as e:
            print('Buffer is empty: increase buffersize?', file=sys.stderr)
            raise sd.CallbackAbort from e

    print('Getting stream information ...')

    channels = strm['channels']
    samplerate = float(strm['sample_rate'])

    audio_file = args.track
    try:
        print('Opening stream ...')
        sr, full_audio = ffmpegio.audio.read(audio_file)
        arr = full_audio.astype('float32')
        (
            mid,
            side,
            mid_loudest_pieces,
            side_loudest_pieces,
            match_rms,
            divisions,
            piece_size,
        ) = processor.analyze_levels(arr, 'whole_input', matchering.core.Config())

        (
            reference_mid,
            reference_side,
            reference_mid_loudest_pieces,
            reference_side_loudest_pieces,
            reference_match_rms,
            *_,
        ) = processor.analyze_levels(MATCH_SAMPLE, "reference", matchering.core.Config())

        (
            rms_coefficient,
            array_main,
            array_additional
        ) = get_rms_c_and_amplify_pair(
            mid,
            side,
            match_rms,
            reference_match_rms,
            matchering.core.Config().min_value,
            'rms'
        )

        reference, final_amplitude_coefficient = processor.normalize_reference(MATCH_SAMPLE, matchering.core.Config())

        with ffmpegio.open(audio_file, mode='a') as file:
            print('Playing ...')
            stream = sd.RawOutputStream(samplerate=samplerate,
                                        channels=channels,
                                        callback=callback,
                                        blocksize=CHUNK_SIZE,
                                        finished_callback=event.set)
            with stream:
                event.wait()

    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')
    except queue.Full:
        # A timeout occurred, i.e. there was an error in the callback
        sys.exit('QUEUE FULL')
    except Exception as e:
        traceback.print_exc()


def run(args, strm):
    new_thread = threading.Thread(target=play, args=(args, strm))
    new_thread.start()


if __name__ == '__main__':
    args, stream = parse_args()
    GUI(run, args, stream)
