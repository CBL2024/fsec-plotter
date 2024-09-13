import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.preprocessing import image
import numpy as np
import os

model = tf.keras.models.load_model("test.keras")

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

# predicting images

imglist = os.listdir('test_graphs')

b = []
for pic in imglist:
    img = image.load_img(os.path.join('test_graphs', pic), target_size=(150, 150))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    c = model.predict(images)
    ls = c.ravel()
    for i in range(len(ls)):
        if ls[i] > 0:  b.append((i+1)*0.2) 

arr = []
for i in range(8):
    arr.append(b[i*12:(i+1)*12])
print(arr)

x = np.arange(0, 13, 1) 
y = np.arange(0, 9, 1)  

fig, ax = plt.subplots()
ax.pcolormesh(x, y, arr)

plt.show()