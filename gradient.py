from textwrap import wrap
import numpy as np
import types

#Accepts strings in the format #FFFFFF[FF], FFFFFF[FF]
def color_from_hex(hexstr):
    rgba = [1]*4
    if(hexstr[0] == '#'):
        hexstr = hexstr[1:]
    rgb_hex = wrap(hexstr, 2)
    rgba = [int(rgb_hex_channel, 16)/255.0 for rgb_hex_channel in rgb_hex]
    if len(rgba) == 3:
        rgba += [1.0]
    return rgba

def build_gradient(colorlist, splitpointlist, resolution=4096):
    if type(colorlist[0][0]) is str:
        colorlist = [[color_from_hex(color) for color in colors] for colors in colorlist]

    colorlist = np.array(colorlist)
    splitpointlist = np.array(splitpointlist)
    gradient = np.zeros((resolution,4))
    # Paint in each gradient on the global gradient
    for i, (grad,colors) in enumerate(zip(splitpointlist, colorlist)):
        start,end = grad[0],grad[1]
        startcolor,endcolor=colors[0],colors[1]

        for j in range(resolution):
            gradient_pos = j/float(resolution)
            if start <= gradient_pos and gradient_pos < end:
                pos_in_grad = (gradient_pos-start)/(end-start)
                gradient[j] = startcolor * (1-pos_in_grad) + endcolor * pos_in_grad
    
    return gradient




if __name__ == '__main__':
    print(color_from_hex("CCFFFF"))
    grad = build_gradient(["84a98c", "52796f"],[[0,1.0]])
    print(grad)