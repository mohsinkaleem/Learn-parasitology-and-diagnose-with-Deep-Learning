from flask import Flask,request,render_template,abort, redirect, url_for
from werkzeug.utils import secure_filename
import io
from PIL import Image
import torch
import numpy as np
import torch.nn as nn
from model import DNN1

check=torch.load("checkpoint")
model=DNN1("./resnet",check["dataset"]["nclasses"],check["dataset"]["labels"])
augment=check["transform"]["basic"]
encoder=check["dataset"]["encoder"]
model.load_state_dict(check["parameters"])
del check
model.eval()
print("here we go on")

app = Flask(__name__)
UPLOAD_FOLDER = "./static"
# app.secret_key = "mohsin30"
# app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MAX_IMAGE_FILESIZE"] = 3 * 1024 * 1024
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def transform_image(images):
    # print(trans_class)

    # trans=transforms.Compose([trans_class.transforms[0],trans_class.transforms[-2],trans_class.transforms[-1]])
    for i,j in enumerate(images):
            images[i]=augment(Image.open(io.BytesIO(j.read()))).unsqueeze(0)
    batch_img=torch.cat(images)
    print(batch_img.shape)
    return batch_img

def get_category(images):  
    transformed_image = transform_image(images=images)
    # use the model to predict the class
    print(transformed_image.shape)
    out = model(transformed_image)
    print(out)
    res={}
    for label in out:
        print(out[label].shape)
        res[label]=list(encoder[label].inverse_transform(out[label].argmax(axis=1).detach().tolist()))
    return list(zip(*res.values()))

def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

import os
@app.route('/res', methods=['POST', 'GET'])
def results():
    
    if request.method == 'POST':
        images=request.files.getlist("image")
        res=get_category(images)
        images=request.files.getlist("image")
        meta=[]
        for i,fil in enumerate(images):
            if fil.filename == "":
                print("no file name")
                continue
            
            filename = secure_filename(fil.filename)
            # print(filename)
            fil.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # filename=filename
            meta.append((os.path.join(app.config["UPLOAD_FOLDER"], filename),filename.split(".")[0],res[i]))

        
        return render_template("index.html",images=meta)
    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
