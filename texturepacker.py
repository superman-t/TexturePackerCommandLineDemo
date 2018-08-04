#!/usr/bin/python  
#encoding=utf-8  
import io
import os
import sys  
import hashlib  
import string  
import re
import getopt
import time, threading, multiprocessing
from multiprocessing import Pool
from multiprocessing import Process

rootPath = ""
outPath = ""
multipack = False

try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:m",["ifile=","ofile=", "multipack"])
except getopt.GetoptError:
    print 'texturepacker.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print 'texturepacker.py -i <inputfile> -o <outputfile>'
        sys.exit()
    elif opt in ("-i", "--ifile"):
        rootPath = os.path.abspath(arg)
    elif opt in ("-o", "--ofile"):
        outPath = os.path.abspath(arg)
    elif opt in ("-m", "--multipack"):
        multipack = True



 
# # input paths
ImageDir  = rootPath

# temporary path to place the sprite sheets
OutputDir = outPath

# # path of the texture packer command line tool
TP="TexturePacker"

# print("ImageDir = " + ImageDir)
# print("OutputDir = " + OutputDir)
# print("TP = " + TP)
 
 
#文件输出目录
def createPath(cPath):
    if not os.path.isdir(cPath):
        os.mkdir(cPath)
 
 
# --trim-sprite-names  去除png等后缀
# --multipack 多图片打包开起，避免资源图太多，生成图集包含不完全，开起则会生成多张图集。
# --maxrects-heuristics macrect的算法  参数 Best ShortSideFit LongSideFit AreaFit BottomLeft ContactPoint
# --enable-rotation 开起旋转，计算rect时如果旋转将会使用更优的算法来处理，得到更小的图集
# --border-padding 精灵之间的间距
# --shape-padding 精灵形状填充
# --trim-mode Trim 删除透明像素，大小使用原始大小。 参数 None Trim Crop CropKeepPos Polygon
# --basic-sort-by Name  按名称排序
# --basic-order Ascending 升序
# --texture-format 纹理格式
# --data 输出纹理文件的信息数据路径 plist
# --sheet 输出图集路径 png
# --scale 1 缩放比例 主要用于低分辨率的机子多资源适配。
# --max-size 最大图片像素 一般我是用的2048，超过2048以前的有些android机型不支持。
# --size-constraints 给纹理进行大小格式化，AnySize 任何大小 POT 使用2次幂 WordAligned
# --replace 正则表达式，用于修改plist加载后的名称
# --pvr-quality PVRTC 纹理质量
# --force-squared 强制使用方形
# --etc1-quality ETC 纹理质量
def PackTextures(inputPath, outputPath, opt, scale, maxSize, sheetSuffix, textureFormat, sizeConstraints, sheetName, otherParams, fileNameSuffix):
    packCommand = TP + \
        " --multipack" \
        " --format cocos2d-x" \
        " --maxrects-heuristics best" \
        " --enable-rotation" \
        " --shape-padding 2" \
        " --border-padding 0" \
        " --trim-mode Trim" \
        " --basic-sort-by Name" \
        " --basic-order Ascending" \
        " --texture-format {textureFormat}" \
        " --data {outputSheetNamePath}{fileNameSuffix}.plist" \
        " --sheet {outputSheetNamePath}{fileNameSuffix}.{sheetSuffix}" \
        " --scale {scale}" \
        " --max-size {maxSize}" \
        " --opt {opt}" \
        " --size-constraints {sizeConstraints}" \
        " {inputPath}" \
        " {otherParams}"
 
 
    # # win 和 mac 上处理正则表达式结果不一样
    # if sys.platform == "win32":
    #   #replace .png to ""
    #   #\\b word boundary
    #     packCommand = packCommand + " --replace (.png)$=" \
    #         " --replace \\b={sheetName}_" \
    #         " --replace {sheetName}_$=.png"
    # else:
    #     packCommand = packCommand + " --replace ^={sheetName}_"
 
 
    packCommand = packCommand.format(
        textureFormat=textureFormat,
        outputSheetNamePath=os.path.join(outputPath,sheetName) + "_{n}",
        sheetName=sheetName,
        sheetSuffix=sheetSuffix,
        scale=scale,
        maxSize=maxSize,
        opt=opt,
        sizeConstraints=sizeConstraints,
        inputPath=inputPath,
        otherParams=otherParams,
        fileNameSuffix=fileNameSuffix)
    os.system(packCommand)


def ExePack( inputPath, outputPath, folder):
    print('Run task %s (%s)...' % (folder, os.getpid()))
    createPath(outputPath)
    if os.path.isdir(inputPath) and len(os.listdir(inputPath)) != 0: 
        PackTextures(inputPath, outputPath, 'RGBA8888', 1, 2048, 'png', "png", "POT", folder, "--png-opt-level 2 --force-squared", "")
            
def MutilThreadPack(inputPath, outputPath, folder):
    return Process(target=ExePack, name=folder, args=(inputPath, outputPath, folder))

if __name__ == '__main__':
    createPath(OutputDir)
    allThread = []
    startTime = time.clock()
    P = Pool(8)
    for sheet in os.listdir(ImageDir):
        inputPath = os.path.join(ImageDir, sheet)
        outputPath = os.path.join(OutputDir, sheet)
        print( inputPath, outputPath, sheet)
        folder = sheet
        if multipack :
            print( "mutilple thread packing")
            P.apply_async(ExePack, args=(inputPath, outputPath, folder))
        else:
            print( "single thread packing")
            ExePack(inputPath, outputPath, folder)
        
    P.close()
    P.join()

    print("-----------------------------------------")
    print( time.clock() - startTime)
    print("-----------------------------------------")