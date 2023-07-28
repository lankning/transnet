from pipes import quote
import fitz, os, zipfile, shutil, PyPDF2, time, datetime, pillow_heif
from PIL import Image

def fetchtime():
    now = datetime.datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime

def writelog(filename, content):
    with open(filename, "a+") as f:
        f.write(fetchtime()+" "+str(content)+"\n")

def PDF2IMG(pdfPath, savePath, scale=1):
    """
    PDF2IMG: Transfer a single PDF file to a zip file of IMAGEs
    pdfPath: the path of PDF file
    imagePath: images to save here
    """
    pdfname = pdfPath.split("/")[-1] # like "repo/tree/book.pdf" -> "book.pdf"
    imagePath = pdfname[:-4]
    if not os.path.exists(imagePath):
        os.makedirs(imagePath)
    zip = zipfile.ZipFile(os.path.join(savePath,"%s.zip" % pdfname[:-4]), "w", zipfile.ZIP_DEFLATED)
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        # Zoom by scale
        zoom_x = 1.3 * scale
        zoom_y = 1.3 * scale
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        pix.writePNG(os.path.join(imagePath,'%s.png' % pg))
        zip.write(os.path.join(imagePath,'%s.png' % pg), '%s.png' % pg)
    zip.close()
    shutil.rmtree(imagePath)

def find_all_files_path(cpath, fileformat=".pdf", filelist=[]):
    """
    find_all_files_path: find all files' path under current path with fileformat
    cpath: current path
    fileformat: format of files
    Trick: Function reload is used for searching
    """
    writelog("log.txt", "current path: %s" % cpath)
    for f in os.listdir(cpath):
        if os.path.isfile(os.path.join(cpath,f)) and f[-1*len(fileformat):]==".pdf":
            filelist.append(os.path.join(cpath,f))
        elif os.path.isdir(os.path.join(cpath,f)):
            find_all_files_path(os.path.join(cpath,f),fileformat=fileformat,filelist=filelist)
    filelist.sort()
    return filelist


def MERGEPDF(zippath):
    """
    MERGEPDF: Merge a zip of pdfs into a single pdf file
    zippath: path of the zip of pdfs
    temppath: path of extracting zip and save the merged pdf
    """
    # step 1: unzip zip file
    temppath = zippath[:-4] # "temppath/book.zip" -> "temppath/book"
    if not os.path.exists(temppath):
        os.mkdir(temppath)
    zip = zipfile.ZipFile(zippath)
    zip.extractall(temppath)
    zip.close()
    # step 2: list pdfs' paths
    filelist = []
    filelist = find_all_files_path(temppath,".pdf",filelist)
    writelog("log.txt", filelist)
    # step 3: merge pdf
    if len(filelist)==0 or len(filelist)==1:
        shutil.rmtree(zippath[:-4])
        return 0 # Error: No files
    else: # len >= 2
        filelist.sort()
        # merge the file.
        pdfFM = PyPDF2.PdfFileMerger(strict=False)
        for fn in filelist:
            writelog("log.txt","Start merging %s ..." % fn)
            file = open(fn,'rb')
            pdfFM.append(file)
            file.close()
        # output the file.
        with open("%s.pdf"%zippath[:-4], 'wb') as write_out_file:
            pdfFM.write(write_out_file)
        shutil.rmtree(zippath[:-4])
        return 1

def HEIC2JPG(heicpath, jpgpath):
    """
    HEIC2JPG: Transfer HEIC to JPG
    """
    if pillow_heif.is_supported(heicpath):
        heif_file = pillow_heif.open_heif(heicpath)
        heif_file.save(jpgpath, quality=95, save_all=False)
        return 1
    return 0

def get_size(filename):
    # Obtain the file size: KB
    size = os.path.getsize(filename)
    return size / 1024

def COMPRESSIMG(imgpath, mode='0'):
    """
    COMPRESSIMG: Compresss image, 不改变图片尺寸压缩图像大小
    imgpath: 压缩图像读取地址
    mode: '0', utral-low, quality=50, resolution = 0.4*raw
    mode: '1', utral-low, quality=70, resolution = 0.7*raw
    mode: '2', utral-low, quality=80, resolution = 0.9*raw
    """
    img = Image.open(imgpath)
    img = img.convert('RGB')
    w = img.size[0]
    h = img.size[1]
    if mode == '0':
        w = int(0.5*w)
        h = int(0.5*h)
        q = 50
    elif mode == '1':
        w = int(0.7*w)
        h = int(0.7*h)
        q = 70
    elif mode == '2':
        w = int(0.9*w)
        h = int(0.9*h)
        q = 80
    else:
        return 0
    img = img.resize((w,h),Image.BICUBIC)
    img.save(imgpath, quality=q)
    writelog("log.txt", 'File size: %.2f KB' % get_size(imgpath))
    return 1

def IMGSR(imgpath, mode='Bicubic', scale=2):
    """
    mode: "Bicubic" / "Neural Network"
    scale: 2 / 4
    """
    img = Image.open(imgpath)
    img = img.convert('RGB')
    w = int(scale*img.size[0])
    d = int(scale*img.size[1])
    img = img.resize((w,d),Image.BICUBIC)
    img.save(imgpath, quality=100)
    writelog("log.txt", 'Super resolution, scale: %d, mode: %s, w: %d, d: %d' % (scale, mode, w, d))
    return 1



def clear(path, intervaltime=60):
    """
    path: path to be cleared
    intervaltime: intervaltime of clear (minute)
    """
    while(1):
        filelist = os.listdir(path)
        filelist = [os.path.join(path,f) for f in filelist]
        ct = time.time()
        for f in filelist:
            mt = os.path.getmtime(f)
            if (ct-mt)>intervaltime*60:
                os.remove(f)
        time.sleep(60*intervaltime)

if __name__ == "__main__":
    fl = []
    fl = find_all_files_path("uploads/note",".pdf",fl)
    print(fl)