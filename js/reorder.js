function reorderWelcome() {
    const vid = document.getElementById("welcome-vid");

    if (vid) {
        const vidParent = vid.parentElement;
        const links = vidParent.querySelector(".links");

        if (links) {
            vidParent.insertBefore(vid, links);
        }
    }
}
