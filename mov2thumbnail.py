import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import shutil
import sys
from PIL import Image, ImageDraw, ImageFont

def pil2cv(imgPIL):
  imgCV_RGB = np.array(imgPIL, dtype = np.uint8)
  imgCV_BGR = np.array(imgPIL)[:, :, ::-1]
  return imgCV_BGR

def cv2pil(imgCV):
  imgCV_RGB = imgCV[:, :, ::-1]
  imgPIL = Image.fromarray(imgCV_RGB)
  return imgPIL

def cv2_putText(img, text, org, fontFace, fontScale, color):
  x, y = org
  b, g, r = color
  colorRGB = (r, g, b)
  imgPIL = cv2pil(img)
  draw = ImageDraw.Draw(imgPIL)
  fontPIL = ImageFont.truetype(font = fontFace, size = fontScale)
  w, h = draw.textsize(text, font = fontPIL)
  draw.text(xy = (x,y-h), text = text, fill = colorRGB, font = fontPIL)
  imgCV = pil2cv(imgPIL)
  return imgCV

def frame2time(frame,fps):
  duration = frame/fps
  hours = int(duration/60/60)
  minutes = int(duration/60)%60
  seconds = int(duration%60)
  return "{:02}:{:02}:{:02}".format(hours,minutes,seconds)

def cv2_imwrite_2byte(filename,img):
  temp = "temp.jpg"
  cv2.imwrite(temp,img_1920)
  shutil.copyfile(temp,filename)
  os.remove(temp)

def get_img(cap_file,getframe,fps,cb):
  cap_file.set(cv2.CAP_PROP_POS_FRAMES, int(getframe))
  ret, frame = cap_file.read()
  if ret:
    frame = cv2.resize(frame,(1920,1080))
    cv2.putText(frame,frame2time(getframe,fps), (20,120), cv2.FONT_HERSHEY_SIMPLEX, 5, (255,255,255), 8, cv2.LINE_AA)
    img = frame
  else:
    if cb <= 0:
      img = cv2.resize(np.zeros(size, dtype=np.uint8),(1920,1080))
    else:
      img = get_img(cap_file,getframe+1,fps,cb-1)
  return img


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--movfiles', required=True)
parser.add_argument('-o', '--outfiles', required=True)
args = parser.parse_args( )

sys.setrecursionlimit(100000)

jp_font = "./fonts/font.ttf"
#フォントファイルの存在チェックを追加
if not os.path.isfile(f"./fonts/font.ttf"):
    print("font file not found")
    sys.exit()
img_ram = {}
img_ram1 = {}
size = 1280,1920, 3
movfiles = args.movfiles
jpgfiles = args.outfiles
files = glob.glob(f"{movfiles}/**/*",recursive=True)

for file in files:
  print(os.path.relpath(file,movfiles))
  #サムネイルが存在するか確認
  if os.path.isfile(f"{jpgfiles}{os.path.relpath(file,movfiles)}.jpg"):
    pass
  else:
    #出力の初期化
    print(f"{file}")
    img_1920 = np.zeros(size, dtype=np.uint8)
    cap_file = cv2.VideoCapture(file)

    #正常に読み込めたか？
    if cap_file.isOpened():
      #動画詳細情報
      frameMax = cap_file.get(cv2.CAP_PROP_FRAME_COUNT)
      fps = cap_file.get(cv2.CAP_PROP_FPS)
      cap_file.set(cv2.CAP_PROP_POS_FRAMES, 1)
      if fps > 1.0:
        ret, frame = cap_file.read()
      else:
        ret = False
      if ret:
        height, width, channels = frame.shape[:3]
        resolution = str(width) + "x" + str(height)
        durationout = frame2time(frameMax,fps)
        print (f"{durationout}")
        #フレーム取得
        for ram1 in range(4):
          for ram2 in range(4):
            getframe = (frameMax/17)*((ram1*4)+ram2+1)
            img_ram[ram2] = get_img(cap_file,getframe,fps,1)
          img_ram1[ram1] = np.concatenate((img_ram[0],img_ram[1],img_ram[2],img_ram[3]),axis=1)
        img_out = np.concatenate((img_ram1[0],img_ram1[1],img_ram1[2],img_ram1[3]),axis=0)
        img_re = cv2.resize(img_out,(1920,1080))


        x_offset=0
        y_offset=200
        img_1920[y_offset:y_offset+img_re.shape[0], x_offset:x_offset+img_re.shape[1]] = img_re


        img_1920 = cv2_putText(img_1920, 'FileName:'+os.path.basename(file), (int(20),int(50)),jp_font, 35, (255,255,255))
        img_1920 = cv2_putText(img_1920, 'FileSize:'+str(int(os.path.getsize(file)/1000000))+"MB", (int(20),int(90)),jp_font, 35, (255,255,255))
        img_1920 = cv2_putText(img_1920, 'Resolution:'+resolution, (int(20),int(130)),jp_font, 35, (255,255,255))
        img_1920 = cv2_putText(img_1920, 'duration:'+durationout, (int(20),int(170)),jp_font, 35, (255,255,255))

        os.makedirs(os.path.dirname(f"{jpgfiles}{os.path.relpath(file,movfiles)}"), exist_ok=True)
        print (f"{jpgfiles}{os.path.relpath(file,movfiles)}.jpg")
        cv2_imwrite_2byte(f"{jpgfiles}{os.path.relpath(file,movfiles)}.jpg",img_1920)
        #cv2.imwrite(f"{jpgfiles}{os.path.relpath(file,movfiles)}.jpg",img_1920)

      else:
        print("moov atom not found")

      #読み込みファイルの開放
      cap_file.release()