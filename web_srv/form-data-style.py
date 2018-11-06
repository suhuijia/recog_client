######### form-data格式请求图片数据
def ReadFileAsContent(filename):  
    #print filename  
    try:  
        with open(filename, 'rb') as f:  
            filecontent = f.read()  
    except Exception as e:  
        print('The Error Message in ReadFileAsContent(): ' + e.message)
        return ''  
    return filecontent


def random_string(num):
    import string
    rand_str = ''
    for _ in range(num):
        rand_str += ''.join(random.sample(string.ascii_letters + string.digits, 1))
        # print(rand_str)
    return rand_str


def post_multipart(host, selector, fields, files):  
    content_type, body = encode_multipart_formdata(fields, files)
    print(content_type)
    body_buf = bytearray(body)
    h = httplib.HTTP(host)  
    h.putrequest('POST', selector)  
    h.putheader('content-type', content_type)  
    h.putheader('content-length', str(len(body_buf)))  
    h.endheaders()  
    h.send(body_buf)  
    errcode, errmsg, headers = h.getreply()  
    print(errcode, errmsg)
    # print(h.file.read())
    # print(headers)
    return h.file.read()
  

def encode_multipart_formdata(fields, files):

    # LIMIT = '----------%s' % ''.join(random.sample('0123456789abcdef', 15))
    # LIMIT = '----------lImIt_of_THE_fIle_eW_$'
    LIMIT = "----" + random_string(20)
    # print(LIMIT)
    body = []
    for (key, value) in fields:
        body.extend(bytes('\r\n--' + LIMIT + '\r\n'))
        body.extend(bytes('Content-Disposition: form-data; name="%s"\r\n' % key))
        body.extend(bytes('\r\n'))
        body.extend(bytes(value))
    for (key, filename, value) in files:
        body.extend(bytes('\r\n--' + LIMIT + '\r\n'))
        body.extend(bytes('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)))
        body.extend(bytes('Content-Type: %s\r\n' % get_content_type(filename)))
        body.extend(bytes('\r\n'))
        body.extend(value)
    body.extend('\r\n--' + LIMIT + '--\r\n')
    content_type = 'multipart/form-data; boundary=%s' % LIMIT
    return content_type, body  


def get_content_type(filename):
    import mimetypes  
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'  
  
  
if "__main__" == __name__:

    img_path = 'E:/Face-detect-recog/test_image/920223/920223_3.jpg'
    data = ReadFileAsContent(img_path)
    # data = [0x01, 0x02, 0x03, 0x04]
    fields = [("type", "0")]
    files = [("up_img", "920223_3.jpg", data)]
    response_str = post_multipart("127.0.0.1:9800", "/v1/face/recognition/", fields, files)
    print(response_str)
