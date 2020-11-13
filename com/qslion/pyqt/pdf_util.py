# -*- coding: utf-8 -*-

# pip install PyMuPDF
# https://pymupdf.readthedocs.io/en/latest/tutorial.html

import os
import fitz
import datetime
from docx import Document
from docx.shared import Inches


def pdfToImage(pdfPath, _zoom_x=2.333333, _zoom_y=2.333333):
    """PDF 转图片"""
    startTime = datetime.datetime.now()  # 开始时间

    imagePath = os.path.join(os.path.split(pdfPath)[0], 'image');
    if not os.path.exists(imagePath):
        os.makedirs(imagePath)  # 若图片文件夹不存在就创建

    print("pdfPath:" + pdfPath + ",imagePath:" + imagePath)
    doc = fitz.open(pdfPath)  # 打开一个PDF文件，doc为Document类型，是一个包含每一页PDF文件的列
    rotate = int(0)  # 设置图片的旋转角度
    # 此处若是不做设置，默认图片大小为：792X612, dpi=96
    zoom_x = _zoom_x # 设置图片相对于PDF文件在X轴上的缩放比例(1.33333333-->1056x816) (2-->1584x1224)
    zoom_y = _zoom_y  # 设置图片相对于PDF文件在Y轴上的缩放比例
    mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
    new_img_name = os.path.join(imagePath, os.path.split(pdfPath)[1].split(".")[0])  # 保证输出的文件名不变
    if doc.pageCount > 1:  # 获取PDF的页数
        for pg in range(doc.pageCount):
            page = doc[pg]  # 获得第pg页
            pix = page.getPixmap(matrix=mat, alpha=False)  # 将其转化为光栅文件（位数）
            pix.writeImage("%s_%s.png" % (new_img_name, pg))
    else:
        page = doc[0]
        pix = page.getPixmap(matrix=mat, alpha=False)
        pix.writeImage("%s.png" % new_img_name)
    print('转换完成，耗时：', (datetime.datetime.now() - startTime).seconds)

def pdfToDocx(pdfPath):
    """PDF 转WORD文档"""

if __name__ == '__main__':
    pdfToImage("D:/bslogs/111.pdf")
