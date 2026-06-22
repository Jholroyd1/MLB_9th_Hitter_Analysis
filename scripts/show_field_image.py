import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

img_path = '../data/baseball_field.png'
img = mpimg.imread(img_path)
fig, ax = plt.subplots(figsize=(10, 7))
ax.imshow(img)
ax.set_title('Baseball Field Image: Mark Home Plate')
plt.xlabel('Pixel X')
plt.ylabel('Pixel Y')
plt.tight_layout()
plt.show()
