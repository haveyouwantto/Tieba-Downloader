function parseArguments() {
    try {
        let href = window.location.href.split("#");
        let dict = {};
        let args = href[href.length - 1].split("&");
        for (let i = 0; i < args.length; i++) {
            const element = args[i].split("=");
            dict[element[0]] = element[1];
        }
        return dict;
    }
    catch (e) {
        return null;
    }
}

function init(pages) {
    let arguments = parseArguments();
    if (arguments.pn == undefined) setPage(pages, 1);
    else {
        pn = arguments.pn;
        setPage(pages, arguments.pn);
    }
}

/**
 * 设置贴子页码
 * @param {*} pages 贴子信息
 * @param {number} pn 页码
 */
function setPage(pages, pn) {
    if (pn < 1) pn = 1;
    if (pn > px) pn = px;
    let prev = document.getElementById("prev");
    let next = document.getElementById("next");
    if (pn <= 1) prev.disabled = true;
    else prev.disabled = false;
    if (pn >= px) next.disabled = true;
    else next.disabled = false;
    updatePage(pages, pn);
}

function updatePage(pages, pn) {
    let span = document.getElementById('posts');
    let pagetext = document.getElementById('pagenum');
    window.location.href = "index.html#pn=" + pn
    pagetext.innerText = '第 ' + pn + ' 页，共 ' + px + ' 页'
    span.innerHTML = "";
    try {
        span.scrollTo(0, 0);
    }
    catch (e) {
        console.log('浏览器不支持滚动');
    }
    for (let i = 0; i < pages[pn - 1].length; ++i) {
        createPost(pages[pn - 1][i]);
    }
}

function createPost(postData) {
    let span = document.getElementById('posts');
    let chatbox = document.createElement('div');
    chatbox.setAttribute('class', 'post');

    chatbox.appendChild(createSender(postData));
    chatbox.appendChild(createFloorField(postData));

    span.append(chatbox);
}

function createFloorField(postData) {
    let floor = document.createElement('div');
    floor.setAttribute('class', 'floor');

    floor.appendChild(createSenderName(postData));
    floor.appendChild(createFloorNum(postData));
    floor.appendChild(createTextField(postData));
    return floor;
}

function createFloorNum(postData) {
    let num = document.createElement('div');
    num.setAttribute('class', 'floornum');
    let textNode = document.createTextNode("第 " + postData.content.post_no + " 楼");
    num.appendChild(textNode);
    return num;
}

function createTextField(postData) {
    let text = document.createElement('div');
    text.setAttribute('class', 'text');
    text.innerHTML = postData.content.content;
    return text;
}

function createSender(postData) {
    let sender = document.createElement('div');
    sender.setAttribute('class', 'sender');

    sender.appendChild(createAvatar(postData));

    return sender;
}

function createSenderName(postData) {
    let sender_name = document.createElement('div');
    sender_name.setAttribute('class', 'sender_name');
    sender_name.innerText = postData.author.user_name;
    return sender_name;
}

function createAvatar(postData) {
    let image = document.createElement('img');
    image.setAttribute('class', 'avatar');
    image.setAttribute('src', 'img/avatars/' + postData.author.user_name + '.jpg');
    return image;
}