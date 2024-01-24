import asyncio
from datetime import timedelta
from pydub import AudioSegment
from shazamio import Shazam, Serialize

file = "10.mp3" # file to be processed
segment_length = 20 * 1000 # length (ms) of sample to be sent to Shazam
segment_overlap = 3 * 1000 # length (ms) of overlap to have between samples

def print_info(data):
    if "title" not in data:
        return
    if data["title"] is None:
        info = "Unknown"
    else:
        info = f"{data['title']:<60} || {data['artist']:<60} || {data['spotify_url']}"
    prefix = f"{data['index']:>3} || {timedelta(seconds=data['start']//1000)} - {timedelta(seconds=data['end']//1000)} || "
    print(prefix + info)

async def main():
    shazam = Shazam()
    # out = await shazam.recognize_song(file)
    audio = AudioSegment.from_file(file)
    total_duration = int(audio.duration_seconds // 1)
    print("File loaded!")
    print('\tDuration:', timedelta(seconds=total_duration))
    print('\tSample rate:', audio.frame_rate)
    print('\tChannels:', audio.channels)

    segment_intervals = []
    start = 0
    while start + segment_length <= total_duration * 1000:
        end = start + segment_length
        segment_intervals.append((start, end))
        start = end - segment_overlap
    print("Total intervals:", len(segment_intervals))
    print()

    prev_song = None
    data = dict()
    index = 0
    for itr, (start, end) in enumerate(segment_intervals):
        # print(f"{itr + 1}: {timedelta(seconds=start//1000)}-{timedelta(seconds=end//1000)}")

        segment = audio[start:end]

        out = await shazam.recognize_song(segment)
        serialized = Serialize.full_track(out)

        if serialized.track is None:
            title = None
        else:
            title = serialized.track.title

        if title != prev_song:
            print_info(data)
            data = dict()
            index += 1
            data["start"] = start
            # data["end"] = end
            data["index"] = index
            data["title"] = title
            if title is not None:
                data["artist"] = serialized.track.subtitle
                data["spotify_url"] = f"https://open.spotify.com/search/{serialized.track.spotify_url.split(':')[-1]}"
        prev_song = title
        data["end"] = end
    print_info(data)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())