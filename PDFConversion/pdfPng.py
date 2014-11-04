'''
Takes in a pdf file and returns the file as a png image. 

Input: pdf file without file extension (i.e. if converting test.pdf, input "test")
Output: png file with same file name (test.pdf becomes test.png)
'''



from wand.image import Image

def pdfPng(name):
	with Image(filename=name+'.pdf') as original:
	    with original.convert('png') as converted:
	        # operations to a jpeg image...
	        converted.save(filename= name +'.png')
	        return converted


#name = 
#pdfJPG(name)