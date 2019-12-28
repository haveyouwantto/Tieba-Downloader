import json
import os
import shutil
import urllib.parse

import imagedownload

from bs4 import BeautifulSoup
import requests


img = 0
emotions = []


def download_image(content, folder, postimgdir, smileydir):
    global img
    global emotions
    if content == None:
        return
    if '<img' in content:
        innerSoup = BeautifulSoup(
            content, "html.parser")

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

        # 默认表情
        for j in innerSoup.find_all(class_="BDE_Smiley"):
            filename = os.path.basename(j.attrs['src']).split('?')[0]
            if filename not in emotions:
                imagedownload.download_smiley(
                    j.attrs['src'], os.path.join(folder, smileydir, filename))
                emotions.append(filename)
            j.attrs['src'] = smileydir + filename
        return str(innerSoup)
    else:
        return content


def convert_link(content, folder, postimgdir, smileydir):
    if content == None:
        return

    if '<a' in content:
        innerSoup = BeautifulSoup(
            content, "html.parser")

        # 链接
        for j in innerSoup.find_all(class_="j-no-opener-url"):
            print('转换链接: '+j.attrs['href'])
            j.attrs['href'] = "redirect.html?url=" + \
                urllib.parse.quote(j.text)

        # @人
        for j in innerSoup.find_all(class_="at"):
            print('转换@人: '+j.attrs['href'])
            j.attrs['href'] = 'http://tieba.baidu.com/home/main?un=' + \
                j.attrs['username']
        return str(innerSoup)
    else:
        return content


def download(no, see_lz, max_page):
    pages = []
    usernames = []
    smiley = []

    page = 1

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
            post['content']['content'] = download_image(
                post['content']['content'], folder, postimgdir, smileydir)

            # 转换贴子链接
            post['content']['content'] = convert_link(
                post['content']['content'], folder, postimgdir, smileydir)

            post['comments'] = None

            posts.append(post)

        print('获取楼中楼信息...')
        r2 = requests.get(
            'https://tieba.baidu.com/p/totalComment?tid={0}&see_lz={1}&pn={2}'.format(no, see_lz, page))
        response = r2.text  # 服务器返回响应

        midfloor = json.loads(response)

        for i in midfloor['data']['comment_list']:
            midpost = midfloor['data']['comment_list'][i]['comment_info']

            for j in range(len(midpost)):
                element = midpost[j]
                element['content'] = download_image(
                    element['content'], folder, postimgdir, smileydir)

                # 转换贴子链接
                element['content'] = convert_link(
                    element['content'], folder, postimgdir, smileydir)

                midpost[j] = element

            midfloor['data']['comment_list'][i]['comment_info'] = midpost

            for j in range(len(posts)):
                element = posts[j]
                if element['content']['post_id'] == int(i):
                    print('添加id为{0}的楼中楼回复'.format(i))
                    posts[j]['comments'] = midfloor['data']['comment_list'][i]

        for i in midfloor['data']['user_list']:

            element=midfloor['data']['user_list'][i]
            username = element['user_name']

            try:
                if username not in usernames:
                    imagedownload.download_avatar(
                        username, element['portrait'], folder + avatardir + username + '.jpg')
                    usernames.append(username)
            except:
                nickname=element['nickname']
                if nickname not in usernames:
                    imagedownload.download_avatar(
                        nickname, element['portrait'], folder + avatardir + nickname + '.jpg')
                    usernames.append(nickname)

        pages.append(posts)

        page += 1

    # 复制模板文件
    print('复制文件')
    for file in os.listdir('template/'):
        shutil.copyfile('template/' + file, folder + file)

    f = open(folder + 'data.js', 'w')
    f.write('let pages=')
    f.write(json.dumps(pages))
    f.write(';let pn=1;let px=pages.length;document.getElementById("jump").max=px;init(pages);')
    f.close()
    print('下载完成')


if __name__ == "__main__":
    download(3758753964, 1, 95)
