from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import cv2
import mediapipe as mp
import urllib.request as urllib
import numpy as np
import urllib.request
import ssl



class VideoEditor:

    @classmethod
    def trim(cls, filename, target_name, start_time, end_time):
        ffmpeg_extract_subclip(filename=filename, t1=start_time, t2=end_time, targetname=target_name)
        return target_name

    @classmethod
    def add_text(cls, filename, start_time, end_time, text, target_name, h, w):
        video = VideoFileClip(filename)

        # Make the text. Many more options are available.
        txt_clip = (TextClip(text).set_position((w, h))
                    .set_duration(end_time - start_time)
                    .set_start(start_time))
        result = CompositeVideoClip([video, txt_clip])  # Overlay text on video
        result.write_videofile(target_name, fps=25, codec="libx264")
        return target_name

    @classmethod
    def add_text_to_video_object(cls, video_obj, start_time, end_time, text, h, w, font_size, color, font):
        """
        saprate function to add text in a video object
        """
        # Make the text. Many more options are available.
        txt_clip = (TextClip(text, fontsize=font_size, color=color, font=font).set_position((w, h))
                    .set_duration(end_time - start_time)
                    .set_start(start_time))
        result = CompositeVideoClip([video_obj, txt_clip])
        return result

    @classmethod
    def add_audio(cls, video_file, audio_file, target_name, volume, start_time, end_time):

        video = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)

        # Set volume of the audio
        audio_clip = volumex(audio_clip, volume)
        audioclip = AudioFileClip(video_file)
        audio_clip = audio_clip.set_duration(end_time - start_time).set_start(start_time)
        audioclip = audioclip

        new_audio = CompositeAudioClip([audioclip,
                                        audio_clip.set_start(start_time).volumex(volume)])

        # Set start time and duration of the audio
        video = video.set_audio(new_audio)
        video.write_videofile(target_name, fps=25, codec="libx264")

        return target_name

        '''
        Complete muting the vedio chunk and overlaping the audio
        '''
        # video = VideoFileClip(video_file)
        # audioclip = AudioFileClip(audio_file)
        # audioclip = volumex(audioclip, volume)
        # v_duration = video.duration
        # v1 = video.subclip(0, start_time)
        # v2 = video.subclip(start_time, end_time)
        # if int(end_time) != int(v_duration):
        #     v3 = video.subclip(end_time, v_duration)
        # v2 = v2.without_audio()
        # v2 = v2.set_audio(audioclip)
        #
        # if int(end_time) != int(v_duration):
        #     final = concatenate_videoclips([v1, v2, v3])
        # else:
        #     final = concatenate_videoclips([v1, v2])
        # final.write_videofile(target_name)
        # return target_name

    @classmethod
    def concat_video(cls):
        pass

    @classmethod
    def change_bg(cls, video_filename, target_name, bg_image):

        # segmentor = SelfiSegmentation()
        # fpsReader = cvzone.FPS()

        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

        context = ssl._create_unverified_context()
        resp = urllib.request.urlopen(bg_image, context=context)
        resp_byte_array = resp.read()
        mutable_byte_array = bytearray(resp_byte_array)
        imgBG = np.asarray(mutable_byte_array, dtype="uint8")
        imgBG = cv2.imdecode(imgBG, cv2.IMREAD_COLOR)
        # imgBG = cv2.imread(bg_image)

        # read video file
        cap = cv2.VideoCapture(video_filename)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (width, height)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # result = cv2.VideoWriter(target_name, cv2.VideoWriter_fourcc(*'FMP4'), fps, size)
        # fourcc = cv2.VideoWriter_fourcc(*'MKV')
        # result = cv2.VideoWriter(target_name, fourcc, fps, size)
        result = cv2.VideoWriter(target_name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
        success = True
        while success:
            success, img = cap.read()
            # flip the frame to horizontal direction
            if success:
                frame = cv2.flip(img, 1)
                height, width, channel = frame.shape
                RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # get the result
                results = selfie_segmentation.process(RGB)
                # extract segmented mask
                # mask = results.segmentation_mask
                condition = np.stack(
                    (results.segmentation_mask,) * 3, axis=-1) > 0.5
                # resize the background image to the same size of the original frame
                bg_image = cv2.resize(imgBG, (width, height))
                # combine frame and background image using the condition
                output_image = np.where(condition, frame, bg_image)
                result.write(output_image)

        result.release()
        return target_name

    @classmethod
    def black_n_white(cls, filename, target_name):
        video = VideoFileClip(filename)
        video = video.fx(blackwhite)
        # result = CompositeVideoClip([video])
        video.write_videofile(target_name, fps=25, codec="libx264")
        return target_name

    @classmethod
    def crop(cls, video_file, target_name, x, y, h, w):

        # read video file
        cap = cv2.VideoCapture(video_file)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # size = (width, height)
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # Output file
        # result = cv2.VideoWriter(target_name, cv2.VideoWriter_fourcc(*'FMP4'), fps, size)
        # x, y, h, w = 0, 0, 200, 200
        result = cv2.VideoWriter(target_name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, (w, h))
        success = True
        while success:
            success, frame = cap.read()
            if success:
                crop_frame = frame[y:y + h, x:x + w]
                result.write(crop_frame)
        result.release()
        return target_name

    @classmethod
    def save_video(cls, video, target_name):
        video.write_videofile(target_name, fps=25, codec="libx264")
        return target_name

    @classmethod
    def get_video_object_from_url(cls, filename):
        video = VideoFileClip(filename)
        return video
