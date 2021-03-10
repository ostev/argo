from imutils import resize
from pyzbar import pyzbar


def get_barcodes(image):
    frame = resize(image, width=400)
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        # (x, y, w, h) = qr_code.rect
        print("x")
        data = barcode.data.decode("utf-8")
        print("Data: " + data + "\nType: " + barcode.type)
