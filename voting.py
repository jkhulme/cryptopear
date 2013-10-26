def encode_image(path):
    with open(path, 'r') as f:
        return f.read().encode("base64")

def decode_image(data):
    with open('test_images/test_james_copy.jpeg','w') as f:
        f.write(data.decode("base64"))
