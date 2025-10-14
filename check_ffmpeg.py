from pydub import AudioSegment
import utils.audio_utils as au
print('AudioSegment.converter ->', getattr(AudioSegment, 'converter', None))
print('AudioSegment.ffprobe ->', getattr(AudioSegment, 'ffprobe', None))
try:
    import imageio_ffmpeg
    print('imageio_ffmpeg available:', imageio_ffmpeg.get_ffmpeg_exe())
except Exception as e:
    print('imageio_ffmpeg not available:', e)
