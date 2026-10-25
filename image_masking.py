# Applies the shape of a "mask" image on another image
# The input images formats are those accepted by Pillow

from PIL import Image, ImageOps

def applyMask(folderPath : str,
              backgroundImageName : str, # Image_name.extension
              maskImageName : str, # Image_name.extension
              OutputImageName : str,
              maskColor : tuple[int, int, int] = (0, 0, 0),
              colorMargin : int = 0, # Margin around the set color that will be counted as part of the mask (0 to 255)
              deleteExterior : bool = True, # Sets the outside of the mask as transparent; otherwise, sets it as the mask image
              backgroundMixing : bool = False, # Sets the background transparency proportionnally to the gap with the set value; only relevant if deleteExterior is set to True
              autoCrop : bool = True, # Crops the output image to the size of the mask; non relevant if deleteExterior is set to False
              ) :

    folderPath.replace("\\", "/")
    if folderPath[-1] == "/" : folderPath = folderPath[:-1]

    try :
        # Loads the images through PIL
        backgroundImage = Image.open(f"{folderPath}/{backgroundImageName}").convert("RGBA")
        maskImage = Image.open(f"{folderPath}/{maskImageName}").convert("RGBA")
    except FileNotFoundError :
        print("Invalid folder/file names. Make sure you include file extension (.png, .jpg, etc.)")
        return

    backgroundWidth, backgroundHeight = backgroundImage.size

    # Resizes the mask image to fit the background
    maskImage = ImageOps.fit(
        maskImage,
        (backgroundWidth, backgroundHeight),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5) # Centers the crop area
    )

    maskWidth, maskHeight = maskImage.size

    backgroundPixelMap = backgroundImage.load()
    maskPixelMap = maskImage.load()
    
    # Coordinates of the mask on the mask image
    maskCoordinates = []

    # Border coordinates of the mask on the mask image
    minX = maskWidth
    maxX = 0
    minY = maskHeight
    maxY = 0

    for y in range(maskHeight) :
        for x in range(maskWidth) :
            red, green, blue, alpha = maskPixelMap[x, y] # type: ignore

            # Checks if the pixel is of the set color +- margin
            if  (maskColor[0] - colorMargin) <= red <= (maskColor[0] + colorMargin) and \
                (maskColor[1] - colorMargin) <= green <= (maskColor[1] + colorMargin) and \
                (maskColor[2] - colorMargin) <= blue <= (maskColor[2] + colorMargin) :\
                
                if x < minX :
                    minX = x
                if x > maxX :
                    maxX = x
                if y < minY :
                    minY = y
                if y > maxY :
                    maxY = y

                if backgroundMixing :
                    mixingRatio = (sum([abs(maskColor[0] - red) / colorMargin,
                                       abs(maskColor[0] - green) / colorMargin,
                                       abs(maskColor[0] - blue) / colorMargin]) / 3)

                else :
                    mixingRatio = 0
                
                maskCoordinates.append((x, y, mixingRatio))

    if not deleteExterior :
        outputImage = maskImage
        outputPixelMap = outputImage.load()
        for (x, y, mixingRatio) in maskCoordinates :
            red, green, blue, alpha = backgroundPixelMap[x, y] # type: ignore
            if backgroundMixing :
                red = maskPixelMap[x, y][0] * mixingRatio + red * (1-mixingRatio) # type: ignore
                green = maskPixelMap[x, y][1] * mixingRatio + green * (1-mixingRatio) # type: ignore
                blue = maskPixelMap[x, y][2] * mixingRatio + blue * (1-mixingRatio) # type: ignore
            outputPixelMap[x, y] = (int(red), int(green), int(blue)) # type: ignore

    elif not autoCrop :
        outputImage = Image.new("RGBA", (backgroundWidth, backgroundHeight), (0, 0, 0, 0))
        outputPixelMap = outputImage.load()
        for (x, y, mixingRatio) in maskCoordinates :
            red, green, blue, alpha = backgroundPixelMap[x, y] # type: ignore
            outputPixelMap[x, y] = (red, green, blue) # type: ignore
    
    else :
        maskRealWidth = maxX - minX + 1
        maskRealHeight = maxY - minY + 1
        outputImage = Image.new("RGBA", (maskRealWidth, maskRealHeight), (0, 0, 0, 0))
        outputPixelMap = outputImage.load()

        for (x, y, mixingRatio) in maskCoordinates :
            red, green, blue, alpha = backgroundPixelMap[x, y] # type: ignore
            outputPixelMap[x - minX, y - minY] = (red, green, blue) # type: ignore

    outputImage.save(f"{folderPath}/{OutputImageName}")

applyMask(folderPath="",
          backgroundImageName="Background.png",
          maskImageName="Mask.png",
          OutputImageName="Output.png",
          maskColor=(0, 0, 0),
          colorMargin=0,
          deleteExterior=True,
          autoCrop=True,
          backgroundMixing=False)
