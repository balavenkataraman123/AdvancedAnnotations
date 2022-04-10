from flask import Flask, render_template, Response, request, send_file
from PIL import Image, ImageGrab
import base64
from io import BytesIO
import win32clipboard as clp
import os
import cv2
app = Flask(__name__)



@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        data_url = request.values.get('image')
        content = data_url.split(';')[1]
        im_b64 = content.split(',')[1]
        im_bytes = base64.b64decode(im_b64)
    
    imgdata = base64.b64decode(im_b64)
    filename = 'some_image.png'

    with open(filename, 'wb') as f:
        f.write(imgdata)

    file_path = 'some_image.png'

    clp.OpenClipboard()
    clp.EmptyClipboard()

    # This works for Discord, but not for Paint.NET:
    wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
    clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
    clp.CloseClipboard()
@app.route('/annotate', methods = ['GET','POST'])
def index1():
    if request.method == 'GET':
        return render_template('annotate.html')
    elif request.method == 'POST':
        data_url = request.values.get('image')
        content = data_url.split(';')[1]
        im_b64 = content.split(',')[1]
        im_bytes = base64.b64decode(im_b64)
    
    imgdata = base64.b64decode(im_b64)
    filename = 'some_image.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    file_path = 'some_image.png'
    
    background = cv2.imread("imres.png", cv2.IMREAD_UNCHANGED)
    background = cv2.cvtColor(background, cv2.COLOR_RGB2RGBA)
    foreground = cv2.imread("some_image.png", cv2.IMREAD_UNCHANGED)

    # normalize alpha channels from 0-255 to 0-1
    alpha_background = background[:,:,3] / 255.0
    alpha_foreground = foreground[:,:,3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        background[:,:,color] = alpha_foreground * foreground[:,:,color] + \
            alpha_background * background[:,:,color] * (1 - alpha_foreground)

    # set adjusted alpha and denormalize back to 0-255
    background[:,:,3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255
    print('background')
    print(background)
    
    cv2.imshow("Composited image", background)
    cv2.waitKey(0)    
    
    cv2.imwrite(file_path, background)
    clp.OpenClipboard()
    clp.EmptyClipboard()    

    # This works for Discord, but not for Paint.NET:
    wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
    clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
    clp.CloseClipboard()    
@app.route("/image", methods = ['POST'])
def retimage():
    height = int(request.values.get('height'))
    width = int(request.values.get('width'))
    im = ImageGrab.grabclipboard()
    im.save('somefile.png','PNG')    
    img = cv2.imread('somefile.png')
    print(img.shape)
    dim = (width, height)
    print(dim)
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    cv2.imwrite('imres.png', img)
    encoded = base64.b64encode(open("imres.png", "rb").read())    
    
    return encoded




if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)