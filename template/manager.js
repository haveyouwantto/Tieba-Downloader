let index = {};

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

function init(thread) {
    document.getElementById('title').innerText = thread.title;
    document.title += ' - ' + thread.title;
    let arguments = parseArguments();
    if (arguments.pn == undefined) setPage(thread.pages, 1);
    else {
        pn = arguments.pn;
        setPage(thread.pages, arguments.pn);
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
        span.scrollTop = 0;
    }
    catch (e) {
        console.log('浏览器不支持滚动');
    }
    for (let i = 0; i < pages[pn - 1].length; ++i) {
        createPost(pages[pn - 1][i]);
        setExpand(i, pages[pn - 1][i]);
    }

}

function setExpand(i, postData) {

    let floors = document.getElementsByClassName('floor');
    let floor = floors[i];
    let midfloor = floor.children[3];
    if (midfloor != null) {
        if (midfloor.clientHeight != midfloor.scrollHeight) {
            floor.appendChild(createExpandButton(postData));
        }
    }
}

function createPost(postData) {
    let span = document.getElementById('posts');
    let chatbox = document.createElement('div');
    chatbox.setAttribute('class', 'post');
    chatbox.setAttribute('id', postData.content.post_id);

    chatbox.appendChild(createSender(postData));
    chatbox.appendChild(createFloorField(postData));

    span.append(chatbox);
}

function createFloorField(postData) {
    let floor = document.createElement('div');
    floor.setAttribute('class', 'floor');

    floor.appendChild(createSenderName(postData));
    floor.appendChild(createFloorInfo(postData));
    floor.appendChild(createTextField(postData));

    if (postData.comments != null) {
        let midfloor = createMidFloor(postData);
        floor.appendChild(midfloor);
    }
    return floor;
}

function createFloorInfo(postData) {
    let num = document.createElement('div');
    num.setAttribute('class', 'floorinfo');
    num.appendChild(createFloorNum(postData));
    num.appendChild(createTime(postData));
    return num;
}

function createTime(postData) {
    let time = document.createElement('div');
    time.setAttribute('class', 'floortime');
    let textNode = document.createTextNode(postData.time);
    time.appendChild(textNode);
    return time;
}

function createFloorNum(postData) {
    let num = document.createElement('div');
    num.setAttribute('class', 'floornum');
    let textNode = document.createTextNode(postData.content.post_no + " 楼");
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

function createMidFloor(postData) {
    let midfloor = document.createElement('span');
    midfloor.setAttribute('class', 'midfloor');
    midfloor.setAttribute('page', '1');
    midfloor.setAttribute('maxpage', postData.comments.comment_info.length);
    midfloor.setAttribute('id', postData.content.post_id + '-mid');
    midfloor.setAttribute('index', postData.content.post_id + '-mid');
    index[postData.content.post_id + '-mid'] = postData;

    updateMidPosts(midfloor, 1);
    // [parseInt(midfloor.getAttribute('page'))-1]
    return midfloor;
}

function createExpandButton(postData) {
    let expand = document.createElement('a');
    expand.innerText = '\u25bc 展开';
    expand.setAttribute('id', postData.content.post_id + '-btn');
    expand.setAttribute('class', 'expand');
    expand.setAttribute('onclick', 'expand("' + postData.content.post_id + '");');
    expand.setAttribute('expanded', '0');
    return expand;
}

function createMidPost(commentInfo) {
    let midpost = document.createElement('div');
    midpost.setAttribute('class', 'midpost');
    midpost.setAttribute('id', commentInfo.comment_id);
    midpost.appendChild(createMidAvatar(commentInfo.username));
    midpost.innerHTML += commentInfo.username + ": " + commentInfo.content;
    return midpost;
}

function createMidAvatar(username) {
    let image = document.createElement('img');
    image.setAttribute('class', 'avatar');
    image.setAttribute('src', 'img/avatars/' + username + '.jpg');
    return image;
}

function expand(id) {
    let element = document.getElementById(id + '-btn');
    let toExpand = document.getElementById(id + '-mid');
    if (element.getAttribute('expanded') == '0') {
        element.setAttribute('expanded', '1');
        element.innerText = '\u25b2 收起';
        toExpand.style.maxHeight = 'min-content';
    } else {
        let span = document.getElementById('posts');
        let lastHeight = toExpand.clientHeight;
        element.setAttribute('expanded', '0');
        element.innerText = '\u25bc 展开';
        toExpand.style.maxHeight = '180px';
        let currHeight = toExpand.clientHeight;
        span.scrollTop += currHeight - lastHeight;
    }
}

function updateMidFloor(id, operation) {
    let toUpdate = document.getElementById(id + '-mid');
    let currpage = parseInt(toUpdate.getAttribute('page'));
    let maxpage = parseInt(toUpdate.getAttribute('maxpage'));

    switch (operation) {
        case '+':
            if (currpage < maxpage) {
                updateMidPosts(toUpdate, currpage + 1);
            }
            break;
        case '-':
            if (currpage > 1) {
                updateMidPosts(toUpdate, currpage - 1);
            }
            break;
        case '<':
            updateMidPosts(toUpdate, 1);
            break;
        case '>':
            updateMidPosts(toUpdate, maxpage);
            break;
    }
}

function updateMidPosts(midfloor, page) {

    let span = document.getElementById('posts');
    let lastHeight = midfloor.clientHeight;

    midfloor.innerHTML = '';
    midfloor.setAttribute('page', page);

    let postData = index[midfloor.getAttribute('index')];
    let midPageControl = document.createElement('div');
    midPageControl.setAttribute('class', 'midpagecontrol');
    for (let i = 0; i < postData.comments.comment_info[page - 1].length; i++) {
        let element = postData.comments.comment_info[page - 1][i];
        midfloor.appendChild(createMidPost(element));
    }
    let maxpage = postData.comments.comment_info.length;
    let postId = postData.content.post_id;

    if (maxpage > 1) {
        if (page > 1) {
            midPageControl.appendChild(createMidFloorPrevPage(postId));
        }
        if (page < maxpage) {
            midPageControl.appendChild(createMidFloorNextPage(postId));
        }
        if (maxpage > 2) {
            if (page > 1) {
                midPageControl.appendChild(createMidFloorFirstPage(postId));
            }
            if (page < maxpage) {
                midPageControl.appendChild(createMidFloorLastPage(postId));
            }
            midPageControl.appendChild(createMidFloorJumpPage(postId, page, maxpage));
            midPageControl.appendChild(createMidFloorJumpPageBtn(postId));
        }
        let pages = document.createTextNode('第 ' + page + ' 页，共 ' + maxpage + ' 页');
        midPageControl.appendChild(pages);
    }
    midfloor.appendChild(midPageControl);
    span.scrollTop -= lastHeight;
}

function midjump(id) {
    let toUpdate = document.getElementById(id + '-mid');
    let maxpage = parseInt(toUpdate.getAttribute('maxpage'));

    let toJump = parseInt(document.getElementById(id + '-jmp').value);

    if (toJump > maxpage) toJump = maxpage;
    else if (toJump < 0) toJump = 0;
    updateMidPosts(toUpdate, toJump);
}

function createMidFloorJumpPage(postId, currPage, maxPage) {
    let field = document.createElement('input');
    field.setAttribute('type', 'number');
    field.setAttribute('max', maxPage);
    field.setAttribute('class', 'input');
    field.setAttribute('size', 1);
    field.setAttribute('value', currPage);
    field.setAttribute('id', postId + '-jmp');
    return field;
}

function createMidFloorJumpPageBtn(postId) {
    let field = document.createElement('input');
    field.setAttribute('type', 'submit');
    field.setAttribute('class', 'btn');
    field.setAttribute('onclick', 'midjump("' + postId + '");');
    field.setAttribute('value', '跳页');
    return field;
}

function createMidFloorNextPage(postId) {
    let a = document.createElement('a');
    a.setAttribute('onclick', 'updateMidFloor("' + postId + '","+");');
    a.innerText = '下一页';
    return a;
}

function createMidFloorPrevPage(postId) {
    let a = document.createElement('a');
    a.setAttribute('onclick', 'updateMidFloor("' + postId + '","-");');
    a.innerText = '上一页';
    return a;
}

function createMidFloorFirstPage(postId) {
    let a = document.createElement('a');
    a.setAttribute('onclick', 'updateMidFloor("' + postId + '","<");');
    a.innerText = '首页';
    return a;
}

function createMidFloorLastPage(postId) {
    let a = document.createElement('a');
    a.setAttribute('onclick', 'updateMidFloor("' + postId + '",">");');
    a.innerText = '尾页';
    return a;
}