RecentComment = function() {
    this.param = rcGlobal;
    this.config = {
        commentTempId: 'rc-comment-temp',
        pingTempId: 'rc-ping-temp',
        itemIdPrefix: 'rc-comment-',
        commentClass: 'rc-comment',
        infoClass: 'rc-info',
        k3lz: 'k3lz',
        excerptClass: 'rc-excerpt',
        ellipsisClass: 'rc-ellipsis',
        contentClass: 'rc-content',
        labelClass: 'rc-label',
        toggleClass: 'rc-toggle',
        collapseClass: 'rc-collapse',
        expandClass: 'rc-expand',
        naviClass: 'rc-navi',
        newestClass: 'rc-newest',
        newerClass: 'rc-newer',
        olderClass: 'rc-older',
        loadingClass: 'rc-loading'
    };
    this.context = {
        commentTemp: null,
        pingTemp: null,
        list: null
    }
};
RecentComment.prototype = {
    init: function(config) {
        this.config = config || this.config;
        var commentTemp = jQuery('#' + this.config.commentTempId);
        var pingTemp = jQuery('#' + this.config.pingTempId);
        if (commentTemp.length <= 0 || pingTemp.length <= 0) {
            return false
        }
        this.context.commentTemp = commentTemp.clone(true);
        this.context.pingTemp = pingTemp.clone(true);
        this.context.list = commentTemp.parent();
        this.page(1)
    },
    page: function(page) {
        var _self = this;
        var url = _self.param.serverUrl;
        url += '?action=rc-ajax';
        url += '&page=' + page;
        jQuery.ajax({
            type: 'GET',
            url: url,
            cache: false,
            dataType: 'html',
            contentType: 'charset=UTF-8',
            beforeSend: function() {
                _self._changeCursor('wait');
                _self._loading()
            },
            success: function(data) {
                var json = eval('(' + data + ')');
                _self._buildList(json);
                _self._changeCursor('auto')
            }
        })
    },
    _buildList: function(json) {
        var _self = this;
        if (!json.items) {
            _self.context.list.html('<li>' + _self.param.noCommentsText + '</li>');
            return false
        }
        var listCode = _self._createCommentCode(json.items);
        var naviCode = _self._createNaviCode(json.navi);
        if (naviCode.length > 0) {
            listCode += naviCode
        }
        _self.context.list.fadeOut(function() {
            jQuery(this).html(listCode).fadeIn(function() {
                if (_self.param.showContent) {
                    _self.context.list.find('li').each(function() {
                        _self._bindCommentAction({
                            item: jQuery(this)
                        })
                    })
                }
                if (_self.param.external) {
                    _self._initLinks()
                }
                if (naviCode.length > 0) {
                    _self._bindNaviAction({
                        item: jQuery(this),
                        pageNumber: json.navi.page
                    })
                }
            })
        });
        return true
    },
    _createCommentCode: function(items) {
        var list = jQuery('<ul>');
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var node = null;
            if (item.type == 'pingback' || item.type == 'trackback') {
                node = this._buildPing(item)
            } else {
                node = this._buildComment(item)
            }
            if (node) {
                list.append(node)
            }
        }
        return list.html()
    },
    _createNaviCode: function(navi) {
        if (!navi) {
            return ''
        }
        var pageNumber = parseInt(navi.page, 10);
        if (pageNumber <= 1 && !navi.more) {
            return ''
        }
        var _self = this;
        var code = '<span class="' + _self.config.naviClass + ' rc-clearfix">';
        if (pageNumber >= 2) {
            if (pageNumber > 2) {
                code += '<a "rel=nofollow" class="' + _self.config.newestClass + '">' + _self.param.newestText + '</a>'
            }
            code += '<a "rel=nofollow" class="' + _self.config.newerClass + '">' + _self.param.newerText + '</a>'
        }
        if (navi.more) {
            code += '<a "rel=nofollow" class="' + _self.config.olderClass + '">' + _self.param.olderText + '</a>'
        }
        code += '</span>';
        return code
    },
    _bindCommentAction: function(args) {
        var item = args.item;
        var _self = this;
        var itemExcerpt = item.find('div.' + _self.config.excerptClass + ':eq(0)');
        var itemEllipsis = itemExcerpt.find('span.' + _self.config.ellipsisClass + ':eq(0)');
        if (itemEllipsis.length == 1) {
            itemExcerpt.parent().hover(function(ev) {
                _self._enterCommnet(ev, {
                    _self: _self,
                    item: item
                })
            },
            function(ev) {
                _self._leaveCommnet(ev, {
                    _self: _self,
                    item: item
                })
            })
        }
    },
    _bindNaviAction: function(args) {
        var item = args.item;
        var pageNumber = args.pageNumber;
        var _self = this;
        var newestLink = item.find('a.' + _self.config.newestClass + ':eq(0)');
        if (newestLink) {
            newestLink.click(function(ev) {
                _self.page(1)
            })
        }
        var newerLink = item.find('a.' + _self.config.newerClass + ':eq(0)');
        if (newerLink) {
            newerLink.click(function(ev) {
                _self.page(parseInt(pageNumber, 10) - 1)
            })
        }
        var olderLink = item.find('a.' + _self.config.olderClass + ':eq(0)');
        if (olderLink) {
            olderLink.click(function(ev) {
                _self.page(parseInt(pageNumber, 10) + 1)
            })
        }
    },
    _buildComment: function(item) {
        var itemNode = this.context.commentTemp.clone(true);
        var itemInfo = itemNode.find('div.' + this.config.infoClass + ':eq(0)');
        var itemInfo1 = itemNode.find('dd.' + this.config.k3lz + ':eq(0)');
        var itemExcerpt = itemNode.find('div.' + this.config.excerptClass + ':eq(0)');
        itemNode.attr('id', this.config.itemIdPrefix + item.id);
        if (item.reviewerName.length <= 0) {
            item.reviewerName = this.param.anonymous
        }
        if (item.title) {
            var reviewerLink = '';
            if (item.reviewerUrl && item.reviewerUrl.length > 0) {
                var relTag = 'nofollow';
                if (this.param.external && item.reviewerUrl.indexOf(this.param.serverUrl) !== 0) {
                    relTag += ' external'
                }
                reviewerLink = '<a class="rc-reviewer" rel="' + relTag + '" href="' + item.reviewerUrl + '">' + item.reviewerName + '</a>'
            } else {
                reviewerLink = '' + item.reviewerName + ''
            }
            var postLink = '<a class="rc-post" rel="nofollow" href="' + item.postUrl + '#comment-' + item.id + '">' + item.postTitle + '</a>';
            itemInfo.html(this.param.infoTemp.replace(/%REVIEWER%/g, reviewerLink).replace(/%POST%/g, postLink))
        } else {
            if (item.userid) {
                if (item.fbnum > 0) {
                    var reviewerLink = '<a style="color:#438904" href="https://www.freebuf.com/author/' + item.reviewerName + '" title="' + item.postTitle + '" target="_blank">' + item.authorName + ' <img src="https://image.3001.net/images/index/f'+item.fbnum+'.png"> ' + item.level + '</a> '
                } else {
                    var reviewerLink = '<a style="color:#438904" href="https://www.freebuf.com/author/' + item.reviewerName + '" title="' + item.postTitle + '" target="_blank">' + item.authorName + item.level + '</a>'
                }
            } else {
                var reviewerLink = item.reviewerName
            }
            itemInfo.html(reviewerLink)
        }
        if (item.timestamp && item.timestamp.length > 0) {
            var timestamp = jQuery('<span class="rc-timestamp">' + item.timestamp + '</span>');
            itemInfo.append(timestamp)
        }
        var excerpt = '<a class="rc-post" rel="nofollow" title="' + item.postTitle + '" href="' + item.postUrl + '#comment-' + item.id + '" target="_blank">' + item.excerpt + '</a>';
        itemExcerpt.html(excerpt);
        if (item.ellipsis) {
            var ellipsis = jQuery('<span>');
            ellipsis.attr('class', this.config.ellipsisClass);
            itemExcerpt.append(ellipsis)
        }
        if (item.avatarImage) {
            var avatar = jQuery('<img>');
            avatar.attr('class', 'rc-avatar rc-' + this.param.avatarPosition);
            avatar.attr('width', this.param.avatarSize);
            avatar.attr('height', this.param.avatarSize);
            avatar.attr('alt', '');
            avatar.attr('src', item.avatarImage);
            avatar.insertBefore(itemInfo1);
            avatar.wrap('<dt></dt>')
        }
        return itemNode
    },
    _buildPing: function(item) {
        var itemNode = this.context.pingTemp.clone(true);
        var itemLabel = itemNode.find('span.' + this.config.labelClass + ':eq(0)');
        itemNode.removeAttr('id');
        var relTag = 'nofollow';
        if (this.param.external && item.reviewerUrl.indexOf(this.param.serverUrl) !== 0) {
            relTag += ' external'
        }
        var pingLink = jQuery('<a>');
        pingLink.attr('rel', relTag);
        pingLink.attr('href', item.reviewerUrl);
        pingLink.attr('title', item.postTitle);
        pingLink.html(item.reviewerName);
        itemNode.append(pingLink);
        itemLabel.html(item.type + ': ');
        return itemNode
    },
    _initLinks: function() {
        var list = this.context.list;
        list.find('a[rel*="external"]').click(function() {
            window.open(this.href);
            return false
        })
    },
    _bindPopup: function(ev, args) {
        window.open(args.link.href);
        if (ev.preventDefault) {
            ev.preventDefault()
        } else {
            ev.returnValue = false
        }
    },
    _enterCommnet: function(ev, args) {
        var _self = args._self;
        var item = args.item;
        var itemExcerpt = item.find('div.' + _self.config.excerptClass + ':eq(0)');
        var itemToggle = item.find('a.' + _self.config.toggleClass + ':eq(0)');
        if (itemToggle.length == 1) {
            itemToggle.fadeIn()
        } else {
            var itemToggle = jQuery('<a>');
            itemToggle.attr('rel', 'nofollow');
            itemToggle.attr('class', _self.config.toggleClass + ' ' + _self.config.collapseClass);
            itemToggle.click(function(ev) {
                _self._toggleComment(ev, {
                    _self: _self,
                    item: item,
                    source: itemToggle
                })
            });
            itemToggle.insertBefore(itemExcerpt)
        }
    },
    _leaveCommnet: function(ev, args) {
        var _self = args._self;
        var item = args.item;
        var itemToggle = item.find('a.' + _self.config.toggleClass + ':eq(0)');
        if (itemToggle.length == 1) {
            itemToggle.fadeOut()
        }
    },
    _toggleComment: function(ev, args) {
        var _self = args._self;
        var item = args.item;
        var source = args.source;
        var itemContent = item.find('div.' + _self.config.contentClass + ':eq(0)');
        var itemExcerpt = item.find('div.' + _self.config.excerptClass + ':eq(0)');
        if (itemContent.length == 1 && source.is('.' + _self.config.collapseClass)) {
            itemExcerpt.hide();
            itemContent.show();
            source.attr('class', _self.config.toggleClass + ' ' + _self.config.expandClass)
        } else if (itemContent.length == 1) {
            itemContent.hide();
            itemExcerpt.show();
            source.attr('class', _self.config.toggleClass + ' ' + _self.config.collapseClass)
        } else {
            itemContent = jQuery('<div>');
            itemContent.attr('class', _self.config.contentClass);
            itemContent.hide();
            itemContent.insertAfter(itemExcerpt);
            var url = _self.param.serverUrl;
            url += '?action=rc-content';
            url += '&id=' + item.attr('id').replace(_self.config.itemIdPrefix, '');
            jQuery.ajax({
                type: 'GET',
                url: url,
                cache: false,
                dataType: 'html',
                contentType: 'charset=UTF-8',
                success: function(data) {
                    if (data.length <= 0) {
                        data = itemExcerpt.html()
                    }
                    itemContent.html(data);
                    itemExcerpt.hide();
                    itemContent.show();
                    source.attr('class', _self.config.toggleClass + ' ' + _self.config.expandClass)
                }
            })
        }
    },
    _loading: function() {
        var navi = this.context.list.find('li.' + this.config.naviClass + ':eq(0)');
        if (navi) {
            navi.html('<span class="' + this.config.loadingClass + '">' + this.param.loadingText + '...<span>')
        }
    },
    _changeCursor: function(status) {
        this.context.list.css('cursor', status)
    }
};
jQuery(document).ready(function() { (new RecentComment()).init()
});