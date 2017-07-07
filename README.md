# CardGenerator 

What do you do when you have a kanban inventory system, hundreds of items to make information cards for, and an intense distaste for manual labor? You get your computer to do the work (obviously).

This nifty little pyscript looks at an inventory CSV with information on product bin IDs, vendors, names, refresh quantities, and Amazon product pages and draws up a 612x712 JPG product card for each item.

The cool part is that the user does no work, not even looking for images, because the card images are scraped off of each item's Amazon product page, and the rest of our information is provided in a usable format.  

If you'd like to run this, be sure to:

    pip install Pillow
    pip install beautifulsoup4
    pip install urllib
    pip install requests

## One more thing
Amazon sometimes likes to (unpredictably) give the scraper a 503. If this happens, the script will pause for 7 seconds and try again until it gets what it wants. If it does this repeatedly (~>5x), however, you'd be better off restarting the program.
