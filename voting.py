def encode_image(path):
    with open(path, 'r') as f:
        return f.read().encode("base64")

def decode_image(data, name):
    with open('test_images/'+name+'.jpeg','w') as f:
        f.write(data.decode("base64"))
