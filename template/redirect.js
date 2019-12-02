function parseArguments() {
    try {
        let href = window.location.href.split("?");
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

function copy(id) {
    var copyText = document.getElementById(id);
    copyText.select();
    document.execCommand("copy");
}

let url = decodeURIComponent(parseArguments().url);
if (url != "undefined") {
    document.getElementById("url").value = url;
    document.getElementById("visit").href = url;
}