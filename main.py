from flask import Flask, request, render_template, redirect,url_for,make_response,send_from_directory,flash
from gevent import pywsgi
import os,  _thread
from func import *

# 文件上传的地址
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#限制最大上传文件为 60 Mb
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/pdf2img', methods=['GET', 'POST'])
def pdf2img():
    if request.method == 'POST':
        print("Page pdf2img, Mode POST")
        file = request.files['file']
        filename = file.filename.rsplit('.', 1)[0]
        filetype = file.filename.rsplit('.', 1)[1]
        if filetype=="pdf":
            filename += str(time.time())
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','_') # 去除文件中的.
            filename = filename.replace('-','_') 
            pdfpath = os.path.join(app.config['UPLOAD_FOLDER'], filename+'.'+filetype)
            file.save(pdfpath)
            PDF2IMG(pdfpath,app.config['UPLOAD_FOLDER'],5)
            writelog("log.txt", "Transfer sucess.")
            os.remove(pdfpath)
            return download("%s.zip" % filename)
        else:
            return redirect(url_for('pdf2img'))
    else: # Get
        return render_template('upload.html')

@app.route('/pdfmerge', methods=['GET', 'POST'])
def pdfmerge():
    if request.method == 'POST':
        writelog("log.txt", "Page pdfmerge, Mode POST")
        file = request.files['file']
        filename = file.filename.rsplit('.', 1)[0]
        filetype = file.filename.rsplit('.', 1)[1]
        if filetype=="zip":
            filename += str(time.time())
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','_') # 去除文件中的.
            filename = filename.replace('-','_') 
            zippath = os.path.join(app.config['UPLOAD_FOLDER'], filename+'.'+filetype)
            file.save(zippath)
            rtnfrommgpdf = MERGEPDF(zippath)
            os.remove(zippath)
            if rtnfrommgpdf==1:
                writelog("log.txt", "Merge sucess.")
                return download("%s.pdf" % filename)
            else:
                writelog("log.txt", "Merge failed.")
                return redirect(url_for('pdfmerge'))
        else:
            return redirect(url_for('pdfmerge'))
    else: # Get
        return render_template('upload.html')

@app.route('/heic2jpg', methods=['GET', 'POST'])
def heic2jpg():
    if request.method == 'POST':
        writelog("log.txt", "Page heic2jpg, Mode POST")
        file = request.files['file']
        filename = file.filename.rsplit('.', 1)[0]
        filetype = file.filename.rsplit('.', 1)[1]
        if filetype=="heic" or filetype=="HEIC" or filetype=="heif" or filetype=="HEIF":
            filename += str(time.time())
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','_') # 去除文件中的.
            filename = filename.replace('-','_') 
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename+'.'+filetype)
            file.save(imgpath)
            token = HEIC2JPG(imgpath, os.path.join(app.config['UPLOAD_FOLDER'], filename+'.jpg'))
            os.remove(imgpath)
            if token==1:
                writelog("log.txt", "Transfer HEIF -> JPG sucess.")
                return download("%s.jpg" % filename)
            else:
                writelog("log.txt", "Transfer HEIF -> JPG failed.")
                return redirect(url_for('heic2jpg'))
        else:
            return redirect(url_for('heic2jpg'))
    else: # Get
        return render_template('upload.html')

@app.route('/imgcpr', methods=['GET', 'POST'])
def imgcpr():
    if request.method == 'POST':
        writelog("log.txt", "Page img compress, Mode POST")
        mode = request.form.get('mode')
        file = request.files['file']
        filename = file.filename.rsplit('.', 1)[0]
        filetype = file.filename.rsplit('.', 1)[1]
        safelist = ["jpg", "JPG", "PNG", "png", "jpeg", "JPEG"]
        if filetype in safelist:
            filename += str(time.time())
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','_') # 去除文件中的.
            filename = filename.replace('-','_') 
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename+'.'+filetype)
            file.save(imgpath)
            token = COMPRESSIMG(imgpath, mode)
            if token==1:
                writelog("log.txt", "IMG Compress sucess.")
                return download("%s.%s" % (filename,filetype))
            else:
                writelog("log.txt", "IMG Compress failed.")
                return redirect(url_for('imgcpr'))
        else:
            return redirect(url_for('imgcpr'))
    else: # Get
        return render_template('imgcpr.html')

@app.route('/imgsr', methods=['GET', 'POST'])
def imgsr():
    if request.method == 'POST':
        writelog("log.txt", "Page img sr, Mode POST")
        mode = request.form.get('mode')
        scale = int(request.form.get('scale'))
        file = request.files['file']
        filename = file.filename.rsplit('.', 1)[0]
        filetype = file.filename.rsplit('.', 1)[1]
        safelist = ["jpg", "JPG", "PNG", "png", "jpeg", "JPEG"]
        if filetype in safelist:
            filename += str(time.time())
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','_') # 去除文件中的.
            filename = filename.replace('-','_') 
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], filename+'.'+filetype)
            file.save(imgpath)
            token = IMGSR(imgpath, mode, scale)
            if token==1:
                writelog("log.txt", "IMG SR sucess.")
                return download("%s.%s" % (filename,filetype))
            else:
                writelog("log.txt", "IMG SR failed.")
                return redirect(url_for('imgsr'))
        else:
            return redirect(url_for('imgsr'))
    else: # Get
        return render_template('imgsr.html')



@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = app.config['UPLOAD_FOLDER']  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response

if __name__ == '__main__':
    _thread.start_new_thread(clear, (app.config['UPLOAD_FOLDER'], 60, ) )
    # https://blog.csdn.net/qq_41427568/article/details/101025193
    # app.run(host='0.0.0.0', threaded=True, port=7050) #, debug=True)
    server = pywsgi.WSGIServer(('0.0.0.0', 7050), app)
    server.serve_forever()