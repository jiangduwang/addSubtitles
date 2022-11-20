from flask import Flask, render_template, request, send_from_directory,redirect
import os
from transcribe import Transcribe
import argparse
from addSubtitles import RealizeAddSubtitles
#from gevent import pywsgi
parser = argparse.ArgumentParser(description='Edit videos based on transcribed subtitles',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('inputs', type=str, nargs='+',
                    help='Inputs filenames/folders')
parser.add_argument('--lang', type=str, default='zh',
                    choices=['zh', 'en'],
                    help='The output language of transcription')
parser.add_argument('--prompt', type=str, default='',
                    help='initial prompt feed into whisper')
parser.add_argument('--whisper-model', type=str, default='small',
                    choices=['tiny', 'base', 'small', 'medium', 'large'],
                    help='The whisper model used to transcribe.')
parser.add_argument('--vad', help='If or not use VAD',
                    action=argparse.BooleanOptionalAction)
parser.add_argument('--force', help='Force write even if files exist',
                    action=argparse.BooleanOptionalAction)
parser.add_argument('--encoding', type=str, default='utf-8',
                    help='Document encoding format')
parser.add_argument('--device', type=str, default=None,
                    choices=['cpu', 'cuda'],
                    help='Force to CPU or GPU for trascribing. In default automatically use GPU if available.')

app = Flask(__name__)
# 设置文件上传保存路径
app.config['UPLOAD_FOLDER'] = 'static/upload/'
# MAX_CONTENT_LENGTH设置上传文件的大小，单位字节
newvideo=""
# def add_subtitles(filename):
#     srt=filename.replace(".mp4",".srt")
#     newvideo=filename[:-4]+"_srt"+filename[-4:]
#     sim="autocut -t {} & ffmpeg -i {} -vf subtitles={} {}".format(filename,filename,srt,newvideo)
#     os.system(sim)

@app.route('/', methods=['GET', 'POST'])
def upload():
    global newvideo
    # 如果是get请求响应上传视图，post请求响应上传文件
    if(request.method == 'GET'):
        return render_template('upload.html');
    else:
        f = request.files['file'];
        # 生成一个uuid作为文件名
        fileName = f.filename;
        # os.path.join拼接地址，上传地址，f.filename获取文件名
        file_1=os.path.join(app.config['UPLOAD_FOLDER'], fileName)
        f.save(file_1)
        file = [file_1]
        args = parser.parse_args(file)
        Transcribe(args).run()
        srt = args.inputs[0].replace(".mp4", ".srt")
        RealizeAddSubtitles(args.inputs[0], srt)
        newvideo=fileName[:-4] + "_srt" + fileName[-4:]
        return redirect('/download')

# 图片下载
@app.route('/download', methods=['GET'])
def download():
    if request.method == "GET":
        filename=newvideo
        #通过文件名下载文件
        path = os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if path:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
   # server = pywsgi.WSGIServer(('0.0.0.0',80),app)
   # server.serve_forever()
   app.run(host='0.0.0.0',port=8081)
