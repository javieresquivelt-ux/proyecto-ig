(function () {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateButton(btn, active, count) {
        if (!btn) return;
        var activeClass = btn.dataset.active;
        var inactiveClass = btn.dataset.inactive;
        btn.classList.remove(activeClass, inactiveClass);
        btn.classList.add(active ? activeClass : inactiveClass);
        var countEl = btn.querySelector('.count');
        if (countEl) {
            countEl.textContent = count ? ' ' + count : '';
        }
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.js-like, .js-dislike');
        if (!btn) return;
        e.preventDefault();
        var box = btn.closest('.js-likebox');
        fetch(btn.dataset.url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        }).then(function (r) {
            return r.json();
        }).then(function (data) {
            updateButton(box.querySelector('.js-like'), data.liked, data.likes_count);
            updateButton(box.querySelector('.js-dislike'), data.disliked, data.dislikes_count);
        }).catch(function () {});
    });

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.js-load-more');
        if (!btn) return;
        e.preventDefault();
        var target = document.getElementById(btn.dataset.target);
        var url = btn.dataset.url + '?page=' + btn.dataset.page;
        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        }).then(function (r) {
            return r.json();
        }).then(function (data) {
            if (target && data.html) {
                target.insertAdjacentHTML('beforeend', data.html);
            }
            if (data.has_next) {
                btn.dataset.page = data.next_page;
            } else {
                btn.remove();
            }
        }).catch(function () {});
    });

    document.addEventListener('click', function (e) {
        var burger = e.target.closest('.hamburger');
        if (burger) {
            var header = burger.closest('.header');
            header.classList.toggle('nav-open');
            burger.setAttribute('aria-expanded', header.classList.contains('nav-open'));
            return;
        }
        var link = e.target.closest('.header__menu a');
        if (link) {
            var h = link.closest('.header');
            h.classList.remove('nav-open');
            var b = h.querySelector('.hamburger');
            if (b) b.setAttribute('aria-expanded', 'false');
        }
    });
})();
