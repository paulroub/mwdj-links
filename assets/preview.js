var LinkPreview = createClass({
    render: function () {
        const entry = this.props.entry;
        const imageStr = entry.getIn(["data", "image"]);
        const image = this.props.getAsset(imageStr);
        const title = entry.getIn(["data", "title"]);
        const link = entry.getIn(["data", "link"]);

        return h(
            "ul",
            { class: "links" },
            h(
                "li",
                { class: "link" },
                h(
                    "a",
                    { href: link },
                    h("img", {
                        src: image.toString(),
                        class: "link-logo",
                        alt: title,
                    })
                ),
                h("a", { class: "link-desc", href: link }, title)
            )
        );
    },
});

CMS.registerPreviewTemplate("links", LinkPreview);
CMS.registerPreviewStyle("/assets/styles.css");
