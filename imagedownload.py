import requests


def download_file(url, filename):
    r = requests.get(url, stream=True)
    #print('服务器返回 '+str(r.status_code))  # 返回状态码
    if r.status_code == 200:
        open(filename, 'wb').write(r.content)
    else:
        return
    del r
    #print('下载成功')


def download_avatar(username, id, filename):
    url = "https://gss0.bdstatic.com/6LZ1dD3d1sgCo2Kml5_Y_D3/sys/portrait/item/" + id
    download_file(url, filename)


def download_smiley(url, filename):
    download_file(url, filename)


def download_image(url, filename):
    url2 = 'http://tiebapic.baidu.com/forum/pic/item/' + \
        url.split('/')[len(url.split('/'))-1]
    r = requests.get(url2, stream=True)
    #print('服务器返回 '+str(r.status_code))  # 返回状态码
    if r.status_code == 200:
        open(filename, 'wb').write(r.content)
    else:
        url2 = 'http://imgsrc.baidu.com/forum/pic/item/' + \
            url.split('/')[len(url.split('/'))-1]
        download_file(url2, filename)
