import json
import os
import shutil
import urllib.parse

import imagedownload

from bs4 import BeautifulSoup
import requests

pages = []
usernames = []
smiley = []

no = int(input('贴子id: '))
see_lz = int(input('只看楼主: '))
page = 1
max_page = int(input('页数: '))


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


folder = "saved/"+str(no) + "/"
imagedir = "img/"
postimgdir = imagedir + "posts/"
avatardir = imagedir + "avatars/"
smileydir = imagedir + "smiley/"
mkdir(folder)
mkdir(folder + imagedir)
mkdir(folder + postimgdir)
mkdir(folder + avatardir)
mkdir(folder + smileydir)

img = 0
while page <= max_page:
    posts = []
    url = 'https://tieba.baidu.com/p/{0}?see_lz={1}&pn={2}'.format(
        no, see_lz, page)
    print('正在下载第' + str(page) + '页')
    r = requests.get(url)
    response = r.text  # 服务器返回响应

    soup = BeautifulSoup(response, "html.parser")

    for i in soup.find_all(class_='l_post l_post_bright j_l_post clearfix'):
        post = json.loads(i.attrs['data-field'])

        # 检测发帖人
        username = post['author']['user_name']
        if username not in usernames:
            imagedownload.download_avatar(
                username, post['author']['portrait'], folder + avatardir + username + '.jpg')
            usernames.append(username)

        # 下载贴子图片
        if '<img' in post['content']['content']:
            innerSoup = BeautifulSoup(
                post['content']['content'], "html.parser")

            # 图片
            for j in innerSoup.find_all(class_="BDE_Image"):
                filename = "{0}.jpg".format(img)
                imagedownload.download_image(
                    j.attrs['src'], os.path.join(folder, postimgdir, filename))
                j.attrs['src'] = postimgdir + filename
                img += 1

            # 自定义表情包
            for j in innerSoup.find_all(class_="BDE_Meme"):
                filename = "{0}.jpg".format(img)
                imagedownload.download_image(
                    j.attrs['src'], os.path.join(folder, postimgdir, filename))
                j.attrs['src'] = postimgdir + filename
                img += 1
            post['content']['content'] = str(innerSoup)

            # 默认表情
            for j in innerSoup.find_all(class_="BDE_Smiley"):
                filename = os.path.basename(j.attrs['src']).split('?')[0]
                imagedownload.download_smiley(
                    j.attrs['src'], os.path.join(folder, smileydir, filename))
                j.attrs['src'] = smileydir + filename
                img += 1
            post['content']['content'] = str(innerSoup)

        # 转换贴子链接
        if '<a' in post['content']['content']:
            innerSoup = BeautifulSoup(
                post['content']['content'], "html.parser")

            # 链接
            for j in innerSoup.find_all(class_="j-no-opener-url"):
                print('转换链接: '+j.attrs['href'])
                j.attrs['href'] = "redirect.html?url=" + urllib.parse.quote(j.text)
            post['content']['content'] = str(innerSoup)

            # @人
            for j in innerSoup.find_all(class_="at"):
                print('转换@人: '+j.attrs['href'])
                j.attrs['href'] = 'http://tieba.baidu.com/home/main?un=' + j.attrs['username']
            post['content']['content'] = str(innerSoup)

        posts.append(post)

    pages.append(posts)

    page += 1

# 复制模板文件
print('复制文件')
for file in os.listdir('template/'):
    shutil.copyfile('template/' + file, folder + file)

f = open(folder + 'data.js', 'w')
f.write('let pages=')
f.write(json.dumps(pages))
f.write(''';
let pn=1;
let px=pages.length;
document.getElementById("jump").max=px;
init(pages);
''')
f.close()
print('下载完成')