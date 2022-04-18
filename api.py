from urllib.parse import urlparse

from flask import Flask, request
import json
import datetime
from aws_s3_helpers import upload_file_to_s3, signed_url
from video_editor import VideoEditor
import os

app = Flask(__name__)


@app.route('/', methods=['POST'])
def edit_video():
    url = ""
    # trim the video
    if 'trim' in request.form:
        params = json.loads(request.form['trim'])
        f_name = urlparse(params['video_url'])
        f_name = os.path.basename(f_name.path)
        # input_url = params['url']
        # input_url = signed_url(input_url, directory="videos")
        filename = VideoEditor.trim(filename=params['video_url'],
                                    target_name="videos/output/edited-{}.mp4".format(datetime.datetime.now()),
                                    start_time=params["start_time"],
                                    end_time=params["end_time"])
        url = upload_file_to_s3(file=filename, f_name=f_name)
        os.remove(filename)

    if "audio" in request.form:
        params = json.loads(request.form['audio'])
        video_file = params['video_url']
        f_name = urlparse(video_file)
        f_name = os.path.basename(f_name.path)
        for audio in params['audios']:
            filename = VideoEditor.add_audio(video_file=video_file,
                                             audio_file=audio['audio_url'],
                                             target_name='videos/output/edited_audio-{}.mp4'.format(
                                                 datetime.datetime.now()),
                                             volume=audio['volume'],
                                             start_time=audio['start_time'],
                                             end_time=audio['end_time'])
            video_file = filename
        url = upload_file_to_s3(file=filename, f_name=f_name)
        os.remove(filename)

    if "change_bg" in request.form:
        params = json.loads(request.form['change_bg'])
        f_name = urlparse(params['video_url'])
        f_name = os.path.basename(f_name.path)
        filename = VideoEditor.change_bg(video_filename=params['video_url'],
                                         target_name='videos/output/edited_bg-{}.mp4'.format(datetime.datetime.now()),
                                         bg_image=params['bg_image_url'])
        url = upload_file_to_s3(file=filename, f_name=f_name)
        os.remove(filename)

    if "filters" in request.form:
        params = json.loads(request.form['filters'])
        f_name = urlparse(params['video_url'])
        f_name = os.path.basename(f_name.path)
        filename = VideoEditor.black_n_white(filename=params['video_url'],
                                             target_name='videos/output/edited_b-w-{}.mp4'.format(
                                                 datetime.datetime.now()))
        url = upload_file_to_s3(file=filename,f_name=f_name)
        os.remove(filename)

    if "crop" in request.form:
        params = json.loads(request.form['crop'])
        f_name = urlparse(params['video_url'])
        f_name = os.path.basename(f_name.path)
        filename = VideoEditor.crop(video_file=params['video_url'],
                                    target_name='videos/output/edited_crop-{}.mp4'.format(datetime.datetime.now()),
                                    x=params['coords'][0], y=params['coords'][1], h=params['coords'][2],
                                    w=params['coords'][3])
        url = upload_file_to_s3(filename,f_name=f_name)
        os.remove(filename)

    if "text" in request.form:
        params = json.loads(request.form['text'])
        f_name = urlparse(params['video_url'])
        f_name = os.path.basename(f_name.path)
        # paths = "videos/1.mkv"
        video = VideoEditor.get_video_object_from_url(filename=params['video_url'])
        # video = VideoEditor.get_video_object_from_url(filename=paths)
        # clip = video.subclip(30)
        for text in params['texts']:
            video = VideoEditor.add_text_to_video_object(video_obj=video,
                                                         start_time=text['start_time'],
                                                         end_time=text['end_time'],
                                                         text=text['text'],
                                                         h=text['height'], w=text['width'],
                                                         font_size=text["font_size"], color=text["color"],
                                                         font=text["font"])
        filename = VideoEditor.save_video(video=video,
                                          target_name="videos/output/edited_text-{}.mp4".format(
                                              datetime.datetime.now()))
        url = upload_file_to_s3(filename,f_name=f_name)
        os.remove(filename)

    return {
        "success": True,
        "message": "Video has been edited Successfully",
        "output_video_url": url
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
