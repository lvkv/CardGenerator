#pip install Pillow
#pip install beautifulsoup4
#pip install urllib
#pip install requests

from urllib.request import urlopen
from bs4 import BeautifulSoup
from PIL import Image, ImageFile, ImageDraw, ImageFont
from io import BytesIO
import urllib
import textwrap
import requests
import time
import csv

# Input: Direct URI to an image on the web
# Output: Tuple (l, w) with the image's dimensions
def getImageSize(uri):
    # Some image URIs may be incorrectly formatted, so we'll skip them
    try:
        file = urlopen(uri)
    except ValueError:
        print('An image on this page almost crashed our ride')
        return (10,10)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return p.image.size
            break
    file.close()
    return None

# Input: URL to (preferably Amazon) webpage for a product
# Output: Direct URI to a satisfactory product image
def getImageURL(url):
    # Sometimes Amazon kicks our scraper and gives us a 503, so we let it cool off before trying again
    while True:
        try:
            html = urlopen(url)  # Open the page
            break
        except urllib.error.HTTPError:
            print("We've been rejected! Waiting 7 seconds and trying again...")
            time.sleep(7)
    soup = BeautifulSoup(html.read(), "html.parser") 
    imgs = soup.findAll("img",{"alt":True, "src":True}) # Scrape up all the images
    l = 200  # We want decent sized images...
    w = 200
    while True:
        for img in imgs[2:]:  # The first two images on an Amazon product page are usually high res banners... skip.
            img_url = img["src"]  # Direct URI to the image we're inspecting
            img_size = getImageSize(img_url)  # Find the image's size
            if img_size[0]>l and img_size[1]>w:
                return img_url  # 99% of the time, the first image to satisfy these lw requirements on an Amazon page is the product image
        l -= 50  # If our search yields nothing, we'll lower our standards until we find something
        w -= 50
        
# Input: List with product information (from our CSV)
# Output: Saves our final stitched card
def assembleImage(row):
    binID = row[0]  # These are data from our spreadsheet
    print(row)
    vendor = row[1]
    product = row[2]
    qty = row[4] + ' pcs'
    
    response = requests.get(getImageURL(row[5]))  # These two lines allow us to grab our product image for use with PIL 
    image = Image.open(BytesIO(response.content))

    landscape = False
    if row[0][0] != 'C':  # Bin IDs with the prefix 'CAB' have landscape-oriented cards
        canvas = Image.open("blank.jpg")
    else:
        canvas = Image.open("blank_cab.jpg")
        landscape = True

    draw = ImageDraw.Draw(canvas)  # We draw... on our canvas
    
    font = ImageFont.truetype("arial.ttf", 70)  # BinID and Qty have larger fonts
    if landscape:
        draw.text((40, 500), binID, (0,0,0), font=font)
        draw.text((500, 500), qty, (0,0,0), font=font)
    else:
        draw.text((40, 700), binID, (0,0,0), font=font)
        draw.text((400, 700), qty, (0,0,0), font=font)

    font = ImageFont.truetype("arial.ttf", 40)
    if landscape:
        draw.text((20, 80), vendor, (0,0,0), font=font)
        offset = 120  # Some product names are too long for one line, so we wrap the text here
        for line in textwrap.wrap(product, width=40):
            draw.text((20, offset), line, (0,0,0), font=font)
            offset += font.getsize(line)[1]
        canvas.paste(image, (185,200))  # Pasting our product image in the center
    else:
        draw.text((20, 80), vendor, (0,0,0), font=font)
        offset = 120
        for line in textwrap.wrap(product, width=30):
            draw.text((20, offset), line, (0,0,0), font=font)
            offset += font.getsize(line)[1]
        canvas.paste(image, (185,300))
        
    filepath = binID+'_'+vendor+'_'+(''.join(product.split('/')))+'.jpg'  # Some product names have no-good slash chars in them, so we filter them out
    canvas.save(filepath)
    
        
#Spreadsheet reading
with open('Org_Items_IT.csv', newline='') as csvfile:
    myreader = csv.reader(csvfile, delimiter=',', quotechar='|')  # Make sure to remove any non-delimiting commas in your CSV
    next(myreader) # Skip the category headers
    for row in myreader:
        assembleImage(row)
        
