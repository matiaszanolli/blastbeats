# BLAST BEATS: Multiformat audio player with remastering on the go.
# 2022 Matías Zanolli / Tech For Music
# Just Because.
import queue
import sys
import threading

from matchering_mini import processor
import matchering
import librosa
import ffmpegio
import sounddevice as sd
from argparse import ArgumentParser

CHUNK_SIZE = 65536
# q = queue.Queue(maxsize=16384)
MATCH_SAMPLE, MATCH_SR = librosa.load('samples/crow2.wav', mono=False)


def parse_args():
    parser = ArgumentParser(
        description="Simple Matchering 2.0 Command Line Application"
    )
    parser.add_argument("track", type=str, help="The track you want to play")

    parser.add_argument(
        '-b', '--blocksize', type=int, default=65536,
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
    if len(streams) != 1:
        parser.exit(1, 'There must be exactly one stream available')

    stream_data = streams[0]

    if stream_data.get('codec_type') != 'audio':
        parser.exit(1, 'The stream must be an audio stream')

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
            x = processor.main(data, MATCH_SAMPLE.transpose(1, 0).astype('float32'), matchering.core.Config())[
                0].copy(order='C').astype('float32')
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
        with ffmpegio.open(audio_file) as file:
            print('Playing ...')
            stream = sd.RawOutputStream(samplerate=samplerate,
                                        channels=channels,
                                        callback=callback,
                                        blocksize=CHUNK_SIZE,
                                        finished_callback=event.set)
            with stream:
                event.wait()
            # with sd.OutputStream(
            #         samplerate=samplerate, blocksize=args.blocksize,
            #         dtype='float32',
            #         callback=callback, finished_callback=event.set):
            #     while True:
            #         print('Reading ...')
            #         data = stream.read(CHUNK_SIZE)
            #         timeout = args.blocksize * args.buffersize * 2 / samplerate
            #         if len(data) < CHUNK_SIZE:
            #             break
            #         q.put(data, timeout=timeout)
            #     with stream:
            #         event.wait()

    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')
    except queue.Full:
        # A timeout occurred, i.e. there was an error in the callback
        sys.exit('QUEUE FULL')
    except Exception as e:
        sys.exit(type(e).__name__ + ': ' + str(e))


def run(args, strm):
    new_thread = threading.Thread(target=play, args=(args, strm))
    new_thread.start()


if __name__ == '__main__':
    args, stream = parse_args()
    run(args, stream)
